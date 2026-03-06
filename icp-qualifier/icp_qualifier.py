import anthropic
from dotenv import load_dotenv
import os
import json
import csv
from datetime import datetime

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert GTM analyst specializing in ICP (Ideal Customer Profile) qualification.

Your job is to evaluate whether a company is a strong ICP fit based on the information provided.

You will score companies on a scale of 1-10 across these dimensions:
- Company Size Fit (headcount and revenue stage)
- Tech Stack Signals (do they use modern/complementary tools?)
- Growth Signals (hiring, funding, expansion)
- Pain Point Alignment (do they likely have the problems we solve?)

CRITICAL: Respond with ONLY a valid JSON object. No markdown, no code blocks, no explanation. Just the raw JSON.

Output format:
{
  "company": "company name",
  "overall_score": X,
  "dimensions": {
    "company_size_fit": {"score": X, "reasoning": "..."},
    "tech_stack_signals": {"score": X, "reasoning": "..."},
    "growth_signals": {"score": X, "reasoning": "..."},
    "pain_point_alignment": {"score": X, "reasoning": "..."}
  },
  "summary": "2-3 sentence executive summary",
  "recommended_action": "Prioritize / Nurture / Deprioritize",
  "suggested_hook": "One personalized opening line for outreach"
}

Be direct, data-driven, and commercially realistic. Don't inflate scores."""


def parse_response(raw_response: str) -> dict:
    """
    Limpia el output de Claude y lo convierte en un diccionario Python.
    Maneja casos donde Claude añade markdown alrededor del JSON.
    """
    # Eliminar markdown code blocks si existen
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        # Eliminar primera línea (```json o ```)
        cleaned = cleaned.split("\n", 1)[1]
    if cleaned.endswith("```"):
        # Eliminar última línea
        cleaned = cleaned.rsplit("```", 1)[0]
    
    cleaned = cleaned.strip()
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw response: {raw_response}")
        return {"error": "Failed to parse response", "raw": raw_response}


def qualify_company(company_name: str, context: str = "") -> dict:
    """
    Qualifica una empresa contra el ICP.
    Devuelve un diccionario estructurado con scores y recomendaciones.
    """
    user_message = f"Company to evaluate: {company_name}"
    if context:
        user_message += f"\n\nAdditional context: {context}"

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    raw = message.content[0].text
    return parse_response(raw)


def process_csv(filepath: str) -> list:
    """
    Lee una lista de empresas desde un CSV y las qualifica todas.
    El CSV debe tener columnas: company_name, context (opcional)
    """
    results = []
    
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        companies = list(reader)
    
    print(f"Processing {len(companies)} companies...\n")
    
    for i, row in enumerate(companies, 1):
        company_name = row.get("company_name", "")
        context = row.get("context", "")
        
        if not company_name:
            continue
            
        print(f"[{i}/{len(companies)}] Evaluating: {company_name}")
        result = qualify_company(company_name, context)
        results.append(result)
        
        # Mostrar resultado resumido
        if "error" not in result:
            print(f"  Score: {result.get('overall_score')}/10 | Action: {result.get('recommended_action')}")
        else:
            print(f"  Error processing this company")
    
    return results


def save_results(results: list, output_file: str = None):
    """
    Guarda los resultados en un archivo JSON con timestamp.
    """
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"results_{timestamp}.json"
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    return output_file


# --- MODO DE USO ---

if __name__ == "__main__":
    import sys
    
    # Si se pasa un CSV como argumento: python3 icp_qualifier.py companies.csv
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        results = process_csv(csv_file)
        save_results(results)
    
    # Si no, ejecutar test con empresas de ejemplo
    else:
        print("Running test with sample companies...\n")
        
        test_companies = [
            {
                "name": "Linear",
                "context": "Series B startup, ~80 employees, project management tool for engineering teams. Recently announced integration with GitHub and Figma."
            },
            {
                "name": "Gong",
                "context": "Revenue intelligence platform, ~1000 employees, Series E. Known users: Salesforce, HubSpot users."
            },
            {
                "name": "Local restaurant chain",
                "context": "5 locations, family business, no tech stack mentioned online."
            }
        ]
        
        results = []
        for company in test_companies:
            print(f"{'='*50}")
            print(f"Evaluating: {company['name']}")
            print('='*50)
            result = qualify_company(company["name"], company["context"])
            results.append(result)
            
            if "error" not in result:
                print(f"Score: {result.get('overall_score')}/10")
                print(f"Action: {result.get('recommended_action')}")
                print(f"Hook: {result.get('suggested_hook')}")
                print(f"Summary: {result.get('summary')}")
            print()
        
        save_results(results)