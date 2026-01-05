# AI Business Automator

System do automatycznej strukturyzacji leadów sprzedażowych z nieustrukturyzowanych tekstów (maile, wiadomości) przy użyciu AI.

## Funkcjonalności

- **AI-powered ekstrakcja danych**: Wyciąga imię, email, telefon, produkt, budżet, pilność, miasto, podsumowanie.
- **Scoring leadów**: Ocenia wartość leada na skali 1-10 (od spamu do wysokiej wartości).
- **Zapis do bazy**: Automatycznie zapisuje strukturyzowane dane do Supabase (PostgreSQL).
- **REST API**: FastAPI endpoint do przetwarzania tekstów.

## Technologie

- **Backend**: FastAPI (Python)
- **AI**: Groq API (model llama-3.1-8b-instant)
- **Baza danych**: Supabase
- **Walidacja**: Pydantic
- **Zależności**: Zobacz `requirements.txt`

## Instalacja

1. Sklonuj repo:
   ```bash
   git clone https://github.com/Tomalson/ai-business-automator.git
   cd ai-business-automator
   ```

2. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```

3. Skonfiguruj zmienne środowiskowe:
   - Skopiuj `.env.example` do `.env`
   - Wypełnij klucze: `GROQ_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY` (service_role secret)

4. Uruchom aplikację:
   ```bash
   uvicorn main:app --reload
   ```

5. API dostępne na `http://127.0.0.1:8000/docs` (Swagger UI)

## Użycie

Wyślij POST do `/process-lead` z JSON:
```json
{
  "text": "Cześć, jestem Jan Kowalski z Warszawy. Interesuje się oprogramowaniem do automatyzacji sprzedaży. Budżet 10 000 PLN. Tel. 123-456-789. Email: jan@example.com"
}
```

Odpowiedź:
```json
{
  "name": "Jan Kowalski",
  "email": "jan@example.com",
  "phone": "123-456-789",
  "product": "oprogramowanie do automatyzacji sprzedaży",
  "budget_est": "10 000 PLN",
  "urgency": "Wysoka",
  "city": "Warszawa",
  "summary": "Potrzebuję oprogramowania do automatyzacji sprzedaży, pilnie.",
  "score": 9
}
```

## Konfiguracja Supabase

1. Utwórz projekt na [supabase.com](https://supabase.com)
2. W SQL Editor uruchom:
   ```sql
   CREATE TABLE leads (
     id SERIAL PRIMARY KEY,
     name TEXT,
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

## Licencja

MIT License - zobacz [LICENSE](LICENSE)

## Autor

Kacper