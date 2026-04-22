from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File, FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import os
import time
from groq import Groq

# ✅ Agents
from agents.research_agent import research_agent
from agents.enrichment_agent import enrichment_agent
from agents.email_agent import email_agent
from agents.scoring_agent import scoring_agent

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    return {"message": "AI BDR Backend Running 🚀"}

# -----------------------------
# 🔥 MULTI-AGENT BDR SYSTEM
# -----------------------------
@app.post("/run-bdr-agent")
def run_bdr_agent(file: UploadFile = File(...)):

    try:
        df = pd.read_csv(file.file)
        df.columns = df.columns.str.strip().str.lower()
    except Exception as e:
        return {"error": f"CSV read error: {str(e)}"}

    results = []

    for idx, row in df.iterrows():

        try:
            name = str(row.get("name", "")).strip()
            company = str(row.get("company", "")).strip()
            industry = str(row.get("industry", "")).strip()

            print(f"\n🔍 Processing Row {idx+1}: {name} | {company} | {industry}")

            # -----------------------------
            # 1️⃣ RESEARCH AGENT
            # -----------------------------
            try:
                context = research_agent(company, industry)
                if not context:
                    context = "Basic company context not available"
            except Exception as e:
                print("❌ Research Error:", e)
                context = "Basic company context not available"

            # -----------------------------
            # 2️⃣ ENRICHMENT AGENT
            # -----------------------------
            try:
                insights = enrichment_agent(company, industry, context)
                if not insights:
                    insights = f"{company} operates in the {industry} industry with potential growth opportunities."
            except Exception as e:
                print("❌ Enrichment Error:", e)
                insights = f"{company} operates in the {industry} industry with potential growth opportunities."

            # -----------------------------
            # 3️⃣ EMAIL AGENT
            # -----------------------------
            try:
                email = email_agent(name, company, insights)
                if not email:
                    email = f"Hi {name},\n\nI came across {company} and wanted to connect regarding potential collaboration opportunities.\n\nBest regards."
            except Exception as e:
                print("❌ Email Error:", e)
                email = f"Hi {name},\n\nI came across {company} and wanted to connect regarding potential collaboration opportunities.\n\nBest regards."

            # -----------------------------
            # 4️⃣ SCORING AGENT
            # -----------------------------
            try:
                score = scoring_agent(company, industry, insights)
                if not score:
                    score = 50
            except Exception as e:
                print("❌ Scoring Error:", e)
                score = 50

            # -----------------------------
            # FINAL RESULT
            # -----------------------------
            results.append({
                "name": name or "N/A",
                "company": company or "N/A",
                "industry": industry or "N/A",
                "insights": insights,
                "email": email,
                "score": score
            })

            # 🔥 IMPORTANT: Prevent API overload
            time.sleep(0.7)

        except Exception as e:
            print("❌ Row Processing Error:", e)

            results.append({
                "name": "Error",
                "company": "Error",
                "industry": "Error",
                "insights": "Error occurred",
                "email": "Error occurred",
                "score": 0
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

    context = f"{req.company} operates in the {req.industry} industry."
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

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        return {"followup_email": response.choices[0].message.content}

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# DOWNLOAD CSV OUTPUT
# -----------------------------
@app.post("/download-emails")
def download_emails(file: UploadFile = File(...)):

    try:
        df = pd.read_csv(file.file)
        df.columns = df.columns.str.strip().str.lower()
    except Exception as e:
        return {"error": f"CSV read error: {str(e)}"}

    output_data = []

    for _, row in df.iterrows():

        try:
            name = str(row.get("name", "")).strip()
            company = str(row.get("company", "")).strip()
            industry = str(row.get("industry", "")).strip()

            context = research_agent(company, industry) or ""
            insights = enrichment_agent(company, industry, context) or ""
            email = email_agent(name, company, insights) or "No email generated"

            output_data.append({
                "name": name,
                "company": company,
                "industry": industry,
                "email": email
            })

            time.sleep(0.5)

        except Exception as e:
            print("❌ Download Error:", e)

    output_file = "output_emails.csv"
    pd.DataFrame(output_data).to_csv(output_file, index=False)

    return FileResponse(
        path=output_file,
        filename="generated_emails.csv",
        media_type='text/csv'
    )