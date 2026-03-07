import os
import requests
import anthropic
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")

hubspot_headers = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

# --- STEP 1: Get company from HubSpot by domain ---

def get_company_by_domain(domain):
    url = "https://api.hubapi.com/crm/v3/objects/companies/search"
    payload = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "domain",
                "operator": "EQ",
                "value": domain
            }]
        }],
        "properties": ["name", "domain", "industry", "numberofemployees", 
                       "annualrevenue", "city", "country", "description"]
    }
    response = requests.post(url, headers=hubspot_headers, json=payload)
    results = response.json().get("results", [])
    return results[0] if results else None

# --- STEP 2: Search external signals via Anthropic web search ---

def get_external_signals(company_name, domain):
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"Search for recent news, job postings, and buying signals for {company_name} ({domain}). Focus on: funding rounds, hiring in sales/marketing, new product launches, leadership changes. Return a brief summary of the 3 most relevant signals."
        }]
    )
    for block in message.content:
        if hasattr(block, "text"):
            return block.text
    return "No external signals found."

# --- STEP 3: Generate GTM briefing ---

def generate_briefing(company_data, signals):
    props = company_data["properties"]
    
    context = f"""
Company: {props.get('name', 'N/A')}
Domain: {props.get('domain', 'N/A')}
Industry: {props.get('industry', 'N/A')}
Employees: {props.get('numberofemployees', 'N/A')}
Revenue: {props.get('annualrevenue', 'N/A')}
Location: {props.get('city', 'N/A')}, {props.get('country', 'N/A')}
Description: {props.get('description', 'N/A')}

External signals:
{signals}
"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{
            "role": "user",
            "content": f"""You are a GTM Intelligence analyst. Generate an executive briefing for an Account Executive about to reach out to this company.

{context}

Generate a briefing with this exact format:

COMPANY SNAPSHOT
[2-3 sentences: what they do, stage, size]

ICP FIT: X/10
[One line justification]

TOP BUYING SIGNALS
1. [Signal + why it matters for outreach]
2. [Signal + why it matters for outreach]
3. [Signal + why it matters for outreach]

RECOMMENDED OUTREACH ANGLE
[One specific, personalized angle for the first message]

SUGGESTED OPENING LINE
[A concrete first line for a cold email or LinkedIn message]"""
        }]
    )
    return message.content[0].text

# --- MAIN ---

def run_gtm_intel(domain):
    print(f"\n{'='*60}")
    print(f"🔍 GTM INTELLIGENCE REPORT — {domain}")
    print(f"{'='*60}")

    print("\n⏳ Step 1: Fetching company from HubSpot...")
    company = get_company_by_domain(domain)
    if not company:
        print(f"❌ Company with domain {domain} not found in HubSpot.")
        return
    print(f"✅ Found: {company['properties'].get('name')}")

    print("\n⏳ Step 2: Searching external signals...")
    signals = get_external_signals(
        company['properties'].get('name'),
        domain
    )
    print("✅ Signals retrieved.")

    print("\n⏳ Step 3: Generating GTM briefing...")
    briefing = generate_briefing(company, signals)

    print("\n" + briefing)
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    run_gtm_intel("factorialhr.com")