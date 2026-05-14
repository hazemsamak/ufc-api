# UFC Events API - Project Instructions

## Project Overview
A production-ready Flask API that scrapes and serves upcoming UFC events. The project features persistent caching, distributed rate limiting, and automated scraping from multiple sources.

### Tech Stack
- **Backend:** Python 3.9+, Flask
- **Data Handling:** BeautifulSoup4, Pandas, Requests
- **Caching & Rate Limiting:** Redis (via Flask-Caching and Flask-Limiter)
- **Documentation:** Flasgger (Swagger/OpenAPI)
- **Production Server:** Gunicorn
- **Containerization:** Docker & Docker Compose

### Architecture
- `src/api.py`: Main entry point, Flask routes, and configuration for caching/rate-limiting.
- `src/scrapers/ufc_scraper.py`: Core logic for scraping UFCStats.com, Wikipedia (for event numbers), and ESPN (for event times).
- `docs/`: Contains OpenAPI specifications (`openapi.json`) and API references.

---

## Building and Running

### Prerequisites
- Docker and Docker Compose (recommended)
- Python 3.9+ (for local development)
- Redis server

### Configuration
Environment variables are managed via `.env`. A template is provided in `.env.example`.
Key variables: `REDIS_HOST`, `REDIS_PORT`, `CACHE_TIMEOUT`, `RATELIMIT_DEFAULT`.

### Running with Docker
```bash
docker-compose up -d --build
```
The API will be accessible at `http://localhost:5010`.

### Local Development
1. Start Redis: `docker-compose up -d ufc-redis`
2. Install dependencies: `pip install -r requirements.txt -r requirements-dev.txt`
3. Run the API: `python src/api.py`

---

## Testing and Quality Assurance

### Automated Testing
Run the test suite using `pytest`:
```bash
pytest tests/test_api_pytest.py
pytest tests/test_scraper_unit.py
```

### Static Analysis & Type Checking
The project uses `mypy` for type checking:
```bash
mypy src/ --config-file tests/mypy.ini
```

### Verification Scripts
- **Rate Limiting:** `python tests/verify_ratelimit.py`
- **Filtering:** `python tests/test_api_filtering.py`

### CI/CD Pipeline
GitHub Actions (`.github/workflows/ci.yml`) automatically performs:
1. Linting and Type Checking (`mypy`).
2. Integration Testing (`pytest` with a Redis service).
3. Docker build verification.

---

## Development Conventions

### Coding Style
- **Type Hinting:** Strictly follow PEP 484 type hints for all function signatures.
- **Documentation:** All API endpoints must include Flasgger docstrings for Swagger UI generation.
- **Imports:** Maintain clear separation between standard library, third-party, and local imports.

### API Standards
- **Versioning:** Endpoints are prefixed with `/api/`.
- **Response Format:** All responses follow a consistent JSON structure:
  ```json
  {
    "status": "success",
    "count": 0,
    "events": []
  }
  ```
- **Error Handling:** Use the standard error structure:
  ```json
  {
    "status": "error",
    "message": "Description of the error"
  }
  ```

### Scraper Best Practices
- **Resilience:** Use `try-except` blocks around network calls and parsing logic.
- **Data Normalization:** Ensure dates and event names are normalized before being served or cached.
- **User Agents:** Always include a realistic `User-Agent` header for scraping (see `ufc_scraper.py`).
