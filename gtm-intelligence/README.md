# GTM Intelligence Tool

Multi-step agent that generates an executive GTM briefing for any target account in seconds. Given a company domain, it fetches CRM data from HubSpot, searches for real-time buying signals, and produces a structured briefing ready for the AE.

## ¿Qué problema resuelve?

Preparar una cuenta antes de un outreach tarda 30-45 minutos si se hace manualmente: buscar la empresa, revisar LinkedIn, leer noticias, pensar el ángulo. Este agente lo hace en 15 segundos y devuelve un briefing estructurado y accionable.

## Output de ejemplo
```
🔍 GTM INTELLIGENCE REPORT — typeform.com

COMPANY SNAPSHOT
Typeform is a 400-person SaaS company headquartered in Spain that provides 
a conversational forms platform used by enterprises globally.

ICP FIT: 8/10
Mid-to-large SaaS with active investment in customer experience — strong fit.

TOP BUYING SIGNALS
1. Acquisition Interest – Exploring strategic growth, budget available
2. Scale & Growth – 400 employees, operational efficiency is a board priority
3. International Expansion – Spain HQ + global base, evaluating new tools

RECOMMENDED OUTREACH ANGLE
Position as enabler of their next growth phase post-expansion.

SUGGESTED OPENING LINE
"I noticed Typeform has been actively exploring strategic growth opportunities — 
I wanted to connect because several scaling SaaS companies have found [X] 
critical when managing rapid expansion."
```

## Arquitectura
```
Input: company domain (e.g. "typeform.com")
         ↓
Step 1: HubSpot CRM API    → company data (size, industry, location)
         ↓
Step 2: Claude web search  → real-time signals (news, hiring, funding)
         ↓
Step 3: Claude briefing    → ICP fit + buying signals + outreach angle
         ↓
Output: executive briefing ready for AE
```

## Stack

- **Python 3.9+**
- **HubSpot CRM API v3** — datos de cuenta
- **Anthropic Claude API** — búsqueda de señales + generación de briefing
- **claude-haiku-4-5** — generación del briefing (rápido y eficiente)
- **web_search tool** — señales externas en tiempo real

## Instalación
```bash
git clone https://github.com/esther-elialo/gtm-engineering-portfolio.git
cd gtm-engineering-portfolio/gtm-intelligence

pip install anthropic requests python-dotenv

cp .env.example .env
# Edita .env con tus tokens
```

## Uso
```python
# Edita la última línea de gtm_intel.py
run_gtm_intel("tudominio.com")

python3 gtm_intel.py
```

## Configuración (.env)
```
HUBSPOT_ACCESS_TOKEN=pat-eu1-...
ANTHROPIC_API_KEY=sk-ant-...
```