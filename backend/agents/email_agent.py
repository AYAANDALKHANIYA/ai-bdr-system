from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def email_agent(name, company, insights):

    prompt = f"""
You are a BDR expert.

Write a cold email.

Lead:
Name: {name}
Company: {company}

Insights:
{insights}

Rules:
- Subject + Body
- Short (100-120 words)
- Persuasive
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content