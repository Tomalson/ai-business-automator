import os
import logging
import time
from groq import Groq
from schemas import Lead
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-8b-instant"  # Updated to current available Groq model

    def process_lead_text(self, text: str) -> Lead:
        prompt = f"""
You are an expert in sales lead analysis. Your task is to process unstructured text from an email or message into structured JSON data.

Instructions:
- Extract the following information: name (full name), email, phone (phone number), product (product/service), budget_est (estimated budget as string, e.g. '10000 PLN'), urgency (High/Medium/Low), city, summary (brief summary).
- Rate the lead value on a scale of 1-10 (score), where:
- SCORE 1-2 (REJECT): Spam, irrelevant services, bot messages, seeking for free samples or job applications. 
  * EXAMPLE: "Naprawa pralki Frania", "Pozycjonowanie stron", "Szukam pracy jako kierowca", "Szukam darmowych próbek".
- SCORE 3-4 (VAGUE): No contact info, no specific product, just "how much?" or general curiosity.
- SCORE 5-6 (VALID): Real customer, specific product mentioned, contact info provided (email or phone). No urgency.
- SCORE 7-8 (HOT): High intent. Mentions specific location, deadline (e.g., "next week"), and provides a valid phone number.
- SCORE 9-10 (ELITE): 
  * MANDATORY 10: If customer mentions "Unlimited budget", "Money is no object", "Płacę gotówką bez limitu", "Budget: Unlimited", OR is a "Large Corporate Client" with ASAP urgency.
- If information is not available, set to null (except score, which must always be a number).
- Response MUST be EXCLUSIVELY a valid JSON object with no additional text, explanations, or markdown. Do not add ```json or anything else.
- IMPORTANT: All extracted string values (especially summary, product, city) MUST be in the same language as the input text.
 LOGIC RULES:
    1. BUDGET: If the customer says "budget is no object", "unlimited", "money is not an issue", or similar, set budget_est to "Unlimited / High Priority" (in the same language as the input text). Only use null if there is absolutely no mention of money. If customer asks for a free sample, or similar set budget_est to "Free" (in the same language as the input text)
    2. URGENCY: If the customer indicates a time frame (e.g., "need it by next week", "as soon as possible"), set urgency to High. If they mention a month or longer, set to Medium. If no time frame is mentioned, set to Low.

Text to analyze:
{text}

JSON Response:
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
                
                data = json.loads(raw_content)
                # Validate with Pydantic
                lead = Lead(**data)
                logger.info("Successfully processed lead")
                return lead
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON response on attempt {attempt + 1}: {e}")
            except Exception as e:
                logger.error(f"Error during AI processing on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait before retry
                else:
                    logger.error("All retries failed, returning manual verification lead")
                    # Return a lead indicating manual verification needed
                    return Lead(
                        name=None,
                        email=None,
                        phone=None,
                        product=None,
                        budget_est=None,
                        urgency=None,
                        city=None,
                        summary="Requires manual verification - AI processing failed",
                        score=1
                    )