# Personal AI Employee Hackathon 0: Building Autonomous FTEs (Full-Time Equivalent) in 2026

**Tagline:** Your life and business on autopilot. Local-first,
agent-driven, human-in-the-loop.

This document serves as a comprehensive architectural blueprint and
hackathon guide for building a **Digital FTE (Full-Time Equivalent)**
--- an AI agent that proactively manages personal and business affairs
24/7 using Claude Code and Obsidian.

------------------------------------------------------------------------

## Overview

This hackathon pushes the concept of a Personal AI Employee to the
extreme. Instead of waiting for prompts, the agent:

-   Manages Gmail, WhatsApp, banking, and files\
-   Handles social media, payments, and project tasks\
-   Operates autonomously with human-in-the-loop safeguards

Think of it as hiring a **senior digital employee** capable of
reasoning, planning, and executing.

------------------------------------------------------------------------

## Standout Idea: Monday Morning CEO Briefing

Every week the AI should autonomously:

-   Audit bank transactions\
-   Review completed tasks\
-   Identify bottlenecks\
-   Generate revenue summaries\
-   Provide proactive suggestions

This transforms the AI from a chatbot into a **business partner**.

------------------------------------------------------------------------

# Architecture & Tech Stack

## The Brain

**Claude Code** acts as the reasoning engine with the *Ralph Wiggum Stop
Hook* to ensure tasks iterate until completion.

## Memory / GUI

**Obsidian (local markdown vault)** keeps data private and structured.

## The Senses (Watchers)

Lightweight Python scripts monitor:

-   Gmail\
-   WhatsApp\
-   Filesystems\
-   Banking data

## The Hands (MCP Servers)

Model Context Protocol servers execute external actions:

-   Sending emails\
-   Posting social media\
-   Clicking browser elements\
-   Creating calendar events

------------------------------------------------------------------------

# Digital FTE: The New Unit of Value

  Feature         Human FTE           Digital FTE
  --------------- ------------------- ------------------
  Availability    40 hrs/week         168 hrs/week
  Monthly Cost    \$4,000--\$8,000+   \$500--\$2,000
  Ramp-up         3--6 months         Instant
  Consistency     85--95%             99%+
  Scaling         Linear              Exponential
  Cost per Task   \~\$3--\$6          \~\$0.25--\$0.50
  Annual Hours    \~2,000             \~8,760

**Aha Moment:** Nearly **90% cost reduction** --- often enough for
executive approval without debate.

------------------------------------------------------------------------

# Prerequisites & Setup

## Required Software

  Component        Requirement           Purpose
  ---------------- --------------------- ------------------
  Claude Code      Active subscription   Reasoning engine
  Obsidian         v1.10.6+              Knowledge base
  Python           3.13+                 Watchers
  Node.js          v24+ LTS              MCP servers
  GitHub Desktop   Latest                Version control

### Hardware

**Minimum:**\
- 8GB RAM\
- 4-core CPU\
- 20GB storage

**Recommended:**\
- 16GB RAM\
- 8-core CPU\
- SSD

------------------------------------------------------------------------

# Skill Expectations

Intermediate technical ability:

-   Comfortable with terminal/bash\
-   Understand APIs\
-   Familiar with file systems\
-   Able to prompt Claude Code

No prior ML experience required.

------------------------------------------------------------------------

# Hackathon Tiers

## 🥉 Bronze --- Foundation

-   Obsidian vault with dashboard\
-   One watcher script\
-   Claude reads/writes vault\
-   Folder structure: `/Inbox /Needs_Action /Done`

## 🥈 Silver --- Functional Assistant

Everything in Bronze plus:

-   Multiple watchers\
-   LinkedIn auto-posting\
-   Plan.md reasoning loop\
-   One MCP server\
-   Human approval workflow

## 🥇 Gold --- Autonomous Employee

Includes Silver plus:

-   Cross-domain integrations\
-   Odoo accounting via MCP\
-   Social media automation\
-   Weekly CEO briefing\
-   Audit logging\
-   Ralph Wiggum loop

## 💎 Platinum --- Always-On Production Agent

Includes Gold plus:

-   24/7 cloud deployment\
-   Work-zone specialization\
-   Synced vault (Git/Syncthing)\
-   Claim-by-move task ownership\
-   Secrets never synced\
-   HTTPS Odoo deployment

**Demo Gate:**\
Email arrives → Cloud drafts → Local approves → MCP sends → Logs → Task
moved to Done.

