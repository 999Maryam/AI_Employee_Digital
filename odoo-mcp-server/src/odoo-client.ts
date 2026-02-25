/**
 * Odoo API Client
 * Handles authentication and API calls to Odoo ERP system
 */

import xmlrpc from 'xmlrpc';
import { URL } from 'url';

export interface OdooConfig {
  url: string;
  db: string;
  username: string;
  password: string;
  dryRun?: boolean;
}

export interface Invoice {
  id?: number;
  partner_id: number;
  invoice_date?: string;
  invoice_line_ids: InvoiceLine[];
  amount_total?: number;
  state?: string;
}

export interface InvoiceLine {
  product_id?: number;
  name: string;
  quantity: number;
  price_unit: number;
}

export interface Expense {
  id?: number;
  name: string;
  product_id?: number;
  price_unit: number;
  quantity: number;
  employee_id?: number;
  date?: string;
}

export interface Partner {
  id?: number;
  name: string;
  email?: string;
  phone?: string;
  is_company?: boolean;
}

export class OdooClient {
  private commonClient: any;
  private objectClient: any;
  private uid: number | null = null;
  private config: OdooConfig;

  constructor(config: OdooConfig) {
    this.config = config;

    // Parse URL to get host and protocol
    const parsedUrl = new URL(config.url);
    const isSecure = parsedUrl.protocol === 'https:';
    const host = parsedUrl.hostname;
    const port = parsedUrl.port ? parseInt(parsedUrl.port) : (isSecure ? 443 : 80);

    // Create XML-RPC clients
    const clientOptions = {
      host,
      port,
      path: '/xmlrpc/2/common'
    };

    const objectOptions = {
      host,
      port,
      path: '/xmlrpc/2/object'
    };

    this.commonClient = isSecure
      ? xmlrpc.createSecureClient(clientOptions)
      : xmlrpc.createClient(clientOptions);

    this.objectClient = isSecure
      ? xmlrpc.createSecureClient(objectOptions)
      : xmlrpc.createClient(objectOptions);
  }

  /**
   * Authenticate with Odoo and get user ID
   */
  async authenticate(): Promise<number> {
    if (this.uid) {
      return this.uid;
    }

    // For demo/dry-run mode
    if (this.config.dryRun) {
      console.log(`[DRY RUN] Would authenticate as ${this.config.username}`);
      this.uid = 1; // Mock user ID
      return this.uid;
    }

    try {
      const uid = await new Promise<number>((resolve, reject) => {
        this.commonClient.methodCall('authenticate', [
          this.config.db,
          this.config.username,
          this.config.password,
          {}
        ], (error: any, value: any) => {
          if (error) reject(error);
          else resolve(value);
        });
      });

      if (!uid || typeof uid !== 'number') {
        throw new Error('Authentication failed - invalid credentials');
      }

      this.uid = uid;
      return this.uid;
    } catch (error: any) {
      throw new Error(`Odoo authentication failed: ${error.message}`);
    }
  }

  /**
   * Execute Odoo model method
   */
  private async execute(model: string, method: string, args: any[], kwargs: any = {}): Promise<any> {
    await this.authenticate();

    // For demo/dry-run mode
    if (this.config.dryRun) {
      console.log(`[DRY RUN] Would call ${model}.${method} with args:`, JSON.stringify(args), 'kwargs:', JSON.stringify(kwargs));
      return this.getMockData(model);
    }

    return new Promise((resolve, reject) => {
      this.objectClient.methodCall('execute_kw', [
        this.config.db,
        this.uid,
        this.config.password,
        model,
        method,
        args,
        kwargs
      ], (error: any, value: any) => {
        if (error) reject(error);
        else resolve(value);
      });
    });
  }

  /**
   * Get mock data for dry-run mode
   */
  private getMockData(model: string): any {
    const mockData: Record<string, any> = {
      'res.partner': [
        { id: 1, name: 'Test Customer', email: 'customer@example.com' }
      ],
      'account.move': [
        { id: 1, name: 'INV/2026/0001', amount_total: 1000, state: 'draft' }
      ],
      'hr.expense': [
        { id: 1, name: 'Office Supplies', unit_amount: 50, state: 'draft' }
      ],
      'product.product': [
        { id: 1, name: 'Consulting Service', list_price: 100 }
      ]
    };

    return mockData[model] || [{ id: 1, name: 'Mock Data' }];
  }

  /**
   * Search and read records
   */
  async searchRead(model: string, domain: any[] = [], fields: string[] = [], limit: number = 10): Promise<any[]> {
    return this.execute(model, 'search_read', [domain], {
      fields,
      limit
    });
  }

  /**
   * Create a new record
   */
  async create(model: string, values: any): Promise<number> {
    return this.execute(model, 'create', [values]);
  }

  /**
   * Update existing record
   */
  async write(model: string, ids: number[], values: any): Promise<boolean> {
    return this.execute(model, 'write', [ids, values]);
  }

