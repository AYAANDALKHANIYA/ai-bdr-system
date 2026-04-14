import os
from groq import Groq

# Load API key from environment
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_response(query, context):
    prompt = f"""
You are an AI Business Development Representative (BDR).

Use the context below to answer the query.

Context:
{context}

Query:
{query}

Answer in a professional and helpful tone.
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",  # fast & powerful
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content