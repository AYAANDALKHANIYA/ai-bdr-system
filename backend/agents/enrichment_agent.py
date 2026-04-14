from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def enrichment_agent(company, industry, context):

    prompt = f"""
You are a business analyst.

Analyze the company and provide:
- What they do
- Pain points
- AI automation opportunities

Company: {company}
Industry: {industry}

Context:
{context}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content