  /**
   * Delete records
   */
  async unlink(model: string, ids: number[]): Promise<boolean> {
    return this.execute(model, 'unlink', [ids]);
  }

  // === Business Methods ===

  /**
   * Create invoice
   */
  async createInvoice(invoice: Invoice): Promise<number> {
    const invoiceData = {
      partner_id: invoice.partner_id,
      move_type: 'out_invoice',
      invoice_date: invoice.invoice_date || new Date().toISOString().split('T')[0],
      invoice_line_ids: invoice.invoice_line_ids.map(line => [0, 0, {
        name: line.name,
        quantity: line.quantity,
        price_unit: line.price_unit,
        product_id: line.product_id
      }])
    };

    return this.create('account.move', invoiceData);
  }

  /**
   * Get invoices
   */
  async getInvoices(limit: number = 10, state?: string): Promise<any[]> {
    const domain: any[] = [['move_type', '=', 'out_invoice']];
    if (state) {
      domain.push(['state', '=', state]);
    }

    return this.searchRead(
      'account.move',
      domain,
      ['name', 'partner_id', 'invoice_date', 'amount_total', 'state', 'payment_state'],
      limit
    );
  }

  /**
   * Record expense
   */
  async recordExpense(expense: Expense): Promise<number> {
    await this.authenticate();

    // If employee_id is not provided, get the current user's employee
    let employeeId = expense.employee_id;
    if (!employeeId) {
      const employees = await this.searchRead(
        'hr.employee',
        [['user_id', '=', this.uid]],
        ['id'],
        1
      );

      if (employees.length === 0) {
        throw new Error('No employee record found for current user. Please create an employee record first.');
      }

      employeeId = employees[0].id;
    }

    const expenseData = {
      name: expense.name,
      price_unit: expense.price_unit,
      quantity: expense.quantity || 1,
      product_id: expense.product_id,
      employee_id: employeeId,
      date: expense.date || new Date().toISOString().split('T')[0]
    };

    return this.create('hr.expense', expenseData);
  }

  /**
   * Get expenses
   */
  async getExpenses(limit: number = 10): Promise<any[]> {
    return this.searchRead(
      'hr.expense',
      [],
      ['name', 'employee_id', 'price_unit', 'quantity', 'total_amount', 'date', 'state'],
      limit
    );
  }

  /**
   * Get financial summary
   */
  async getFinancialSummary(startDate?: string, endDate?: string): Promise<any> {
    const domain: any[] = [['move_type', '=', 'out_invoice']];

    if (startDate) {
      domain.push(['invoice_date', '>=', startDate]);
    }
    if (endDate) {
      domain.push(['invoice_date', '<=', endDate]);
    }

    const invoices = await this.searchRead(
      'account.move',
      domain,
      ['amount_total', 'state', 'payment_state']
    );

    let totalRevenue = 0;
    let paidRevenue = 0;
    let unpaidRevenue = 0;

    invoices.forEach(inv => {
      if (inv.state === 'posted') {
        totalRevenue += inv.amount_total || 0;
        if (inv.payment_state === 'paid') {
          paidRevenue += inv.amount_total || 0;
        } else {
          unpaidRevenue += inv.amount_total || 0;
        }
      }
    });

    // Get expenses
    const expenseDomain: any[] = [];
    if (startDate) {
      expenseDomain.push(['date', '>=', startDate]);
    }
    if (endDate) {
      expenseDomain.push(['date', '<=', endDate]);
    }

    const expenses = await this.searchRead(
      'hr.expense',
      expenseDomain,
      ['price_unit', 'quantity', 'total_amount', 'state']
    );

    let totalExpenses = 0;
    expenses.forEach(exp => {
      if (exp.state === 'approved' || exp.state === 'done') {
        totalExpenses += exp.total_amount || ((exp.price_unit || 0) * (exp.quantity || 1));
      }
    });

    return {
      revenue: {
        total: totalRevenue,
        paid: paidRevenue,
        unpaid: unpaidRevenue,
        invoice_count: invoices.length
      },
      expenses: {
        total: totalExpenses,
        expense_count: expenses.length
      },
      profit: totalRevenue - totalExpenses,
      period: {
        start: startDate,
        end: endDate
      }
    };
  }

  /**
   * Search partners/customers
   */
  async searchPartners(searchTerm: string, limit: number = 10): Promise<Partner[]> {
    const domain = [
      '|',
      ['name', 'ilike', searchTerm],
      ['email', 'ilike', searchTerm]
    ];

    return this.searchRead(
      'res.partner',
      domain,
      ['name', 'email', 'phone', 'is_company'],
      limit
    );
  }

  /**
   * Create partner/customer
   */
  async createPartner(partner: Partner): Promise<number> {
    return this.create('res.partner', partner);
  }

  /**
   * Test connection
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.authenticate();
      return true;
    } catch (error) {
      return false;
    }
  }
}
