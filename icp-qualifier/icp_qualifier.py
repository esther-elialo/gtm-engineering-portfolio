import anthropic
from dotenv import load_dotenv
import os

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert GTM analyst specializing in ICP (Ideal Customer Profile) qualification.

Your job is to evaluate whether a company is a strong ICP fit based on the information provided.

You will score companies on a scale of 1-10 across these dimensions:
- Company Size Fit (headcount and revenue stage)
- Tech Stack Signals (do they use modern/complementary tools?)
- Growth Signals (hiring, funding, expansion)
- Pain Point Alignment (do they likely have the problems we solve?)

Output format - always respond in this exact JSON structure:
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


def qualify_company(company_name: str, context: str = "") -> str:
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
    return message.content[0].text


if __name__ == "__main__":
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

    for company in test_companies:
        print(f"\n{'='*50}")
        print(f"Evaluating: {company['name']}")
        print('='*50)
        result = qualify_company(company["name"], company["context"])
        print(result)