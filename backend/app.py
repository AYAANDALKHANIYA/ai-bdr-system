from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File, FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import os
from groq import Groq
import json

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
    return {"message": "Optimized AI BDR Backend Running 🚀"}

# -----------------------------
# 🔥 SINGLE-CALL BDR SYSTEM
# -----------------------------
@app.post("/run-bdr-agent")
def run_bdr_agent(file: UploadFile = File(...)):

    try:
        df = pd.read_csv(file.file)
        df.columns = df.columns.str.strip().str.lower()
    except Exception as e:
        return {"error": f"CSV error: {str(e)}"}

    results = []

    for _, row in df.iterrows():

        name = str(row.get("name", "")).strip()
        company = str(row.get("company", "")).strip()
        industry = str(row.get("industry", "")).strip()

        print(f"🚀 Processing: {name}, {company}")

        prompt = f"""
You are a senior AI Business Development Representative.

Analyze the lead deeply and generate HIGH-QUALITY output.

Lead Details:
- Name: {name}
- Company: {company}
- Industry: {industry}

INSTRUCTIONS:

1. INSIGHTS:
- Give detailed, realistic insights about the company
- Mention possible business model, challenges, opportunities
- Explain WHY they might need AI solutions
- Minimum 4-5 lines

2. EMAIL:
- Write a highly personalized cold email
- Include:
    • Subject line
    • Strong opening (not generic)
    • Clear value proposition
    • Use-case relevant to their industry
    • CTA (call to action)
- Make it sound human, premium, and persuasive
- Minimum 8–10 lines

3. SCORE:
- Give a realistic lead score (0–100)
- Based on potential fit for AI solutions

Return ONLY valid JSON:
{{
    "insights": "...",
    "email": "...",
    "score": "..."
}}
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            content = response.choices[0].message.content

            # ✅ SAFE JSON PARSE
            try:
                parsed = json.loads(content)
            except:
                print("⚠️ JSON parse failed, using fallback")
                parsed = {
                    "insights": "Generated insights unavailable",
                    "email": content,
                    "score": "50"
                }

            results.append({
                "name": name or "N/A",
                "company": company or "N/A",
                "industry": industry or "N/A",
                "insights": parsed.get("insights", ""),
                "email": parsed.get("email", ""),
                "score": parsed.get("score", "0")
            })

        except Exception as e:
            print("❌ API Error:", e)

            results.append({
                "name": name,
                "company": company,
                "industry": industry,
                "insights": "Error generating insights",
                "email": "Error generating email",
                "score": "0"
            })

    return {"results": results}


# -----------------------------
# FOLLOW-UP (UNCHANGED)
# -----------------------------
class FollowupRequest(BaseModel):
    name: str
    company: str
    industry: str
    previous_email: str
    followup_number: int


@app.post("/generate-followup")
def generate_followup(req: FollowupRequest):

    prompt = f"""
Write a follow-up email.

Name: {req.name}
Company: {req.company}
Industry: {req.industry}

Previous Email:
{req.previous_email}

Tone: {"gentle reminder" if req.followup_number == 1 else "persuasive"}

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