------------------------------------------------------------------------

# Foundational Architecture

## Perception → Reasoning → Action

### Perception

Python watchers detect events and create markdown files in
`/Needs_Action`.

### Reasoning

Claude:

1.  Reads vault\
2.  Thinks\
3.  Creates Plan.md\
4.  Requests approval

### Action

MCP servers execute tasks after approval.

------------------------------------------------------------------------

# Human-in-the-Loop Pattern

Sensitive actions generate approval files:

    /Vault/Pending_Approval/PAYMENT_Client_A.md

User moves file to:

-   `/Approved` → Execute\
-   `/Rejected` → Cancel

------------------------------------------------------------------------

# Ralph Wiggum Loop (Autonomy Engine)

Prevents lazy agents.

Flow:

1.  Claude attempts exit\
2.  Stop hook checks completion\
3.  If incomplete → re-inject prompt\
4.  Repeat until done

------------------------------------------------------------------------

# Key Feature: Autonomous Business Handover

Triggered weekly.

Claude reviews:

-   Business goals\
-   Completed tasks\
-   Bank transactions

Outputs:

## Monday Morning CEO Briefing

Includes:

-   Executive summary\
-   Revenue metrics\
-   Bottlenecks\
-   Cost optimizations\
-   Upcoming deadlines

------------------------------------------------------------------------

# Security Architecture

## Credential Rules

-   Never store secrets in vault\
-   Use environment variables\
-   Rotate credentials monthly

Example `.env`:

    GMAIL_CLIENT_ID=xxx
    BANK_API_TOKEN=xxx

------------------------------------------------------------------------

## Sandboxing

-   DEV_MODE flag\
-   Dry-run support\
-   Test accounts\
-   Rate limiting

------------------------------------------------------------------------

## Audit Logging

Every action must log:

-   Timestamp\
-   Actor\
-   Target\
-   Approval status\
-   Result

Retention: **90 days minimum**.

------------------------------------------------------------------------

## Permission Boundaries

  Category        Auto                Approval
  --------------- ------------------- --------------
  Email replies   Known contacts      New contacts
  Payments        \< \$50 recurring   New payees
  Social posts    Scheduled           Replies
  File ops        Create/read         Delete

------------------------------------------------------------------------

# Error Recovery

  Category    Example             Strategy
  ----------- ------------------- --------------
  Transient   API timeout         Retry
  Auth        Expired token       Alert human
  Logic       Misinterpretation   Review queue
  Data        Corrupt file        Quarantine
  System      Crash               Auto-restart

Graceful degradation is mandatory.

------------------------------------------------------------------------

# Process Management

Watchers are daemon processes --- without supervision they die.

### Recommended Tool: PM2

Install:

``` bash
npm install -g pm2
pm2 start gmail_watcher.py --interpreter python3
pm2 save
pm2 startup
```

Provides:

-   Auto restart\
-   Boot persistence\
-   Logging

------------------------------------------------------------------------

# Ethics & Responsible Automation

### AI Should NOT Act Autonomously When:

-   Emotional conversations\
-   Legal matters\
-   Medical decisions\
-   Large financial actions\
-   Irreversible operations

### Principles

-   Disclose AI involvement\
-   Maintain audit trails\
-   Allow opt-outs\
-   Review weekly

**You remain accountable for your AI employee.**

Suggested oversight:

-   Daily: 2‑minute check\
-   Weekly: 15‑minute review\
-   Monthly: 1‑hour audit

------------------------------------------------------------------------

# Judging Criteria

  Criterion       Weight
  --------------- --------
  Functionality   30%
  Innovation      25%
  Practicality    20%
  Security        15%
  Documentation   10%

------------------------------------------------------------------------

# Submission Requirements

-   GitHub repo\
-   README\
-   Demo video (5--10 min)\
-   Security disclosure\
-   Tier declaration

Submit: https://forms.gle/JR9T1SJq5rmQyGkGA

------------------------------------------------------------------------

# Core Strengths

✅ Local-first privacy\
✅ Human approval safeguards\
✅ Autonomous reasoning\
✅ Scalable architecture

------------------------------------------------------------------------

# Final Insight

A Digital FTE is not just software --- it is **programmable headcount**.

Organizations that adopt early gain massive leverage in:

-   Cost efficiency\
-   Operational speed\
-   Decision support\
-   Automation maturity

The future workforce will be **hybrid: human + autonomous agents**.
