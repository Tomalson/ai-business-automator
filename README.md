# AI Business Automator

[![Tests CI](https://github.com/Tomalson/ai-business-automator/actions/workflows/tests.yml/badge.svg)](https://github.com/Tomalson/ai-business-automator/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/Tomalson/ai-business-automator/branch/main/graph/badge.svg)](https://codecov.io/gh/Tomalson/ai-business-automator)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://hub.docker.com/)

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

### Option 1: Local Installation

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

### Option 2: Docker Installation

1. Make sure you have [Docker](https://www.docker.com/products/docker-desktop) installed

2. Build the Docker image:
   ```bash
   docker build -t ai-business-automator .
   ```

3. Run the container:
   ```bash
   docker run -p 8000:8000 \
     -e GROQ_API_KEY="your-groq-key" \
     -e SUPABASE_URL="your-supabase-url" \
     -e SUPABASE_KEY="your-supabase-key" \
     ai-business-automator
   ```

4. API available at `http://localhost:8000/docs` (Swagger UI)

**Using Docker Compose (recommended):**

Create a `.env` file with your keys, then:
   ```bash
   docker-compose up
   ```

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

```
ai-business-automator/
├── main.py                    # FastAPI application & routes
├── ai_service.py              # AI processing logic (Groq integration)
├── database.py                # Supabase database service
├── schemas.py                 # Pydantic models for validation
├── prompts.example.py         # Example niche prompts
│
├── Dockerfile                 # Multi-stage production image
├── docker-compose.yml         # Local development setup
├── .dockerignore               # Docker build optimization
│
├── test_main.py               # API endpoint tests
├── test_services.py           # AI & Database service tests
├── pytest.ini                 # Pytest configuration
│
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
│
├── README.md                  # This file
├── CONTRIBUTING.md            # Contribution guidelines
├── CHANGELOG.md               # Version history
├── LICENSE                    # MIT License
│
└── .github/
    └── workflows/
        └── tests.yml          # GitHub Actions CI/CD
```

### Key Files

- [ai_service.py](ai_service.py): Core AI processing (routing, calling Groq, JSON parsing, profanity handling).
- [prompts.py](prompts.py): Centralized niche prompt templates used by `AIService`.
- [database.py](database.py): Supabase persistence.
- [main.py](main.py): FastAPI app and routes.
- [test_main.py](test_main.py): Endpoint tests (12 tests)
- [test_services.py](test_services.py): Service tests (5 tests)

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

## Testing

### Run Tests Locally

Install test dependencies (included in `requirements.txt`):
```bash
pytest test_main.py test_services.py -v
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html  # or use 'start htmlcov/index.html' on Windows
```

### Test Structure

- **test_main.py**: Tests for FastAPI endpoints (`/process-lead`, `/`)
- **test_services.py**: Tests for AIService and DatabaseService

### Run Tests in Docker

```bash
docker run --rm ai-business-automator pytest test_main.py test_services.py -v
```

## Docker Architecture

The `Dockerfile` uses a **multi-stage build** for efficiency:

1. **Builder stage**: Compiles dependencies (smaller final image)
2. **Production stage**: Contains only runtime requirements

### Key Features:

- ✅ **Minimal image size**: ~200MB (Python 3.11 slim + dependencies)
- ✅ **Non-root user**: Runs as `appuser` (UID 1000) for security
- ✅ **Health check**: Monitors container availability every 30s
- ✅ **CORS enabled**: Pre-configured for cross-origin requests
- ✅ **Environment variables**: Easy configuration via `-e` flags

### Docker Image Details

```dockerfile
# Multi-stage build reduces final image size
# Stage 1: Install dependencies
# Stage 2: Copy only necessary files for production
CI/CD Pipeline

Automated testing on every push/PR:
- ✅ **Linting** with flake8
- ✅ **Unit tests** with pytest
- ✅ **Coverage tracking** with Codecov
- ✅ **Docker build** verification

See [.github/workflows/tests.yml](.github/workflows/tests.yml) for details.

## Performance Metrics

| Metric | Value |
|--------|-------|
| Image Size | ~200MB |
| Python Version | 3.11 |
| Test Coverage | 80%+ |
| API Response Time | <500ms (Groq dependent) |
| Security | Non-root user, health checks |

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

### Quick Start for Contributors

```bash
git clone https://github.com/Tomalson/ai-business-automator.git
cd ai-business-automator
pip install -r requirements.txt
pytest -v
```

## Roadmap

- [ ] GraphQL API support
- [ ] Advanced lead segmentation
- [ ] Webhook integrations
- [ ] Rate limiting & API keys
- [ ] Admin dashboard
- [ ] Multi-language support

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT License - see [LICENSE](LICENSE)

## Author

**Kacper** - [GitHub](https://github.com/Tomalson)

## Support

- 📧 Issues & Questions: [GitHub Issues](https://github.com/Tomalson/ai-business-automator/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Tomalson/ai-business-automator/discussions)ker-compose.yml (Optional)

Create this file for easier local development:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
```

Then run: `docker-compose up`

## License

MIT License - see [LICENSE](LICENSE)

## Author

Kacper