# GTM Engineering Portfolio — Esther Elías

Sales Manager, Senior Account Executive, GTM Specialist — and now GTM Engineer. I build the AI agents that supercharge and multiply what my team and I can do.

## Projects

---

### 1. ICP Qualification Agent
AI-powered agent that evaluates companies against your Ideal Customer Profile and returns structured scores with outreach recommendations.

- **Input:** Company name + context (or a CSV list)
- **Output:** JSON with scores across 4 dimensions + personalized outreach hook
- **Stack:** Python · Anthropic Claude API
- **Value:** Qualify 50 accounts in the time it takes to manually research 5

→ [View project](./icp-qualifier)

---

### 2. Lead Enrichment Agent
Agent that connects to HubSpot CRM, reads contacts and companies, and automatically generates an ICP score with justification and next action for each lead.

- **Input:** HubSpot CRM contacts and companies
- **Output:** ICP Score + reason + concrete next action per lead
- **Stack:** Python · HubSpot CRM API · Anthropic Claude API
- **Value:** Enrich and prioritize an entire CRM in seconds, not hours

→ [View project](./hubspot-integration)

---

### 3. GTM Intelligence Tool
Multi-step agent that generates an executive GTM briefing for any target account. Fetches CRM data, searches real-time buying signals, and produces a structured briefing ready for the AE.

- **Input:** Company domain (e.g. `typeform.com`)
- **Output:** ICP fit score + buying signals + outreach angle + suggested opening line
- **Stack:** Python · HubSpot CRM API · Anthropic Claude API · web search
- **Value:** 45 minutes of manual account research done in 15 seconds

→ [View project](./gtm-intelligence)

---

### 4. Pipeline Health Monitor
AI agent that connects to HubSpot CRM, analyzes all active deals, and generates a weekly pipeline health report with prioritized actions for the Sales Manager.

- **Input:** HubSpot CRM deals (automatic)
- **Output:** Pipeline health report with 🔴 at-risk, 🟡 needs attention, 🟢 on track + top 3 priorities
- **Stack:** Python · HubSpot CRM API · Anthropic Claude API
- **Value:** 30 minutes of manual pipeline review done in 15 seconds, every Monday morning

→ [View project](./pipeline-monitor)

---

## Stack

| Tool | Usage |
|---|---|
| Python | Core scripting and agent logic |
| Anthropic Claude API | LLM reasoning, scoring, briefing generation |
| HubSpot CRM API | Contact and company data |
| web Auúnsearch (Claude tool) | Real-time buying signals |
| Git + GitHub | Version control and portfolio |

## About

Background in Sales Management, Account Executive, and GTM Strategy. Now I can also build the technical layer that makes GTM and Sales teams 10x more effective.

→ [LinkedIn](https://linkedin.com/in/esther-elias) · [GitHub](https://github.com/esther-elialo)