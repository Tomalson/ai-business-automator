# AI Business Automator

System for automatic structuring of sales leads from unstructured texts (emails, messages) using AI.

## Business Value

**Saves up to 10 hours weekly on manual lead transcription.**

## Features

- **AI-powered data extraction**: Extracts name, email, company, phone, product, budget, urgency, city, summary.
- **Lead scoring**: Rates lead value on a scale of 1-10 (from spam to high value).
- **Language consistency**: Output JSON fields (summary, product, city).
- **Database saving**: Automatically saves structured data to Supabase (PostgreSQL).
- **REST API**: FastAPI endpoint for processing texts.
- **Modular prompts**: Niche prompts live in a separate module for easy customization.

## Technologies

- **Backend**: FastAPI (Python)
- **AI**: Groq API (model llama-3.1-8b-instant)
- **Database**: Supabase
- **Validation**: Pydantic
- **Dependencies**: See `requirements.txt`

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/Tomalson/ai-business-automator.git
   cd ai-business-automator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Fill in keys: `GROQ_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY` (service_role secret)

4. Run the application:
   ```bash
   python -m uvicorn main:app --reload
   ```

5. API available at `http://127.0.0.1:8000/docs` (Swagger UI)

## Usage

Send POST to `/process-lead` with JSON:
```json
{
  "text": "Hi, I'm Jan Kowalski from Warsaw. Interested in sales automation software. Budget 10,000 PLN. Phone: 123-456-789. Email: jan@example.com"
}
```

Response:
```json
{
  
  "name": "Jan Kowalski",
  "email": "jan@example.com",
  "phone": "123-456-789",
  "product": "sales automation software",
  "budget_est": "10 000 PLN",
  "urgency": "High",
  "city": "Warsaw",
  "summary": "I need sales automation software urgently.",
  "score": 9
}
```

## Project Structure

- [ai_service.py](ai_service.py): Core AI processing (routing, calling Groq, JSON parsing, profanity handling).
- [prompts.py](prompts.py): Centralized niche prompt templates used by `AIService`.
- [database.py](database.py): Supabase persistence.
- [main.py](main.py): FastAPI app and routes.

## Custom Niches (prompts)

You can add or modify niche prompts in [prompts.py](prompts.py). Each niche is a key in the `PROMPTS` dictionary mapped to a multi-line string template. For example:

```python
# prompts.py
PROMPTS = {
   "PHOTOVOLTAIC & HEAT PUMP COMPANY": """
ROLE: Senior Sales Qualifier for a PHOTOVOLTAIC & HEAT PUMP COMPANY.
... (rules, scoring, extraction) ...
""",

   "AIR CONDITIONING & VENTILATION RECOVERY COMPANY.": """
ROLE: Senior Sales Qualifier for an AIR CONDITIONING & VENTILATION RECOVERY COMPANY.
... (rules, scoring, extraction) ...
""",

   # Add your own niche:
   "my_custom_niche": """
ROLE: Senior Sales Qualifier for <YOUR NICHE>.
Define ambiguity handler, profanity handling, scoring matrix, and extraction rules.
Return ONLY valid JSON with keys: name, company, email, phone, product, budget_est, urgency, city, summary, score.
""",
}
```

`AIService` automatically routes generic input to the best-matching niche where possible (e.g., HVAC keywords). You can still pass an explicit niche via dedicated methods if you extend the API.

## Example Prompts Template

For convenience, see [prompts.example.py](prompts.example.py) — copy it to [prompts.py](prompts.py) and edit keys and content to fit your business. The examples are neutral and generic (e.g., e-commerce, SaaS, home renovation) to serve as starting points; they are not tied to our PV/HVAC niches. This keeps the main service logic clean while letting you iterate on prompt content.

## Example

**Input text (messy):**
```
Cześć, jestem Jan Kowalski z Warszawy. Interesuje się oprogramowaniem do automatyzacji sprzedaży. Budżet 10 000 PLN. Tel. 123-456-789. Email: jan@example.com
```

**Output (clean JSON):**
```json
{
  "name": "Jan Kowalski",
  "email": "jan@example.com",
  "phone": "123-456-789",
  "product": "oprogramowanie do automatyzacji sprzedaży",
  "budget_est": "10 000 PLN",
  "urgency": "High",
  "city": "Warszawa",
  "summary": "Klient z Warszawy zainteresowany oprogramowaniem do automatyzacji sprzedaży.",
  "score": 9
}
```

## Supabase Configuration

1. Create a project on [supabase.com](https://supabase.com)
2. In SQL Editor run:
   ```sql
   CREATE TABLE leads (
     id SERIAL PRIMARY KEY,
     name TEXT,
     company TEXT,
     email TEXT,
     phone TEXT,
     product TEXT,
     budget_est TEXT,
     urgency TEXT,
     city TEXT,
     summary TEXT,
     score INTEGER
   );
   ```

## License

MIT License - see [LICENSE](LICENSE)

## Author

Kacper