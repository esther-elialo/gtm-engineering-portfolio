import os
import csv
import json
import time
import requests
import anthropic
from dotenv import load_dotenv

load_dotenv()

APOLLO_KEY = os.getenv("APOLLO_API_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

def enrich_person_apollo(first_name, last_name, domain):
    """Enrich a person using Apollo People Match API"""
    url = "https://api.apollo.io/api/v1/people/match"
    headers = {
        "X-Api-Key": APOLLO_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "domain": domain,
        "reveal_personal_emails": False
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            person = response.json().get("person", {})
            if person:
                return {
                    "title": person.get("title", ""),
                    "seniority": person.get("seniority", ""),
                    "departments": person.get("departments", []),
                    "company_name": person.get("organization", {}).get("name", ""),
                    "company_industry": person.get("organization", {}).get("industry", ""),
                    "company_size": person.get("organization", {}).get("estimated_num_employees", ""),
                    "company_founded": person.get("organization", {}).get("founded_year", ""),
                    "linkedin": person.get("linkedin_url", "")
                }
    except Exception as e:
        print(f"  ⚠️  Apollo error: {e}")
    return {}

def get_company_signals(company, domain):
    """Use Claude web search to find recent signals about the company"""
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=600,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"""Search for recent news about {company} ({domain}) from the last 90 days.
Find: funding rounds, product launches, hiring surges, new partnerships, leadership changes, or expansion announcements.
Return only the 2-3 most relevant signals as a short bullet list. Be specific and concrete."""
        }]
    )
    signals = ""
    for block in response.content:
        if hasattr(block, "text"):
            signals += block.text
    return signals.strip()

def generate_email_sequence(contact, apollo_data, signals):
    """Generate 5-email outreach sequence using Claude Haiku"""

    enriched_title = apollo_data.get("title") or contact.get("title", "")
    enriched_company = apollo_data.get("company_name") or contact.get("company", "")
    enriched_industry = apollo_data.get("company_industry") or contact.get("industry", "")
    enriched_size = apollo_data.get("company_size") or contact.get("employees", "")

    prompt = f"""You are an expert B2B sales copywriter. Generate a 5-email outreach sequence for this prospect.

PROSPECT:
- Name: {contact['first_name']} {contact['last_name']}
- Title: {enriched_title}
- Company: {enriched_company}
- Industry: {enriched_industry}
- Company size: {enriched_size} employees

RECENT COMPANY SIGNALS:
{signals if signals else "No recent signals found — use general industry context"}

SEQUENCE RULES:
- Email 1: Pattern interrupt opener based on a specific signal. Short (3-4 lines). No pitch.
- Email 2: Share a relevant insight or stat for their industry. Soft CTA.
- Email 3: Social proof — similar company result. One concrete metric.
- Email 4: Different angle — address a likely pain point directly.
- Email 5: Breakup email. Honest, respectful, leaves door open.

FORMAT each email exactly like this:
EMAIL [N] — [Subject line]
[Body]
---

Keep each email under 80 words. Write in first person. No fluff."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def run_sequence_generator():
    print("\n🚀 SALES EMAIL SEQUENCE GENERATOR")
    print("   Stack: Apollo API + Claude web search + Claude Haiku")
    print("   ─────────────────────────────────────────────────\n")

    accounts = []
    with open("email-sequence/accounts.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts.append(row)

    print(f"📋 Loaded {len(accounts)} accounts from CSV\n")

    results = []

    for i, contact in enumerate(accounts, 1):
        name = f"{contact['first_name']} {contact['last_name']}"
        company = contact['company']
        domain = contact['domain']

        print(f"[{i}/{len(accounts)}] Processing {name} — {company}")

        # Step 1: Enrich with Apollo
        print(f"  🔍 Enriching via Apollo API...")
        apollo_data = enrich_person_apollo(contact['first_name'], contact['last_name'], domain)
        if apollo_data.get("title"):
            print(f"  ✅ Apollo: {apollo_data['title']} at {apollo_data['company_name']}")
        else:
            print(f"  ⚠️  Apollo: no match found, using CSV data")

        # Step 2: Get company signals
        print(f"  🌐 Searching signals for {company}...")
        signals = get_company_signals(company, domain)
        print(f"  ✅ Signals retrieved")

        # Step 3: Generate sequence
        print(f"  ✍️  Generating 5-email sequence...")
        sequence = generate_email_sequence(contact, apollo_data, signals)
        print(f"  ✅ Sequence generated\n")

        results.append({
            "contact": name,
            "company": company,
            "title": apollo_data.get("title") or contact.get("title"),
            "sequence": sequence
        })

        # Wait between accounts to avoid Opus rate limit
        if i < len(accounts):
            print(f"  ⏳ Waiting 45s before next account to avoid rate limit...\n")
            time.sleep(45)

    # Output results
    print("\n" + "="*60)
    print("📧 GENERATED SEQUENCES")
    print("="*60)

    for result in results:
        print(f"\n{'='*60}")
        print(f"👤 {result['contact']} — {result['title']} @ {result['company']}")
        print(f"{'='*60}")
        print(result['sequence'])

    # Save to JSON
    output_path = "email-sequence/sequences_output.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Results saved to {output_path}")

if __name__ == "__main__":
    run_sequence_generator()