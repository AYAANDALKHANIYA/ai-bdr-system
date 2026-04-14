from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os
from groq import Groq

from rag.rag_pipeline import create_vector_store, query_vector_store

# ✅ Agents
from agents.research_agent import research_agent
from agents.enrichment_agent import enrichment_agent
from agents.email_agent import email_agent
from agents.scoring_agent import scoring_agent

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# GROQ CLIENT
# -----------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# -----------------------------
# HOME
# -----------------------------
@app.get("/")
def home():
    return {"message": "RAG API Running"}


# -----------------------------
# CREATE VECTOR DB
# -----------------------------
@app.get("/create-db")
def create_db():
    create_vector_store()
    return {"message": "Vector DB created successfully"}


# -----------------------------
# ASK (RAG QA)
# -----------------------------
class QueryRequest(BaseModel):
    query: str


@app.post("/ask")
def ask(request: QueryRequest):
    answer = query_vector_store(request.query)
    return {"response": answer}


# -----------------------------
# 🔥 MULTI-AGENT BDR SYSTEM
# -----------------------------
@app.post("/run-bdr-agent")
def run_bdr_agent(file: UploadFile = File(...)):

    # ✅ Read uploaded CSV
    df = pd.read_csv(file.file)

    results = []

    # ✅ Loop through each lead
    for _, row in df.iterrows():

        name = row["name"]
        company = row["company"]
        industry = row["industry"]

        # 1️⃣ Research Agent
        context = research_agent(company, industry)

        # 2️⃣ Enrichment Agent
        insights = enrichment_agent(company, industry, context)

        # 3️⃣ Email Agent
        email = email_agent(name, company, insights)

        # 4️⃣ Scoring Agent
        score = scoring_agent(company, industry, insights)

        results.append({
            "name": name,
            "company": company,
            "industry": industry,
            "insights": insights,
            "email": email,
            "score": score
        })

    return {"results": results}


# -----------------------------
# FOLLOW-UP
# -----------------------------
class FollowupRequest(BaseModel):
    name: str
    company: str
    industry: str
    previous_email: str
    followup_number: int


@app.post("/generate-followup")
def generate_followup(req: FollowupRequest):

    context = query_vector_store(
        f"Tell me about {req.company} in {req.industry}"
    )

    tone = "gentle reminder" if req.followup_number == 1 else "slightly persuasive"

    prompt = f"""
Write a follow-up email.

Name: {req.name}
Company: {req.company}

Previous Email:
{req.previous_email}

Context:
{context}

Tone: {tone}

Include Subject + Body
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return {"followup_email": response.choices[0].message.content}


# -----------------------------
# DOWNLOAD CSV OUTPUT
# -----------------------------
@app.post("/download-emails")
def download_emails(file: UploadFile = File(...)):

    df = pd.read_csv(file.file)
    output_data = []

    for _, row in df.iterrows():

        context = research_agent(row["company"], row["industry"])
        insights = enrichment_agent(row["company"], row["industry"], context)
        email = email_agent(row["name"], row["company"], insights)

        output_data.append({
            "name": row["name"],
            "company": row["company"],
            "industry": row["industry"],
            "email": email
        })

    output_file = "output_emails.csv"
    pd.DataFrame(output_data).to_csv(output_file, index=False)

    return FileResponse(
        path=output_file,
        filename="generated_emails.csv",
        media_type='text/csv'
    )