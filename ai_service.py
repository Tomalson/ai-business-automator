import os
import logging
import time
from groq import Groq
from schemas import Lead
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-8b-instant"  # Updated to current available Groq model


    def process_lead_text(self, text: str) -> Lead:
        prompt = f"""
        ROLE: Senior Sales Qualifier for a PHOTOVOLTAIC & HEAT PUMP COMPANY.
        
        YOUR MISSION:
        Qualify leads for Solar Panels (Fotowoltaika) and Heat Pumps.
        Your goal is NOT to reject potential customers, but to categorize them.
        
        ### 1. AMBIGUITY HANDLER (CRITICAL):
        - If user writes "panele" (panels) AND mentions "dach" (roof), "słońce" (sun), "prąd" (electricity) -> IT IS PHOTOVOLTAIC. -> PASS.
        - If user writes "panele" without context -> Check if it could be floor panels. If unsure but likely solar or pump -> PASS with Score 3.
        - If user writes "pompa" (pump) AND mentions "ciepła" (heat), "dom" (house), "ogrzewanie" (heating) -> IT IS HEAT PUMP. -> PASS.
        - If user writes "pompa" without context -> Check if it could be water pump. If unsure but likely heat pump -> PASS with Score 3.
        - "Ile za..." (How much for...) is a VALID BUYING INTENT. Do NOT reject it as spam.

        ### 2. SCORING MATRIX:
        
        * SCORE 1 (TRASH / OFF-TOPIC):
          - Explicitly wrong industry: "Naprawa pralki", "Układanie paneli podłogowych", "Sprzedam Opla".
          - Spam/Ads/Job seekers.
          
        * SCORE 3-4 (VALID BUT VAGUE):
          - Matches our industry (Solar/Heating) but lacks details.
          - Examples: "Ile za panele na dachu?", "Chcę fotowoltaikę", "Cennik pomp ciepła".
          - ACTION: Valid Lead. Save to DB.
          
        * SCORE 5-7 (SOLID):
          - Industry match + Contact info.
          - SCORE 5: Basic specifics provided.
          - SCORE 6-7: HIGH DETAIL (Location + Bill amount + System size/Power). Example: "Lodz, 450zl bill, 6kWp".
          
        * SCORE 10 (GOLDEN):
          - Industry match + "Unlimited budget" / "Commercial/Hala" / "Urgent".

        ### 3. EXTRACTION RULES:
        - Extract ALL available details into the JSON fields:
          * `name`: Full name of the sender.
          * `company`: Name of the company if B2B.
          * `email`: Extract email address.
          * `phone`: Extract phone number.
          * `city`: City or location mentioned.
          * `budget_est`: Estimated budget or "Unlimited" if stated.
          * `urgency`: "High" (ASAP), "Medium", or "Low".
          * `product`: Classify as "Fotowoltaika", "Pompy Ciepła", "Fotowoltaika i/lub Pompy Ciepła" or "Inne".
          * `summary`: A short summary of the inquiry. 
        - If any field is missing, set it to null in JSON.
        INPUT TEXT:
        "{text}"
        the output must be a valid JSON matching the Lead schema. 
        Ensure the summary is in polish with correct grammar (e.g. "Paneli fotowoltaicznych" instead of "Paneli fotowoltajnych") ect.
        OUTPUT JSON:
        """

        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Processing lead text, attempt {attempt + 1}")
                response = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Jesteś pomocnym asystentem, który zawsze zwraca prawidłowy JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    model=self.model,
                    temperature=0.1,  # Niska temperatura dla spójności
                    max_tokens=500
                )
                raw_content = response.choices[0].message.content.strip()
                # Remove possible markdown ```json
                if raw_content.startswith("```json"):
                    raw_content = raw_content[7:]
                if raw_content.endswith("```"):
                    raw_content = raw_content[:-3]
                raw_content = raw_content.strip()
                
                # Try to find JSON object if extra text exists
                json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)
                if json_match:
                    raw_content = json_match.group(0)

                data = json.loads(raw_content)
                # Validate with Pydantic
                lead = Lead(**data)
                logger.info("Successfully processed lead")
                return lead
            except Exception as e:
                logger.error(f"Error during AI processing on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait before retry
                else:
                    logger.error("All retries failed, returning manual verification lead")
                    # Return a lead indicating manual verification needed
                    return Lead(
                        name=None,
                        company=None,
                        email=None,
                        phone=None,
                        product=None,
                        budget_est=None,
                        urgency=None,
                        city=None,
                        summary="Requires manual verification - AI processing failed",
                        score=1
                    )
