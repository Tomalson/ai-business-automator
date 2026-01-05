import os
from groq import Groq
from schemas import Lead
import json

class AIService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-8b-instant"  # Updated to current available Groq model

    def process_lead_text(self, text: str) -> Lead:
        prompt = f"""
Jesteś ekspertem w analizie leadów sprzedażowych. Twoim zadaniem jest przetworzenie nieustrukturyzowanego tekstu z maila lub wiadomości na strukturyzowane dane JSON.

Instrukcje:
- Wyciągnij następujące informacje: name (imię i nazwisko), email, phone (numer telefonu), product (produkt/usługa), budget_est (szacunkowy budżet jako string, np. '10000 PLN'), urgency (pilność: Wysoka/Średnia/Niska), city (miasto), summary (krótkie podsumowanie).
- Oceń wartość leada na skali 1-10 (score), gdzie:
  - 1-3: Spam lub niskiej wartości (np. brak kontaktu, ogólne pytania)
  - 4-6: Średnia wartość (podstawowe zainteresowanie)
  - 7-10: Wysoka wartość (konkretne potrzeby, budżet, pilność)
- Jeśli informacje nie są dostępne, ustaw na null (oprócz score, który zawsze musi być liczbą).
- Odpowiedź MUSI być WYŁĄCZNIE prawidłowym obiektem JSON bez żadnego dodatkowego tekstu, wyjaśnień lub markdown. Nie dodawaj ```json ani niczego innego.

Tekst do analizy:
{text}

Odpowiedź JSON:
"""

        try:
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
            # Usuń ewentualne markdown ```json
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:]
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3]
            raw_content = raw_content.strip()
            
            data = json.loads(raw_content)
            # Walidacja z Pydantic
            lead = Lead(**data)
            return lead
        except Exception as e:
            raise ValueError(f"Błąd podczas przetwarzania przez AI: {str(e)}")