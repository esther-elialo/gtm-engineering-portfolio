# Daily Prospect Agent

AI agent that runs every morning, finds new prospects matching your ICP, scores them, searches for buying signals, and automatically adds them to the first stage of your HubSpot pipeline — ready for outreach.

## What it does

1. **Loads target accounts** — from Apollo/Clay CSV export
2. **Checks for duplicates** — skips contacts already in HubSpot
3. **Searches buying signals** — real-time signals per company (funding, hiring, launches)
4. **Scores ICP fit** — 1-10 score with reasoning per prospect
5. **Populates HubSpot pipeline** — creates contact + deal in first stage with outreach intel

## Output per prospect
```
👤 Maria Garcia — VP of Sales @ Factorial HR
   📧 maria@factorialhr.com
   🔗 linkedin.com/in/mariagarcia
   ⭐ ICP Score: 9/10 — B2B SaaS, decision maker, 200 employees within target range
   📡 Signal: Factorial raised €80M Series C and expanding into new European markets
   🎯 Angle: Scale sales motion across new markets without proportional headcount growth
   💬 Opening: Maria, saw Factorial just launched in Poland — how are you scaling the sales motion?
```

## Stack

- Python 3
- Apollo API — contact enrichment (People Match endpoint)
- Anthropic Claude Opus 4.6 — web search for real-time buying signals
- Anthropic Claude Haiku 4.5 — ICP scoring + outreach angle generation
- HubSpot CRM API — contact and deal creation in pipeline

## Apollo free plan vs paid plan

**This demo uses a CSV export workflow** — contacts are loaded from an Apollo/Clay export file rather than queried live via API. This is intentional: the Apollo Search API (`/mixed_people/search`) requires a paid plan.

**What this agent does with a free plan:**
- Reads contacts from Apollo CSV export
- Enriches each one with buying signals via Claude web search
- Scores ICP fit and generates outreach intel
- Populates HubSpot pipeline automatically

**What this agent would do with Apollo paid plan ($49+/month):**
- Search Apollo's 220M+ contact database live by ICP filters (industry, title, company size, location)
- Find the right decision maker at any company automatically
- Run daily with zero manual CSV exports
- Scale to 30+ new prospects per day fully autonomously
- Combine with Apollo's intent data for even sharper signal detection

The core logic, scoring, and HubSpot integration are identical in both cases. In production, upgrading to Apollo paid unlocks the full autonomous pipeline generation.

## Real-world workflow
```
Apollo (search by ICP filters) → export CSV
    ↓
Clay (waterfall enrichment — LinkedIn, job postings, tech stack)
    ↓
prospect_agent.py → buying signals + ICP scoring
    ↓
HubSpot pipeline (first stage, ready for outreach)
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

## Scheduling (production)

To run automatically every morning at 8AM, use n8n:
1. Create a Schedule Trigger node (8:00 AM daily)
2. Add an Execute Command node: `python3 /path/to/prospect_agent.py`
3. Deploy and forget — prospects appear in your pipeline every morning