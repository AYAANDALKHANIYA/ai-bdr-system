from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def research_agent(company, industry):
    prompt = f"Give short business research about {company} in {industry} industry."

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content