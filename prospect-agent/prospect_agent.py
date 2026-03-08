import os
import json
import time
import csv
import requests
import anthropic
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

hubspot_headers = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

def load_icp_config():
    with open("prospect-agent/icp_config.json", "r") as f:
        return json.load(f)

def load_prospects_from_csv():
    prospects = []
    csv_path = "email-sequence/accounts.csv"
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prospects.append(row)
    return prospects

def get_signals_and_score(prospect, icp):
    """Single call: web search for signals + ICP scoring + outreach intel — all Haiku"""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"""You are a GTM intelligence agent. Do two things:

1. Search for recent news about {prospect['company']} ({prospect.get('domain', '')}) from the last 60 days.
   Look for: funding rounds, hiring activity, product launches, partnerships, expansion.

2. Then score this prospect against the ICP and generate outreach intel.

PROSPECT:
- Name: {prospect['first_name']} {prospect['last_name']}
- Title: {prospect['title']}
- Company: {prospect['company']}
- Industry: {prospect.get('industry', 'Unknown')}
- Employees: {prospect.get('employees', 'Unknown')}

ICP TARGET:
- Industries: {', '.join(icp['industries'])}
- Company size: {icp['company_size_min']}-{icp['company_size_max']} employees
- Target titles: {', '.join(icp['target_titles'])}

Respond ONLY in this exact JSON format, no markdown:
{{
  "icp_score": <number 1-10>,
  "icp_reason": "<one sentence why>",
  "buying_signal": "<most relevant signal found or None detected>",
  "outreach_angle": "<specific angle based on signals>",
  "opening_line": "<first sentence for cold outreach, max 20 words>"
}}"""
        }]
    )

    # Extract text from response
    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text

    try:
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception:
        return {
            "icp_score": 5,
            "icp_reason": "Unable to score",
            "buying_signal": "None detected",
            "outreach_angle": "General outreach",
            "opening_line": f"Hi {prospect['first_name']}, I'd love to connect."
        }

def check_existing_in_hubspot(email):
    if not email:
        return False
    url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
    payload = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "email",
                "operator": "EQ",
                "value": email
            }]
        }]
    }
    response = requests.post(url, headers=hubspot_headers, json=payload)
    return response.json().get("total", 0) > 0

def get_or_create_contact(prospect_data):
    """Create contact, or retrieve existing ID if already exists (409)"""
    contact_payload = {
        "properties": {
            "firstname": prospect_data["first_name"],
            "lastname": prospect_data["last_name"],
            "email": prospect_data.get("email", ""),
            "jobtitle": prospect_data["title"],
            "company": prospect_data["company"],
            "hs_lead_status": "NEW",
            "website": prospect_data.get("linkedin", "")
        }
    }
    resp = requests.post(
        "https://api.hubapi.com/crm/v3/objects/contacts",
        headers=hubspot_headers,
        json=contact_payload
    )

    if resp.status_code == 201:
        return resp.json()["id"]

    if resp.status_code == 409:
        existing_id = resp.json().get("message", "").split("ID: ")[-1]
        if existing_id.isdigit():
            print(f"  ℹ️  Contact exists (ID: {existing_id}) — creating deal anyway")
            return existing_id

    print(f"  ❌ Contact error {resp.status_code}: {resp.text[:200]}")
    return None

def add_to_hubspot_pipeline(prospect_data):
    """Add prospect as contact + deal in HubSpot first pipeline stage"""
    pipeline_url = "https://api.hubapi.com/crm/v3/pipelines/deals"
    pipeline_resp = requests.get(pipeline_url, headers=hubspot_headers)
    stages = pipeline_resp.json().get("results", [{}])[0].get("stages", [])
    first_stage_id = stages[0]["id"] if stages else "appointmentscheduled"

    contact_id = get_or_create_contact(prospect_data)
    if not contact_id:
        return False

    deal_payload = {
        "properties": {
            "dealname": f"{prospect_data['company']} — {datetime.now().strftime('%d %b %Y')}",
            "dealstage": first_stage_id,
            "amount": "0"
        }
    }
    deal_resp = requests.post(
        "https://api.hubapi.com/crm/v3/objects/deals",
        headers=hubspot_headers,
        json=deal_payload
    )

    if deal_resp.status_code != 201:
        print(f"  ❌ Deal error {deal_resp.status_code}: {deal_resp.text[:200]}")
        return False

    deal_id = deal_resp.json()["id"]
    requests.put(
        f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}/associations/contacts/{contact_id}/3",
        headers=hubspot_headers
    )
    return True

