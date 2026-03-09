# Lead Scoring Pipeline

Real-time lead scoring automation. When a new contact enters HubSpot, this workflow scores them against your ICP using Claude AI and automatically routes them — high-value leads get flagged in the CRM, discarded leads go to a Google Sheet for full pipeline visibility.

No manual triage. No leads falling through the cracks.

---

## What it does

1. **Receives** contact data via webhook (triggered by HubSpot or any source)
2. **Scores** the lead using Claude AI — evaluates name, company, job title and email against ICP criteria
3. **Routes** based on score:
   - Score ≥ 7 → Updates contact in HubSpot (`Lead Status: In Progress`)
   - Score < 7 → Appends row to Google Sheets with full reasoning

---

## Output per lead (score ≥ 7)
```
HubSpot contact updated:
  Name: Maria Garcia
  Company: Factorial HR
  Title: VP of Sales
  Lead Status: In Progress
  ICP Score: 9/10
  Reason: VP of Sales at HR SaaS with 200 employees — perfect ICP fit
  Next Action: sequence
```

## Output per lead (score < 7)

Row added to Google Sheets:

| Fecha | Nombre | Empresa | Cargo | Email | ICP Score | Razón | Señal |
|-------|--------|---------|-------|-------|-----------|-------|-------|
| 2026-03-09 | John Smith | Self Employed | Freelance Designer | john@... | 2 | Not a B2B buyer | discard |

---

## Architecture
```
Webhook (POST)
    │
    ▼
HTTP Request → Claude API (claude-haiku-4-5)
    │          Evaluates contact data against ICP
    ▼
Code Node → Parses Claude JSON response
    │        Recovers contact data from webhook
    ▼
If Node → icp_score ≥ 7?
    │
    ├── TRUE  → HubSpot: Update Contact
    │           Lead Status = IN_PROGRESS
    │
    └── FALSE → Google Sheets: Append Row
                Fecha · Nombre · Empresa · Cargo · Email · Score · Razón · Señal
```

---

## Claude prompt

Claude receives contact data and returns a structured JSON:
```json
{
  "icp_score": 9,
  "reason": "VP of Sales at HR SaaS with 200 employees — perfect title, industry and size match",
  "next_action": "sequence"
}
```

`next_action` is one of: `sequence` | `nurture` | `discard`

---

## Stack

| Tool | Usage |
|------|-------|
| n8n Cloud | Workflow automation and routing logic |
| Claude Haiku 4.5 | ICP scoring via Claude API |
| HubSpot CRM API | Contact update (APP Token auth) |
| Google Sheets | Discard log (OAuth2) |

---

## Webhook payload format
```json
{
  "firstname": "Maria",
  "lastname": "Garcia",
  "email": "maria.garcia@company.com",
  "company": "Factorial HR",
  "jobtitle": "VP of Sales"
}
```

---

## Test it
```bash
curl -X POST "YOUR_N8N_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "firstname": "Maria",
    "lastname": "Garcia",
    "email": "maria.garcia@factorial.hr",
    "company": "Factorial HR",
    "jobtitle": "VP of Sales"
  }'
```

---

## Setup

### Prerequisites
- n8n Cloud account
- Anthropic API key
- HubSpot Private App token (scopes: `crm.objects.contacts.read` · `crm.objects.contacts.write`)
- Google Sheets connected via OAuth2 in n8n

### Credentials in n8n
1. **Anthropic** — Header Auth: `x-api-key` + your API key
2. **HubSpot** — APP Token (`pat-eu1-...` from Private App)
3. **Google Sheets** — Google Sheets account (OAuth2)

---

## Why this matters

Manual lead triage is a bottleneck in every sales team. This workflow:

- Scores every inbound lead instantly and consistently against ICP criteria
- Routes qualified leads directly into the CRM without human touch
- Gives RevOps full visibility into both qualified and discarded leads
- Runs 24/7 — no one needs to be online for it to work

---

## Part of GTM Engineering Portfolio

This is Project 8 of the [GTM Engineering Portfolio](../README.md) — a collection of AI-powered tools built for modern sales/partnerships/revenue teams.