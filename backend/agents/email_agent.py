from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def email_agent(name, company, insights):
    prompt = f"""
Write a professional cold email.

Name: {name}
Company: {company}
Insights: {insights}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content