def run_prospect_agent():
    print(f"\n🤖 DAILY PROSPECT AGENT")
    print(f"   {datetime.now().strftime('%A %d %b %Y — %H:%M')}")
    print(f"   ─────────────────────────────────────────\n")

    icp = load_icp_config()
    print(f"📋 ICP: {icp['description']}")
    print(f"   Targets: {', '.join(icp['target_titles'][:3])}...")

    prospects = load_prospects_from_csv()
    print(f"   Prospects loaded: {len(prospects)} from Apollo/Clay export\n")
    print(f"   ⚠️  Note: Apollo Search API requires paid plan.")
    print(f"   Using CSV export workflow (Apollo free → export → enrich → pipeline)\n")

    results = []
    added_to_hubspot = 0
    skipped_duplicates = 0

    for i, prospect in enumerate(prospects, 1):
        name = f"{prospect['first_name']} {prospect['last_name']}"
        company = prospect['company']
        domain = prospect.get('domain', '')
        email = prospect.get('email', '')

        print(f"[{i}/{len(prospects)}] {name} — {prospect['title']} @ {company}")

        if check_existing_in_hubspot(email):
            print(f"  ⏭️  Already in HubSpot — skipping\n")
            skipped_duplicates += 1
            continue

        # Single call: signals + scoring
        print(f"  🔍 Searching signals + scoring ICP fit...")
        enrichment = get_signals_and_score(prospect, icp)
        print(f"  ⭐ ICP Score: {enrichment.get('icp_score')}/10")

        prospect_data = {
            "first_name": prospect["first_name"],
            "last_name": prospect["last_name"],
            "title": prospect["title"],
            "company": company,
            "domain": domain,
            "email": email,
            "linkedin": prospect.get("linkedin_url", ""),
            "icp_score": enrichment.get("icp_score", 0),
            "icp_reason": enrichment.get("icp_reason", ""),
            "buying_signal": enrichment.get("buying_signal", ""),
            "outreach_angle": enrichment.get("outreach_angle", ""),
            "opening_line": enrichment.get("opening_line", "")
        }

        print(f"  📥 Adding to HubSpot pipeline...")
        if add_to_hubspot_pipeline(prospect_data):
            print(f"  ✅ Added to pipeline\n")
            added_to_hubspot += 1
        else:
            print(f"  ⚠️  HubSpot error — saved locally\n")

        results.append(prospect_data)

    results.sort(key=lambda x: x["icp_score"], reverse=True)

    print("\n" + "="*55)
    print(f"📊 DAILY PROSPECT REPORT — {datetime.now().strftime('%d %b %Y')}")
    print("="*55)
    print(f"✅ Added to HubSpot: {added_to_hubspot}")
    print(f"⏭️  Skipped (duplicates): {skipped_duplicates}")
    print(f"\n🏆 TOP PROSPECTS BY ICP SCORE:")
    print("-"*55)

    for p in results[:5]:
        print(f"\n👤 {p['first_name']} {p['last_name']} — {p['title']}")
        print(f"   🏢 {p['company']} | 📧 {p['email'] or 'N/A'}")
        print(f"   🔗 {p['linkedin'] or 'N/A'}")
        print(f"   ⭐ ICP Score: {p['icp_score']}/10 — {p['icp_reason']}")
        print(f"   📡 Signal: {p['buying_signal']}")
        print(f"   🎯 Angle: {p['outreach_angle']}")
        print(f"   💬 Opening: {p['opening_line']}")

    output_path = "prospect-agent/daily_prospects.json"
    with open(output_path, "w") as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "summary": {
                "added_to_hubspot": added_to_hubspot,
                "skipped_duplicates": skipped_duplicates,
                "total_processed": len(results)
            },
            "prospects": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Full report saved to {output_path}")
    print(f"✅ Done. {added_to_hubspot} new prospects in your pipeline.")

if __name__ == "__main__":
    run_prospect_agent()