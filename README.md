# AI Business Automator

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

System for automatic structuring of sales leads from unstructured texts (emails, messages) using AI.

## Features

- AI-powered data extraction from raw lead text
- Lead scoring on a 1-10 scale
- Consistent structured JSON output
- Automatic saving to Supabase
- FastAPI REST API endpoint for lead processing
- Prompt templates isolated in a dedicated module

## Tech Stack

- Backend: FastAPI (Python)
- AI: Groq API (model llama-3.1-8b-instant)
- Database: Supabase
- Validation: Pydantic

## Installation

1. Clone repository:

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
- Fill in `GROQ_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`

4. Start API:

```bash
python -m uvicorn main:app --reload
```

5. Open docs at `http://127.0.0.1:8000/docs`

## Usage

Send POST to `/process-lead` with JSON:

```json
{
  "text": "Hi, I'm Jan Kowalski from Warsaw. Interested in sales automation software. Budget 10,000 PLN. Phone: 123-456-789. Email: jan@example.com"
}
```

Example response:

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

```text
ai-business-automator/
├── main.py
├── ai_service.py
├── database.py
├── schemas.py
├── prompts.py
├── prompts.example.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── CONTRIBUTING.md
└── CHANGELOG.md
```

## Custom Prompts

You can add or modify niche prompt templates in `prompts.py`. Each niche is a key in `PROMPTS` with a dedicated instruction template.

## Supabase Setup

Create a `leads` table, for example:

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

## Contributing

Contribution process is described in `CONTRIBUTING.md`.

## License

MIT License.
