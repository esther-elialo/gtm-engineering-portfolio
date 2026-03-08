# Sales Email Sequence Generator

AI agent that takes a list of target accounts and generates a personalized 5-email outreach sequence for each contact, based on real-time company signals and enriched contact data.

## What it does

1. **Enriches contacts via Apollo API** — title, seniority, company size, industry
2. **Searches real-time signals** — funding rounds, product launches, hiring activity, partnerships (last 90 days)
3. **Generates 5-email sequence per contact** — each email with a different angle, all grounded in specific signals

## Email sequence structure

- **Email 1** — Pattern interrupt opener based on a specific company signal
- **Email 2** — Industry insight or stat with soft CTA
- **Email 3** — Social proof with one concrete metric
- **Email 4** — Pain point angle, direct question
- **Email 5** — Breakup email, respectful, leaves door open

## Example output
```
👤 Maria Garcia — VP of Sales @ Factorial HR

EMAIL 1 — Poland expansion just went live
Maria, saw Factorial launched in Poland this month with a remote-first playbook.
Curious how you're scaling the sales motion across 10 countries without
traditional boots-on-the-ground infrastructure. Worth a quick conversation?

EMAIL 5 — Stepping back
Five emails in, and I haven't heard back. Either I'm not solving something
that matters, or timing's off. Either way—genuinely curious if there's
anything worth exploring. Open to it?
```

## Real-world workflow

In production this agent fits into a larger GTM stack:
```
Apollo → search and export contacts by ICP filters
    ↓
Clay → waterfall enrichment (LinkedIn activity, job postings, tech stack)
    ↓
accounts.csv → this script → 5 emails per contact
    ↓
HubSpot or Apollo Sequences → load and send
```

## Stack

- Python 3
- Apollo API — contact enrichment (People Match endpoint)
- Anthropic Claude Opus 4.6 — web search for real-time signals
- Anthropic Claude Haiku 4.5 — email sequence generation
- Clay — waterfall enrichment (manual export workflow)

## Setup
```bash
pip3 install anthropic requests python-dotenv
cp .env.example .env
# Add your keys to .env
python3 email_sequence.py
```

## .env required
```
ANTHROPIC_API_KEY=your_key
APOLLO_API_KEY=your_key
```

## Input format

Edit `accounts.csv` with your target accounts. Compatible with Apollo CSV exports and Clay exports.

## Output

- Console: full sequences printed per contact
- `sequences_output.json`: all sequences saved for loading into your sequencer