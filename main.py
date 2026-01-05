from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import LeadInput, Lead
from ai_service import AIService
from database import DatabaseService
import os
from dotenv import load_dotenv

load_dotenv()  # Ładuje zmienne z .env

app = FastAPI(title="AI Business Automator", description="System for automatic sales lead structuring")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = AIService()
db_service = DatabaseService()

@app.post("/process-lead", response_model=Lead)
async def process_lead(input_data: LeadInput):
    try:
        # Przetwórz tekst przez AI
        lead = ai_service.process_lead_text(input_data.text)
        
        # Zapisz do bazy
        db_result = db_service.insert_lead(lead)
        
        return lead
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wewnętrzny błąd serwera: {str(e)}")

@app.get("/")
async def root():
    return {"message": "AI Business Automator API is running"}