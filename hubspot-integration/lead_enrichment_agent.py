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

# --- HUBSPOT FUNCTIONS ---

def get_contacts(limit=5):
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    params = {
        "limit": limit,
        "properties": "firstname,lastname,email,company,jobtitle,phone"
    }
    response = requests.get(url, headers=hubspot_headers, params=params)
    return response.json().get("results", [])

def get_companies(limit=5):
    url = "https://api.hubapi.com/crm/v3/objects/companies"
    params = {
        "limit": limit,
        "properties": "name,domain,industry,numberofemployees,annualrevenue,city,country"
    }
    response = requests.get(url, headers=hubspot_headers, params=params)
    return response.json().get("results", [])

# --- CLAUDE ANALYSIS ---

def analyze_lead(data, lead_type="contact"):
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    if lead_type == "contact":
        props = data["properties"]
        context = f"""
- Nombre: {props.get('firstname', '')} {props.get('lastname', '')}
- Email: {props.get('email', 'N/A')}
- Empresa: {props.get('company', 'N/A')}
- Cargo: {props.get('jobtitle', 'N/A')}
"""
    else:
        props = data["properties"]
        context = f"""
- Empresa: {props.get('name', 'N/A')}
- Dominio: {props.get('domain', 'N/A')}
- Industria: {props.get('industry', 'N/A')}
- Empleados: {props.get('numberofemployees', 'N/A')}
- Revenue anual: {props.get('annualrevenue', 'N/A')}
- País: {props.get('country', 'N/A')}
"""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": f"""Analiza este {lead_type} y dame un ICP score del 1 al 10.

{context}

ICP target: empresas B2B SaaS, decisores de ventas o marketing, 50-500 empleados.

Responde en este formato exacto:
ICP Score: X/10
Razón: [una línea]
Next action: [una acción concreta]"""
            }
        ]
    )
    return message.content[0].text

# --- MAIN ---

if __name__ == "__main__":
    print("\n🔍 LEAD ENRICHMENT AGENT")
    print("=" * 50)

    print("\n📋 CONTACTS")
    print("-" * 50)
    contacts = get_contacts()
    for contact in contacts:
        props = contact["properties"]
        name = f"{props.get('firstname', '')} {props.get('lastname', '')}"
        company = props.get('company', 'N/A')
        print(f"\n➤ {name} — {company}")
        print(analyze_lead(contact, "contact"))

    print("\n\n🏢 COMPANIES")
    print("-" * 50)
    companies = get_companies()
    for company in companies:
        props = company["properties"]
        print(f"\n➤ {props.get('name', 'N/A')} — {props.get('domain', 'N/A')}")
        print(analyze_lead(company, "company"))