# UFC Events API

A production-ready Flask API that scrapes and serves upcoming UFC events with persistent caching and rate limiting.

## Project Structure

```
UFC/
├── .github/workflows/  # CI/CD Pipeline (GitHub Actions)
├── docs/               # API Reference and OpenAPI Spec
├── src/
│   ├── api.py              # Main Flask API / WSGI entry point
│   └── scrapers/
│       └── ufc_scraper.py  # Multi-source scraper (UFCStats + Wikipedia)
├── tests/
│   ├── test_scraper_unit.py # Unit tests with mocking
│   ├── test_api_pytest.py  # API integration tests
│   ├── verify_ratelimit.py # Rate limit verification script
│   └── test_api_filtering.py # Filtering verification script
├── Dockerfile              # Production container config
├── docker-compose.yml     # Multi-container orchestration (API + Redis)
├── requirements.txt        # Production dependencies
└── README.md              # Project documentation
```

## Features

- **Automated Scraping:** Fetches live data from UFCStats.com and Wikipedia for event numbers.
- **Persistent Caching:** Uses **Redis** to cache scraped data for 12 hours, ensuring < 20ms response times.
- **Distributed Rate Limiting:** Protects the API using `Flask-Limiter` with a Redis backend (Default: 200/day, 50/hour).
- **Advanced Filtering:** Search events by `type` (exact) or `search` (substring) across name and location.
- **Production Ready:** Pre-configured for **Gunicorn** in Docker with optimized worker/thread settings.
- **Interactive documentation:** Swagger UI available for live endpoint testing.

## Configuration

The application uses environment variables. Copy the template to start:
```bash
cp .env.example .env
```

| Variable | Description | Default |
| :--- | :--- | :--- |
| `REDIS_HOST` | Redis server hostname | `redis` (Docker) / `localhost` (Local) |
| `REDIS_PORT` | Redis server port | `6379` |
| `RATELIMIT_DEFAULT`| Default rate limit rules | `"200 per day;50 per hour"` |
| `API_EXTERNAL_PORT`| Public port for the API | `5010` |
| `CACHE_TIMEOUT` | Cache duration in seconds | `43200` (12 hours) |

---

## Getting Started

### 1. Docker Deployment (Recommended)
This starts the API and the Redis dependency in a single command.
```bash
docker-compose up -d --build
```
Access the API at `http://localhost:5010`.

### 2. Local Development (Manual)
To run the code directly on your machine while using the Dockerized Redis:
1. **Start Redis only:** `docker-compose up -d redis`
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Run API:** `python src/api.py`

---

## API Reference

### Swagger UI
Test the endpoints interactively: `http://localhost:5000/apidocs` (or `5010` if via Docker).

### Endpoints
- `GET /api/events`: Basic name, date, and type info.
- `GET /api/events/full`: Includes full metadata (location, record).
- `GET /api/health`: System health status.

### Filtering & Search
All event endpoints support the following query parameters:
- `type`: Exact match for event type (`UFC` or `UFC Fight Night`).
- `search`: Substring search in event name or location.

**Examples:**
- `GET /api/events?type=UFC` (Numbered events only)
- `GET /api/events/full?search=Vegas` (Events in Las Vegas)

---

## Testing & Verification
- **Unit Tests:** `pytest tests/test_scraper_unit.py`
- **Rate Limit Test:** `python tests/verify_ratelimit.py`
- **Filtering Test:** `python tests/test_api_filtering.py`
