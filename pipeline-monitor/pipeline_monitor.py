import os
import requests
import anthropic
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")

hubspot_headers = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}
client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

def get_deals():
    url = "https://api.hubapi.com/crm/v3/objects/deals"
    params = {
        "limit": 50,
        "properties": "dealname,amount,dealstage,closedate,hs_lastmodifieddate,pipeline"
    }
    response = requests.get(url, headers=hubspot_headers, params=params)
    return response.json().get("results", [])

def analyze_deal(deal):
    props = deal["properties"]
    name = props.get("dealname", "N/A")
    amount = props.get("amount", "0")
    stage = props.get("dealstage", "N/A")
    closedate = props.get("closedate", "N/A")
    last_modified = props.get("hs_lastmodifieddate", "N/A")

    # Calculate days until close and days since last activity
    today = datetime.now(timezone.utc)
    days_to_close = "N/A"
    days_stale = "N/A"

    if closedate and closedate != "N/A":
        try:
            close_dt = datetime.fromisoformat(closedate.replace("Z", "+00:00"))
            days_to_close = (close_dt - today).days
        except:
            pass

    if last_modified and last_modified != "N/A":
        try:
            mod_dt = datetime.fromisoformat(last_modified.replace("Z", "+00:00"))
            days_stale = (today - mod_dt).days
        except:
            pass

    return {
        "name": name,
        "amount": amount,
        "stage": stage,
        "days_to_close": days_to_close,
        "days_stale": days_stale,
        "closedate": closedate
    }

def generate_pipeline_report(deals_data):
    deals_summary = "\n".join([
        f"- {d['name']} | Stage: {d['stage']} | Amount: €{d['amount']} | "
        f"Days to close: {d['days_to_close']} | Days since last activity: {d['days_stale']}"
        for d in deals_data
    ])

    total_pipeline = sum(float(d['amount'] or 0) for d in deals_data)

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": f"""You are a Sales Manager AI assistant. Analyze this pipeline and generate a weekly health report.

PIPELINE DATA:
{deals_summary}

TOTAL PIPELINE VALUE: €{total_pipeline:,.0f}

Generate a report with this exact format:

PIPELINE HEALTH REPORT — {datetime.now().strftime("%d %b %Y")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY
Total pipeline: €{total_pipeline:,.0f}
[2 lines: overall pipeline health assessment]

🔴 AT RISK DEALS
[List deals with overdue close dates or stale for 30+ days, with specific action]

🟡 NEEDS ATTENTION
[List deals closing in <14 days or stale 14-30 days, with specific action]

🟢 ON TRACK
[List deals progressing well]

TOP PRIORITY THIS WEEK
1. [Most urgent action]
2. [Second priority]
3. [Third priority]"""
        }]
    )
    return message.content[0].text

def run_pipeline_monitor():
    print("\n⏳ Fetching deals from HubSpot...")
    deals = get_deals()
    print(f"✅ Found {len(deals)} deals\n")

    deals_data = [analyze_deal(d) for d in deals]

    print("⏳ Generating pipeline health report...")
    report = generate_pipeline_report(deals_data)

    print("\n" + report)

if __name__ == "__main__":
    run_pipeline_monitor()