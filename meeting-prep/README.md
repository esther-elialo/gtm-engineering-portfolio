# Meeting Prep Agent

AI agent that generates a complete pre-meeting briefing for any prospect in seconds. Given a name and company, it pulls CRM data, searches real-time signals, and produces a structured briefing ready to read 5 minutes before the call.

## What it does

1. **Fetches CRM data** — contact info, job title, lead status, existing deals from HubSpot
2. **Searches external signals** — recent news, hiring activity, product launches, funding rounds
3. **Generates the briefing** — structured output with everything the AE needs to walk in prepared

## Output
```
MEETING PREP BRIEFING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 WHO YOU'RE MEETING
Role, responsibilities, what they care about

🏢 COMPANY SNAPSHOT  
What they do, size, market position, strategic priorities

📡 BUYING SIGNALS
3 specific signals suggesting readiness or priority areas

⚠️ LIKELY OBJECTIONS
2-3 objections with a one-line response for each

🎯 RECOMMENDED TALK TRACK
Opening line · Key angle · Discovery question

✅ YOUR OBJECTIVE FOR THIS MEETING
One clear sentence: what to walk out with
```

## Usage
```bash
# Default test (Brian Halligan / Typeform)
python3 meeting_prep.py

# Custom prospect
python3 meeting_prep.py "Maria Garcia" "Factorial HR"
```

## Stack

- Python 3
- HubSpot CRM API v3 — contact, company and deal data
- Anthropic Claude API — web search (signals) + briefing generation

## Setup
```bash
pip3 install anthropic requests python-dotenv
cp .env.example .env
# Add your keys to .env
python3 meeting_prep.py
```

## .env required
```
ANTHROPIC_API_KEY=your_key
HUBSPOT_ACCESS_TOKEN=your_token
```

HubSpot Private App requires: `crm.objects.contacts.read` · `crm.objects.companies.read` · `crm.objects.deals.read`

## Use case

Replace 30 minutes of manual research before every discovery call. Run it while you're walking to the meeting room.