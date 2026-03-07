import os
import requests
import anthropic
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")

def get_contacts(limit=5):
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_TOKEN}",
        "Content-Type": "application/json"
    }
    params = {
        "limit": limit,
        "properties": "firstname,lastname,email,company,jobtitle"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def analyze_contact(contact):
    props = contact["properties"]
    name = f"{props.get('firstname', '')} {props.get('lastname', '')}"
    email = props.get('email', 'N/A')
    company = props.get('company', 'N/A')
    jobtitle = props.get('jobtitle', 'N/A')

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": f"""Analiza este contacto y dame un ICP score del 1 al 10 con justificación breve.
                
Contacto:
- Nombre: {name}
- Email: {email}
- Empresa: {company}
- Cargo: {jobtitle}

ICP target: empresas B2B SaaS, decisores de ventas o marketing, empresas de 50-500 empleados.

Responde en este formato exacto:
ICP Score: X/10
Razón: [una línea]
Next action: [una acción concreta]"""
            }
        ]
    )
    return message.content[0].text

if __name__ == "__main__":
    data = get_contacts()
    for contact in data["results"]:
        props = contact["properties"]
        print(f"\n{'='*50}")
        print(f"Contacto: {props.get('firstname')} {props.get('lastname')} - {props.get('company')}")
        print(analyze_contact(contact))