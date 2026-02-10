# UFC Events API Reference

**Version:** 1.0.0
**Base URL:** `http://localhost:5000`

## Overview

This API allows you to retrieve the upcoming schedule for UFC events. It scrapes data from official sources to provide up-to-date information on event names, dates, types, numbers, and locations.

## Authentication

This API is currently open and does not require authentication.

## Endpoints

### 1. Health Check

Verifies that the API server is running and responsive.

- **URL:** `/api/health`
- **Method:** `GET`
- **Description:** Returns the health status of the API.

**Response Example:**

```json
{
  "status": "healthy",
  "message": "UFC Events API is running"
}
```

### 2. Get Upcoming Events

Retrieves a list of upcoming UFC events with essential details (name, date, type, number).

- **URL:** `/api/events`
- **Method:** `GET`
- **Description:** Returns a JSON object containing a list of upcoming events.

**Response Schema:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `status` | string | API status (e.g., "success") |
| `count` | integer | Number of events returned |
| `events` | array | List of event objects |

**Event Object:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `event_name` | string | Full name of the event (e.g., "UFC Fight Night: Bautista vs. Oliveira") |
| `event_date` | string | Date of the event (e.g., "February 07, 2026") |
| `event_type` | string | Type of event ("UFC" or "UFC Fight Night") |
| `event_number` | string | The number of the event (e.g., "268" or "325") |

**Response Example:**

```json
{
  "status": "success",
  "count": 2,
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

### 3. Get Full Upcoming Events

Retrieves a list of upcoming UFC events with *all* available details, including location.

- **URL:** `/api/events/full`
- **Method:** `GET`
- **Description:** Returns a JSON object containing a detailed list of upcoming events.

**Response Schema:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `status` | string | API status (e.g., "success") |
| `count` | integer | Number of events returned |
| `events` | array | List of event objects |

**Event Object:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `event_name` | string | Full name of the event |
| `event_date` | string | Date of the event |
| `event_type` | string | Type of event |
| `event_number` | string | The number of the event |
| `location` | string | Venue and city/country of the event (e.g., "Las Vegas, Nevada, USA") |

**Response Example:**

```json
{
  "status": "success",
  "count": 1,
  "events": [
    {
      "event_name": "UFC Fight Night: Bautista vs. Oliveira",
      "event_date": "February 07, 2026",
      "event_type": "UFC Fight Night",
      "event_number": "268",
      "location": "Las Vegas, Nevada, USA"
    }
  ]
}
```

## Importing into Postman

You can easily import this API into [Postman](https://www.postman.com/) to test the endpoints:

1.  Open Postman and click the **Import** button in the top left corner (or press `Ctrl+O`).
2.  Drag and drop the `openapi.json` file into the import window, or select it from your file system.
3.  Postman will automatically detect the OpenAPI 2.0 format. Click **Import** to finish.
4.  You will now see a new collection named "API" (or the title defined in the spec) with all the endpoints ready to use.

## Error Handling

In case of an error, the API will return a JSON object with `status: "error"` and a `message` describing the issue.

```json
{
  "status": "error",
  "message": "Internal Server Error"
}
```
