from flask import Flask, jsonify
from flasgger import Swagger # type: ignore
from flask_caching import Cache
from scrapers.ufc_scraper import get_upcoming_ufc_schedule
from typing import Any, Dict, List

app = Flask(__name__)
swagger = Swagger(app)

# Configure caching
cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 43200  # 12 hours
})

@app.route('/api/events', methods=['GET'])
@cache.cached()
def get_events() -> Any:
    """
    Get upcoming UFC events and dates
    ---
    tags:
      - Events
    responses:
      200:
        description: List of upcoming UFC events with basic details
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            count:
              type: integer
              example: 7
            events:
              type: array
              items:
                type: object
                properties:
                  event_name:
                    type: string
                    example: "UFC Fight Night: Bautista vs. Oliveira"
                  event_date:
                    type: string
                    example: "February 07, 2026"
                  event_type:
                    type: string
                    example: "UFC Fight Night"
                  event_number:
                    type: string
                    example: "268"
    """
    try:
        events = get_upcoming_ufc_schedule()
        
        # Return event name, date, type, and number
        simplified_events = [
            {
                'event_name': event['event_name'],
                'event_date': event['event_date'],
                'event_type': event['event_type'],
                'event_number': event['event_number']
            }
            for event in events
        ]
        
        return jsonify({
            'status': 'success',
            'count': len(simplified_events),
            'events': simplified_events
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/events/full', methods=['GET'])
@cache.cached()
def get_events_full() -> Any:
    """
    Get upcoming UFC events with full details
    ---
    tags:
      - Events
    responses:
      200:
        description: List of upcoming UFC events with full details including location
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            count:
              type: integer
              example: 7
            events:
              type: array
              items:
                type: object
                properties:
                  event_name:
                    type: string
                    example: "UFC Fight Night: Bautista vs. Oliveira"
                  event_date:
                    type: string
                    example: "February 07, 2026"
                  event_type:
                    type: string
                    example: "UFC Fight Night"
                  event_number:
                    type: string
                    example: "268"
                  location:
                    type: string
                    example: "Las Vegas, Nevada, USA"
    """
    try:
        events = get_upcoming_ufc_schedule()
        
        return jsonify({
            'status': 'success',
            'count': len(events),
            'events': events
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check() -> Any:
    """
    Health check endpoint
    ---
    tags:
      - System
    responses:
      200:
        description: API health status
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            message:
              type: string
              example: UFC Events API is running
    """
    return jsonify({
        'status': 'healthy',
        'message': 'UFC Events API is running'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
