from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File, FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import os
from groq import Groq

# ✅ Agents (KEEP YOUR ORIGINAL PIPELINE)
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

# ✅ GROQ CLIENT
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# -----------------------------
# HOME
# -----------------------------
@app.get("/")
def home():
    return {"message": "AI BDR Backend Running 🚀"}

# -----------------------------
# 🔥 MULTI-AGENT BDR SYSTEM (FINAL FIXED)
# -----------------------------
@app.post("/run-bdr-agent")
def run_bdr_agent(file: UploadFile = File(...)):

    try:
        df = pd.read_csv(file.file)
        df.columns = df.columns.str.strip().str.lower()
    except Exception as e:
        return {"error": f"CSV error: {str(e)}"}

    results = []

    for i, row in df.iterrows():

        name = str(row.get("name", "")).strip()
        company = str(row.get("company", "")).strip()
        industry = str(row.get("industry", "")).strip()

        print(f"\n🚀 Processing Row {i+1}: {name} | {company} | {industry}")

        # -----------------------------
        # AGENT PIPELINE (WITH SAFE FALLBACKS)
        # -----------------------------

        # 1️⃣ Research
        try:
            context = research_agent(company, industry)
        except Exception as e:
            print("❌ Research Error:", e)
            context = ""

        # 2️⃣ Enrichment (INSIGHTS)
        try:
            insights = enrichment_agent(company, industry, context)
        except Exception as e:
            print("❌ Enrichment Error:", e)
            insights = ""

        # 3️⃣ Email
        try:
            email = email_agent(name, company, insights)
        except Exception as e:
            print("❌ Email Error:", e)
            email = ""

        # 4️⃣ Score
        try:
            score = scoring_agent(company, industry, insights)
        except Exception as e:
            print("❌ Score Error:", e)
            score = ""

        # -----------------------------
        # ✅ SMART FALLBACKS (IMPORTANT FIX)
        # -----------------------------
        if not insights:
            insights = f"{company} operates in the {industry} industry and may benefit from AI-driven optimization, automation, and growth strategies."

        if not email:
            email = f"""Subject: Unlock AI Opportunities for {company}

Hi {name},

I came across {company} and noticed your work in the {industry} space.

We help companies like yours leverage AI to improve efficiency, automate workflows, and drive growth.

Would you be open to a quick 15-minute discussion to explore this?

Best regards,  
[Your Name]
"""

        if not score:
            score = "60"

        # -----------------------------
        results.append({
            "name": name or "N/A",
            "company": company or "N/A",
            "industry": industry or "N/A",
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

    tone = "gentle reminder" if req.followup_number == 1 else "slightly persuasive"

    prompt = f"""
Write a follow-up email.

Name: {req.name}
Company: {req.company}
Industry: {req.industry}

Previous Email:
{req.previous_email}

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