# Pipeline Health Monitor

AI-powered agent that analyzes your HubSpot pipeline, detects at-risk deals, and generates a weekly health report with prioritized actions for the Sales Manager.

## What it does

Connects to HubSpot CRM, reads all active deals, and uses Claude to generate an executive pipeline report that identifies:

- **🔴 At-risk deals** — overdue close dates or stale for 30+ days
- **🟡 Needs attention** — closing soon or losing momentum
- **🟢 On track** — progressing well
- **Top 3 priorities** for the week, ordered by urgency and deal size

## Example output
```
PIPELINE HEALTH REPORT — 07 Mar 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY
Total pipeline: €114,000
Pipeline health is CONCERNING with 2 critical overdue deals totaling €51,000 (45% of pipeline).

🔴 AT RISK DEALS
- GlobalSaaS Inc — Enterprise (€45,000) | 36 DAYS OVERDUE
  ACTION: Contact decision-maker today to reschedule or confirm deal status.

🟡 NEEDS ATTENTION
- TechStartup SL — Annual (€24,000) | Closes in 12 days
  ACTION: Schedule demo within 3 days to maintain momentum.

TOP PRIORITY THIS WEEK
1. Contact GlobalSaaS Inc TODAY — €45K deal 36 days overdue
2. Push TechStartup SL to presentation stage — 12 days to close
3. Secure Typeform contract signature — decision-maker engaged
```

## Stack

- Python 3
- HubSpot CRM API v3
- Anthropic Claude API (claude-haiku)

## Setup
```bash
# Install dependencies
pip3 install anthropic requests python-dotenv

# Configure environment
cp .env.example .env
# Add your keys to .env

# Run
python3 pipeline_monitor.py
```

## .env required
```
ANTHROPIC_API_KEY=your_key
HUBSPOT_ACCESS_TOKEN=your_token
```

HubSpot Private App requires scopes: `crm.objects.deals.read`

## Use case

Run every Monday morning before your pipeline review. Takes 15 seconds instead of 30 minutes of manual CRM analysis.