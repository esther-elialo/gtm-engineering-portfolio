# Lead Enrichment Agent — HubSpot + Claude

Agente que conecta con HubSpot CRM, extrae contactos y empresas, y genera automáticamente un ICP score con justificación y next action usando Claude (Anthropic).

## ¿Qué problema resuelve?

Un AE con 200 cuentas en el CRM no puede analizar manualmente cada una. Este agente lo hace en segundos: lee los datos de HubSpot, evalúa el encaje con el ICP y devuelve una acción concreta para cada lead.

## Output de ejemplo
```
🔍 LEAD ENRICHMENT AGENT

🏢 COMPANIES
➤ Typeform — typeform.com
ICP Score: 8/10
Razón: B2B SaaS con 400 empleados, encaja perfectamente en rango objetivo.
Next action: Contactar VP Marketing con mensaje personalizado sobre funnel de captación.

➤ Factorial HR — factorialhr.com  
ICP Score: 7/10
Razón: SaaS de 200 empleados en fase de hipercrecimiento, decisor en ventas/marketing.
Next action: Identificar Head of Growth en LinkedIn y contactar enfocando en escalar GTM.
```

## Stack

- **Python 3.9+**
- **HubSpot CRM API v3** — lectura de contactos y empresas
- **Anthropic Claude API** — análisis ICP y generación de next actions
- **python-dotenv** — gestión de credenciales

## Arquitectura
```
HubSpot CRM
    ↓
get_contacts() / get_companies()   ← CRM API v3
    ↓
analyze_lead()                     ← Claude (claude-opus-4-6)
    ↓
ICP Score + Razón + Next Action
```

## Instalación
```bash
# 1. Clona el repositorio
git clone https://github.com/esther-elialo/gtm-engineering-portfolio.git
cd gtm-engineering-portfolio/hubspot-integration

# 2. Instala dependencias
pip install anthropic requests python-dotenv

# 3. Configura credenciales
cp .env.example .env
# Edita .env con tus tokens

# 4. Ejecuta
python3 lead_enrichment_agent.py
```

## Configuración (.env)
```
HUBSPOT_ACCESS_TOKEN=pat-eu1-...   # Token de Private App en HubSpot
ANTHROPIC_API_KEY=sk-ant-...       # API key de Anthropic
```

## ICP target configurado

- Empresas B2B SaaS
- Decisores de ventas o marketing
- 50–500 empleados

Edita el prompt en `analyze_lead()` para adaptar el ICP a tu caso de uso.

## Archivos

| Archivo | Descripción |
|---|---|
| `lead_enrichment_agent.py` | Agente principal |
| `hubspot_test.py` | Script de verificación de conexión |
| `.env.example` | Plantilla de variables de entorno |