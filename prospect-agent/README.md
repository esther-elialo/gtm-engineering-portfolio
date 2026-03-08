# Daily Prospect Agent

AI agent that runs every morning, finds new prospects matching your ICP, scores them, searches for real-time buying signals, and automatically adds them to the first stage of your HubSpot pipeline — ready for outreach.

## What it does

1. **Loads target accounts** — from Apollo/Clay CSV export
2. **Checks for duplicates** — skips contacts already in HubSpot
3. **Searches buying signals + scores ICP fit** — single optimized call per prospect
4. **Populates HubSpot pipeline** — creates contact + deal in first stage with outreach intel

## Output per prospect
```
👤 Maria Garcia — VP of Sales @ Factorial HR
   📧 maria@factorialhr.com
   🔗 linkedin.com/in/mariagarcia
   ⭐ ICP Score: 9/10 — Perfect title, industry and size match; VP of Sales at HR SaaS with 200 employees
   📡 Signal: $120M non-dilutive GTM funding + expanding into Germany, France and Italy
   🎯 Angle: Position as revenue acceleration partner for their European market entry
   💬 Opening: Maria, saw Factorial hit $100M ARR and Germany expansion — how are you scaling sales ops?
```

## Model optimization

This agent is designed to deliver maximum output at minimum cost:

| Task | Model | Reason |
|---|---|---|
| Web search + ICP scoring | Claude Haiku 4.5 | Single combined call — signals and scoring in one request |

**Same output, half the cost, twice the speed.**

Early versions used Claude Opus 4.6 for web search and a separate Claude Haiku call for scoring — two API calls per prospect. The optimized version combines both into a single Haiku call, since web search quality depends on the tool, not the model reasoning. Result: 50% fewer API calls, no rate limit delays, faster execution.

## Apollo free plan vs paid plan

**This demo uses a CSV export workflow** — contacts are loaded from an Apollo/Clay export file rather than queried live via API. This is intentional: the Apollo Search API (`/mixed_people/search`) requires a paid plan.

**What this agent does with a free plan:**
- Reads contacts from Apollo CSV export (manual step)
- Enriches each one with real-time buying signals
- Scores ICP fit and generates outreach intel
- Populates HubSpot pipeline automatically

**What this agent would do with Apollo paid plan ($49+/month):**
- Search Apollo's 220M+ contact database live by ICP filters (industry, title, company size, location)
- Find the right decision maker at any target company automatically
- Run daily with zero manual CSV exports
- Scale to 30+ new prospects per day fully autonomously
- Combine with Apollo intent data for sharper signal detection

The core logic, ICP scoring, and HubSpot integration are identical in both cases. Upgrading Apollo unlocks the full autonomous pipeline generation.

## Real-world workflow
```
Apollo (search by ICP filters) → export CSV
    ↓
Clay (waterfall enrichment — LinkedIn, job postings, tech stack)
    ↓
prospect_agent.py → buying signals + ICP scoring (single Haiku call)
    ↓
HubSpot pipeline (first stage, contact + deal created, ready for outreach)
```

## ICP configuration

Edit `icp_config.json` to define your ICP without touching code:
```json
{
  "description": "B2B SaaS companies looking to scale their sales team",
  "industries": ["computer software", "saas", "hr software"],
  "company_size_min": 50,
  "company_size_max": 500,
  "target_titles": ["VP of Sales", "CRO", "Head of Growth"],
  "locations": ["Spain", "France", "Germany", "United Kingdom"]
}
```

## Stack

- Python 3
- Apollo API — contact data source (CSV export on free plan, live search on paid plan)
- Clay — waterfall enrichment (LinkedIn activity, job postings, tech stack)
- Anthropic Claude Haiku 4.5 — web search + ICP scoring + outreach intel (single call)
- HubSpot CRM API — contact and deal creation in pipeline

## Setup
```bash
pip3 install anthropic requests python-dotenv
cp .env.example .env
# Add your keys to .env
python3 prospect_agent.py
```

## .env required
```
ANTHROPIC_API_KEY=your_key
HUBSPOT_ACCESS_TOKEN=your_token
```

HubSpot Private App requires: `crm.objects.contacts.read` · `crm.objects.contacts.write` · `crm.objects.deals.read` · `crm.objects.deals.write`

## Scheduling (production)

To run automatically every morning at 8AM, use n8n:
1. Create a Schedule Trigger node (8:00 AM daily)
2. Add an Execute Command node: `python3 /path/to/prospect_agent.py`
3. Deploy and forget — prospects appear in your pipeline every morning