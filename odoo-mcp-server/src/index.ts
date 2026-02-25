#!/usr/bin/env node

/**
 * Odoo MCP Server
 * Enables Claude Code to interact with Odoo ERP for accounting automation
 *
 * Gold Tier Feature #4
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { OdooClient } from './odoo-client.js';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Validate required environment variables
const ODOO_URL = process.env.ODOO_URL;
const ODOO_DB = process.env.ODOO_DB;
const ODOO_USERNAME = process.env.ODOO_USERNAME;
const ODOO_PASSWORD = process.env.ODOO_PASSWORD;
const DRY_RUN = process.env.DRY_RUN === 'true';

if (!ODOO_URL || !ODOO_DB || !ODOO_USERNAME || !ODOO_PASSWORD) {
  console.error('Error: Missing required Odoo configuration');
  console.error('Required: ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD');
  process.exit(1);
}

// Initialize Odoo client
const odooClient = new OdooClient({
  url: ODOO_URL,
  db: ODOO_DB,
  username: ODOO_USERNAME,
  password: ODOO_PASSWORD,
  dryRun: DRY_RUN
});

// Define tool schemas
const CreateInvoiceSchema = z.object({
  customer_id: z.number().describe('Customer/Partner ID'),
  items: z.array(z.object({
    name: z.string().describe('Item description'),
    quantity: z.number().describe('Quantity'),
    price: z.number().describe('Unit price'),
    product_id: z.number().optional().describe('Product ID (optional)')
  })).describe('Invoice line items'),
  invoice_date: z.string().optional().describe('Invoice date (YYYY-MM-DD, defaults to today)')
});

const RecordExpenseSchema = z.object({
  name: z.string().describe('Expense description'),
  amount: z.number().describe('Expense amount'),
  quantity: z.number().default(1).describe('Quantity (default: 1)'),
  product_id: z.number().optional().describe('Product/Category ID'),
  date: z.string().optional().describe('Expense date (YYYY-MM-DD, defaults to today)')
});

const GetFinancialSummarySchema = z.object({
  start_date: z.string().optional().describe('Start date (YYYY-MM-DD)'),
  end_date: z.string().optional().describe('End date (YYYY-MM-DD)')
});

const SearchPartnersSchema = z.object({
  search_term: z.string().describe('Name or email to search'),
  limit: z.number().default(10).describe('Maximum results')
});

const CreatePartnerSchema = z.object({
  name: z.string().describe('Partner/Customer name'),
  email: z.string().optional().describe('Email address'),
  phone: z.string().optional().describe('Phone number'),
  is_company: z.boolean().default(false).describe('Is this a company?')
});

// Define available tools
const tools: Tool[] = [
  {
    name: 'create_invoice',
    description: 'Create a new customer invoice in Odoo. Returns invoice ID.',
    inputSchema: {
      type: 'object',
      properties: {
        customer_id: {
          type: 'number',
          description: 'Customer/Partner ID in Odoo'
        },
        items: {
          type: 'array',
          description: 'Invoice line items',
          items: {
            type: 'object',
            properties: {
              name: { type: 'string', description: 'Item description' },
              quantity: { type: 'number', description: 'Quantity' },
              price: { type: 'number', description: 'Unit price' },
              product_id: { type: 'number', description: 'Product ID (optional)' }
            },
            required: ['name', 'quantity', 'price']
          }
        },
        invoice_date: {
          type: 'string',
          description: 'Invoice date (YYYY-MM-DD, optional)'
        }
      },
      required: ['customer_id', 'items']
    }
  },
  {
    name: 'get_invoices',
    description: 'Retrieve recent invoices from Odoo. Filter by state (draft, posted, paid) if needed.',
    inputSchema: {
      type: 'object',
      properties: {
        limit: {
          type: 'number',
          description: 'Maximum number of invoices to retrieve',
          default: 10
        },
        state: {
          type: 'string',
          description: 'Filter by state: draft, posted, or paid',
          enum: ['draft', 'posted', 'paid']
        }
      }
    }
  },
  {
    name: 'record_expense',
    description: 'Record a new expense in Odoo. Returns expense ID.',
    inputSchema: {
      type: 'object',
      properties: {
        name: {
          type: 'string',
          description: 'Expense description'
        },
        amount: {
          type: 'number',
          description: 'Expense amount'
        },
        quantity: {
          type: 'number',
          description: 'Quantity (default: 1)',
          default: 1
        },
        product_id: {
          type: 'number',
          description: 'Product/Category ID (optional)'
        },
        date: {
          type: 'string',
          description: 'Expense date (YYYY-MM-DD, optional)'
        }
      },
      required: ['name', 'amount']
    }
  },
  {
    name: 'get_expenses',
    description: 'Retrieve recent expenses from Odoo.',
    inputSchema: {
      type: 'object',
      properties: {
        limit: {
          type: 'number',
          description: 'Maximum number of expenses to retrieve',
          default: 10
        }
      }
    }
  },
  {
    name: 'get_financial_summary',
    description: 'Get financial summary including revenue, expenses, and profit for a date range.',
    inputSchema: {
      type: 'object',
      properties: {
        start_date: {
          type: 'string',
          description: 'Start date (YYYY-MM-DD, optional)'
        },
        end_date: {
          type: 'string',
          description: 'End date (YYYY-MM-DD, optional)'
        }
      }
    }
  },
  {
    name: 'search_partners',
    description: 'Search for customers/partners by name or email.',
    inputSchema: {
      type: 'object',
      properties: {
        search_term: {
          type: 'string',
          description: 'Name or email to search'
        },
        limit: {
          type: 'number',
          description: 'Maximum results',
          default: 10
        }
      },
      required: ['search_term']
    }
  },
  {
    name: 'create_partner',
    description: 'Create a new customer/partner in Odoo. Returns partner ID.',
    inputSchema: {
      type: 'object',
      properties: {
        name: {
          type: 'string',
          description: 'Partner/Customer name'
        },
        email: {
          type: 'string',
          description: 'Email address (optional)'
        },
        phone: {
          type: 'string',
          description: 'Phone number (optional)'
        },
        is_company: {
          type: 'boolean',
          description: 'Is this a company?',
          default: false
        }
      },
      required: ['name']
    }
  },
  {
    name: 'test_odoo_connection',
    description: 'Test connection to Odoo server. Useful for verifying configuration.',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  }
];

// Create MCP server instance
const server = new Server(
  {
    name: 'odoo-mcp-server',
    version: '1.0.0'
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools
  };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    // Create Invoice
    if (name === 'create_invoice') {
      const validated = CreateInvoiceSchema.parse(args);

      const invoiceId = await odooClient.createInvoice({
        partner_id: validated.customer_id,
        invoice_date: validated.invoice_date,
        invoice_line_ids: validated.items.map(item => ({
          name: item.name,
          quantity: item.quantity,
          price_unit: item.price,
          product_id: item.product_id
        }))
      });

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            success: true,
            invoice_id: invoiceId,
            message: DRY_RUN ? 'DRY RUN: Invoice would be created' : 'Invoice created successfully',
            customer_id: validated.customer_id,
            total_items: validated.items.length
          }, null, 2)
        }]
      };
    }

    // Get Invoices
    if (name === 'get_invoices') {
      const limit = (args as any).limit || 10;
      const state = (args as any).state;

      const invoices = await odooClient.getInvoices(limit, state);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            success: true,
            count: invoices.length,
            invoices: invoices.map(inv => ({
              id: inv.id,
              name: inv.name,
              customer: inv.partner_id?.[1] || 'Unknown',
              date: inv.invoice_date,
              amount: inv.amount_total,
              state: inv.state,
              payment_state: inv.payment_state
            }))
          }, null, 2)
        }]
      };
    }

    // Record Expense
    if (name === 'record_expense') {
      const validated = RecordExpenseSchema.parse(args);

      const expenseId = await odooClient.recordExpense({
        name: validated.name,
        price_unit: validated.amount,
        quantity: validated.quantity,
        product_id: validated.product_id,
        date: validated.date
      });

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            success: true,
            expense_id: expenseId,
            message: DRY_RUN ? 'DRY RUN: Expense would be recorded' : 'Expense recorded successfully',
            amount: validated.amount
          }, null, 2)
        }]
      };
    }

    // Get Expenses
    if (name === 'get_expenses') {
      const limit = (args as any).limit || 10;

      const expenses = await odooClient.getExpenses(limit);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            success: true,
            count: expenses.length,
            expenses: expenses.map(exp => ({
              id: exp.id,
              name: exp.name,
              employee: exp.employee_id?.[1] || 'Unknown',
              amount: exp.unit_amount,
              date: exp.date,
              state: exp.state
            }))
          }, null, 2)
        }]
      };
    }

    // Get Financial Summary
    if (name === 'get_financial_summary') {
      const validated = GetFinancialSummarySchema.parse(args);

      const summary = await odooClient.getFinancialSummary(
        validated.start_date,
        validated.end_date
      );

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            success: true,
            summary: {
              revenue: {
                total: summary.revenue.total,
                paid: summary.revenue.paid,
                unpaid: summary.revenue.unpaid,
                invoices: summary.revenue.invoice_count
              },
              expenses: {
                total: summary.expenses.total,
                count: summary.expenses.expense_count
              },
              profit: summary.profit,
              period: summary.period
            },
            message: DRY_RUN ? 'DRY RUN: Financial data' : 'Financial summary retrieved'
          }, null, 2)
        }]
      };
    }

    // Search Partners
    if (name === 'search_partners') {
      const validated = SearchPartnersSchema.parse(args);

      const partners = await odooClient.searchPartners(
        validated.search_term,
        validated.limit
      );

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            success: true,
            count: partners.length,
            partners: partners.map(p => ({
              id: p.id,
              name: p.name,
              email: p.email,
              phone: p.phone,
              is_company: p.is_company
            }))
          }, null, 2)
        }]
      };
    }

    // Create Partner
    if (name === 'create_partner') {
      const validated = CreatePartnerSchema.parse(args);

      const partnerId = await odooClient.createPartner(validated);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            success: true,
            partner_id: partnerId,
            message: DRY_RUN ? 'DRY RUN: Partner would be created' : 'Partner created successfully',
            name: validated.name
          }, null, 2)
        }]
      };
    }

    // Test Connection
    if (name === 'test_odoo_connection') {
      const isConnected = await odooClient.testConnection();

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            success: isConnected,
            connected: isConnected,
            message: isConnected
              ? `Connected to Odoo at ${ODOO_URL}`
              : 'Connection failed - check credentials',
            mode: DRY_RUN ? 'DRY RUN' : 'LIVE',
            server: ODOO_URL,
            database: ODOO_DB
          }, null, 2)
        }]
      };
    }

    throw new Error(`Unknown tool: ${name}`);

  } catch (error: any) {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          success: false,
          error: error.message
        }, null, 2)
      }],
      isError: true
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Odoo MCP Server running on stdio');
  console.error(`Mode: ${DRY_RUN ? 'DRY RUN (no actual Odoo operations)' : 'LIVE'}`);
  console.error(`Server: ${ODOO_URL}`);
  console.error(`Database: ${ODOO_DB}`);
  console.error('Available tools: create_invoice, get_invoices, record_expense, get_expenses,');
  console.error('                 get_financial_summary, search_partners, create_partner, test_odoo_connection');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
