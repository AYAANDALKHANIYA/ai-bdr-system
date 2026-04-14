from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def scoring_agent(company, industry, insights):

    prompt = f"""
You are a sales analyst.

Give:
- Score (0-100)
- Category (Hot/Warm/Cold)
- Reason

Company: {company}
Industry: {industry}

Insights:
{insights}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content