import os
import sys
import requests
import anthropic
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")

hubspot_headers = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}
client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

def search_contact_in_hubspot(name):
    """Search for a contact in HubSpot by name"""
    url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
    payload = {
        "query": name,
        "limit": 1,
        "properties": [
            "firstname", "lastname", "email", "jobtitle",
            "company", "phone", "hs_lead_status", "notes_last_updated"
        ]
    }
    response = requests.post(url, headers=hubspot_headers, json=payload)
    results = response.json().get("results", [])
    if results:
        return results[0]["properties"]
    return None

def search_company_in_hubspot(company_name):
    """Search for a company in HubSpot by name"""
    url = "https://api.hubapi.com/crm/v3/objects/companies/search"
    payload = {
        "query": company_name,
        "limit": 1,
        "properties": [
            "name", "domain", "industry", "numberofemployees",
            "annualrevenue", "city", "country", "description"
        ]
    }
    response = requests.post(url, headers=hubspot_headers, json=payload)
    results = response.json().get("results", [])
    if results:
        return results[0]["properties"]
    return None

def search_deals_for_company(company_name):
    """Search for any existing deals related to the company"""
    url = "https://api.hubapi.com/crm/v3/objects/deals/search"
    payload = {
        "query": company_name,
        "limit": 3,
        "properties": ["dealname", "dealstage", "amount", "closedate"]
    }
    response = requests.post(url, headers=hubspot_headers, json=payload)
    results = response.json().get("results", [])
    return [r["properties"] for r in results]

def get_external_signals(prospect_name, company_name):
    """Use Claude web search to find recent signals about the company"""
    print("  🔍 Searching external signals...")
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"""Search for recent information about {company_name} to prepare for a sales meeting. Find:
1. Recent company news (last 3 months)
2. Recent job postings that signal priorities or growth areas
3. Any funding rounds, partnerships, or product launches
4. Any challenges or pain points mentioned in the press

Search for: "{company_name} news 2026" and "{company_name} hiring" and "{prospect_name} {company_name}"

Return a concise summary of the 3-5 most relevant signals you find."""
        }]
    )
    
    signals = ""
    for block in response.content:
        if hasattr(block, "text"):
            signals += block.text
    return signals

def generate_meeting_briefing(prospect_name, company_name, contact_data, company_data, deals_data, signals):
    """Generate the full meeting prep briefing"""
    
    contact_info = f"""
Contact in HubSpot: {contact_data if contact_data else 'Not found in CRM'}
"""
    if contact_data:
        contact_info = f"""
- Name: {contact_data.get('firstname', '')} {contact_data.get('lastname', '')}
- Title: {contact_data.get('jobtitle', 'Unknown')}
- Email: {contact_data.get('email', 'Unknown')}
- Lead status: {contact_data.get('hs_lead_status', 'Unknown')}
"""

    company_info = "Company not found in CRM"
    if company_data:
        company_info = f"""
- Company: {company_data.get('name', company_name)}
- Industry: {company_data.get('industry', 'Unknown')}
- Employees: {company_data.get('numberofemployees', 'Unknown')}
- Revenue: {company_data.get('annualrevenue', 'Unknown')}
- Location: {company_data.get('city', '')}, {company_data.get('country', '')}
"""

    deals_info = "No existing deals"
    if deals_data:
        deals_info = "\n".join([
            f"- {d.get('dealname')} | Stage: {d.get('dealstage')} | €{d.get('amount', '0')}"
            for d in deals_data
        ])

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        messages=[{
            "role": "user",
            "content": f"""You are a sales intelligence assistant. Generate a meeting prep briefing for a sales rep about to meet with a prospect.

PROSPECT: {prospect_name}
COMPANY: {company_name}

CRM DATA:
{contact_info}

COMPANY DATA:
{company_info}

EXISTING DEALS:
{deals_info}

EXTERNAL SIGNALS:
{signals}

Generate a briefing with this EXACT format:

MEETING PREP BRIEFING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 WHO YOU'RE MEETING
[2-3 sentences about the person — role, likely responsibilities, what they care about]

🏢 COMPANY SNAPSHOT
[2-3 sentences about the company — what they do, size, market position]

📡 BUYING SIGNALS
[3 specific signals from the data above that suggest readiness or priority areas]
- Signal 1
- Signal 2  
- Signal 3

⚠️ LIKELY OBJECTIONS
[2-3 objections this type of prospect typically raises, with a one-line response for each]
- Objection: [objection] → Response: [how to handle it]

🎯 RECOMMENDED TALK TRACK
Opening line: [specific first sentence to open the meeting]
Key angle: [the main value angle to focus on based on their signals]
Question to ask: [one powerful discovery question tailored to their situation]

✅ YOUR OBJECTIVE FOR THIS MEETING
[One clear sentence: what you want to walk out with]"""
        }]
    )
    return response.content[0].text

def run_meeting_prep(prospect_name, company_name):
    print(f"\n🚀 MEETING PREP AGENT")
    print(f"   Prospect: {prospect_name}")
    print(f"   Company:  {company_name}")
    print(f"   Date:     {datetime.now().strftime('%d %b %Y, %H:%M')}\n")

    print("📂 Step 1/3 — Fetching CRM data...")
    contact_data = search_contact_in_hubspot(prospect_name)
    company_data = search_company_in_hubspot(company_name)
    deals_data = search_deals_for_company(company_name)

    if contact_data:
        print(f"  ✅ Contact found: {contact_data.get('firstname')} {contact_data.get('lastname')} — {contact_data.get('jobtitle')}")
    else:
        print(f"  ⚠️  Contact not found in CRM — proceeding with external data")

    if company_data:
        print(f"  ✅ Company found: {company_data.get('name')} — {company_data.get('industry')}")

    if deals_data:
        print(f"  ✅ Found {len(deals_data)} existing deal(s)")

    print("\n🌐 Step 2/3 — Searching external signals...")
    signals = get_external_signals(prospect_name, company_name)
    print("  ✅ Signals retrieved")

    print("\n🧠 Step 3/3 — Generating briefing...")
    briefing = generate_meeting_briefing(
        prospect_name, company_name,
        contact_data, company_data, deals_data, signals
    )

    print("\n" + "="*50)
    print(briefing)
    print("="*50)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        prospect = sys.argv[1]
        company = sys.argv[2]
    else:
        # Default test case
        prospect = "Brian Halligan"
        company = "Typeform"
    
    run_meeting_prep(prospect, company)