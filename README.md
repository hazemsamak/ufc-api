# UFC Events API

A simple Flask API to scrape and return upcoming UFC events and dates.

## Project Structure

```
UFC/
├── .github/workflows/  # CI/CD Pipeline configuration
├── docs/               # API Reference and OpenAPI Spec
├── src/
│   ├── api.py              # Main Flask API server
│   └── scrapers/
│       └── ufc_scraper.py  # UFC scraping logic
├── tests/
│   ├── test_api_pytest.py  # Automated tests (pytest)
│   ├── test_api.py         # Legacy manual testing script
│   ├── verify_caching.py   # Caching performance test
│   └── mypy.ini            # Static type checking config
├── Dockerfile              # Docker image configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```
## Features

- **Automated Scraping:** Fetches live data from UFCStats.com and Wikipedia.
- **Caching:** 12-hour caching layer using `Flask-Caching` for lightning-fast responses (< 20ms).
- **Interactive UI:** Swagger UI for easy API exploration.
- **Type Safety:** Comprehensive Python type hinting and `mypy` integration.
- **CI/CD:** Automated testing and Docker builds via GitHub Actions.

## Configuration

The application uses environment variables for configuration. A template is provided in `.env.example`.

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```
2. Adjust the values in `.env` as needed:
   - `API_PORT`: Port the API will listen on (default: 5000).
   - `CACHE_TIMEOUT`: Data cache duration in seconds (default: 43200).
   - `FLASK_DEBUG`: Enable/disable debug mode (default: True).

## Swagger Documentation
 
 interactive Swagger UI is available at:
```
http://localhost:5000/apidocs
```
This UI allows you to explore and test the API endpoints directly from your browser.

## External Documentation

For offline access or third-party integration, you can find the documentation in the `docs/` folder:

- **[API Reference (Markdown)](docs/API_REFERENCE.md)**
- **[OpenAPI Specification (JSON)](docs/openapi.json)**
 
## API Endpoints

### 1. Health Check
```
GET /api/health
```
Returns API health status.

### 2. Get Events (Names and Dates Only)
```
GET /api/events
```
Returns upcoming UFC events with just names and dates.

**Response:**
```json
{
  "status": "success",
  "count": 7,
  "events": [
    {
      "event_name": "UFC Fight Night: Bautista vs. Oliveira",
      "event_date": "February 07, 2026",
      "event_type": "UFC Fight Night",
      "event_number": "268"
    },
    {
      "event_name": "UFC 325: Strickland vs. Hernandez", 
      "event_date": "February 21, 2026",
      "event_type": "UFC",
      "event_number": "325"
    }
  ]
}
```

### 3. Get Full Events (with Location)
```
GET /api/events/full
```
Returns upcoming UFC events with names, dates, types, numbers, and locations.

**Response:**
```json
{
  "status": "success",
  "count": 7,
  "events": [
    {
      "event_date": "February 07, 2026",
      "event_name": "UFC Fight Night: Bautista vs. Oliveira",
      "event_number": "268",
      "event_type": "UFC Fight Night",
      "location": "Las Vegas, Nevada, USA"
    }
  ]
}
```



## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the API server:
```bash
python src/api.py
```

3. API will be available at:
- http://127.0.0.1:5000
- http://0.0.0.0:5000

4. Run automated tests:
```bash
pytest
```

5. Verify caching performance:
```bash
python tests/verify_caching.py
```

## Example Usage with curl

```bash
# Health check
curl http://127.0.0.1:5000/api/health

# Get events (names and dates only)
curl http://127.0.0.1:5000/api/events

# Get full events (with location)
curl http://127.0.0.1:5000/api/events/full
```

## Example Usage with Python

```python
import requests

# Get upcoming events (name and date only)
response = requests.get("http://127.0.0.1:5000/api/events")
data = response.json()

for event in data['events']:
    print(f"{event['event_name']} - {event['event_date']}")
```

## Docker Deployment

### Using Docker

1. Build the Docker image:
```bash
docker build -t ufc-api .
```

2. Run the container:
```bash
docker run -d -p 5000:5000 --name ufc-api ufc-api
```

3. Check logs:
```bash
docker logs ufc-api
```

4. Stop the container:
```bash
docker stop ufc-api
docker rm ufc-api
```

### Using Docker Compose (Recommended)

1. Start the service:
```bash
docker-compose up -d
```

2. Check logs:
```bash
docker-compose logs -f
```

3. Stop the service:
```bash
docker-compose down
```

### Testing with Docker

Once the container is running, test the API:
```bash
# Health check
curl http://localhost:5000/api/health

# Get events
curl http://localhost:5000/api/events

# Or run the test suite
python tests/test_api.py
```

## Development

To run the API in development mode with auto-reload:
```bash
cd src
python api.py
```

The API runs with Flask's debug mode enabled by default.