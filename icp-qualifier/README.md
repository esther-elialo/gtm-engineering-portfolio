# ICP Qualification Agent

An AI-powered agent that evaluates companies against your Ideal Customer Profile and returns structured qualification scores with actionable recommendations.

## What it does

- Scores companies across 4 ICP dimensions (size, tech stack, growth signals, pain point alignment)
- Returns structured JSON output ready for CRM integration
- Generates a personalized outreach hook for each qualified account
- Recommends action: Prioritize / Nurture / Deprioritize

## Stack

- Python 3.9+
- Anthropic Claude API (claude-opus-4-5)
- Input: company name + optional context string
- Output: structured JSON

## Setup
```bash
pip3 install anthropic python-dotenv
```

Create a `.env` file:
```
ANTHROPIC_API_KEY=your_key_here
```

## Usage
```bash
python3 icp_qualifier.py
```

## Example Output
```json
{
  "company": "Linear",
  "overall_score": 7,
  "recommended_action": "Prioritize",
  "suggested_hook": "Saw you just shipped the Figma integration—curious how you're thinking about [your value prop] as you scale the integrations ecosystem?"
}
```

## Why this matters

Manual ICP qualification is one of the biggest time sinks in outbound sales. This agent lets an AE qualify 50 accounts in the time it takes to manually research 5.

## Roadmap

- Add web scraping to pull live signals automatically
- HubSpot integration to push scores directly to contact records
- Batch processing for list qualification