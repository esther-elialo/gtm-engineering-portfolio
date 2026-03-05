import anthropic
from dotenv import load_dotenv
import os

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "You are a GTM analyst. Given the company name 'Notion', give me 3 reasons why they might be a good ICP fit for a B2B SaaS tool targeting productivity teams. Be concise."
        }
    ]
)

print(message.content[0].text)