# UFC Events API

A simple Flask API to scrape and return upcoming UFC events and dates.

## Project Structure

```
UFC/
├── src/
│   ├── api.py              # Main Flask API server
│   └── scrapers/
│       └── ufc_scraper.py  # UFC scraping logic
├── tests/
│   └── test_api.py         # API testing script
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Docker Compose orchestration
├── .dockerignore          # Docker ignore rules
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

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
      "event_date": "February 07, 2026"
    },
    {
      "event_name": "UFC Fight Night: Strickland vs. Hernandez", 
      "event_date": "February 21, 2026"
    }
  ]
}
```

### 3. Get Full Events (with Location)
```
GET /api/events/full
```
Returns upcoming UFC events with names, dates, and locations.

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

4. Test the API (in a separate terminal):
```bash
python tests/test_api.py
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