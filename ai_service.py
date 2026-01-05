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
  - 1-3: Spam or low value (e.g. no contact, general questions)
  - 4-6: Medium value (basic interest)
  - 7-10: High value (specific needs, budget, urgency)
- If information is not available, set to null (except score, which must always be a number).
- Response MUST be EXCLUSIVELY a valid JSON object with no additional text, explanations, or markdown. Do not add ```json or anything else.
- IMPORTANT: All extracted string values (especially summary, product, city) MUST be in the same language as the input text.

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