import os
from flask import Flask, jsonify
from flasgger import Swagger # type: ignore
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from scrapers.ufc_scraper import get_upcoming_ufc_schedule
from typing import Any, Dict, List, Sequence, Union, Callable, cast

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
swagger = Swagger(app)

# Configure caching
cache = Cache(app, config={
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_HOST': os.getenv('REDIS_HOST', 'localhost'),
    'CACHE_REDIS_PORT': int(os.getenv('REDIS_PORT', 6379)),
    'CACHE_DEFAULT_TIMEOUT': int(os.getenv('CACHE_TIMEOUT', 43200))
})

# Configure rate limiting
default_limits = cast(Any, os.getenv('RATELIMIT_DEFAULT', "200 per day;50 per hour").split(';'))
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=default_limits,
    storage_uri=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}"
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'status': 'error',
        'message': f"Rate limit exceeded: {e.description}"
    }), 429

@app.route('/api/events', methods=['GET'])
@cache.cached(query_string=True)
def get_events() -> Any:
    """
    Get upcoming UFC events and dates
    ---
    tags:
      - Events
    parameters:
      - name: type
        in: query
        type: string
        description: Filter by event type (e.g., "UFC", "UFC Fight Night")
      - name: search
        in: query
        type: string
        description: Search in event name or location
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
        from flask import request
        event_type = request.args.get('type')
        search_query = request.args.get('search')
        
        events = get_upcoming_ufc_schedule()
        
        # Apply filters
        if event_type:
            events = [e for e in events if event_type.lower() == e['event_type'].lower()]
        
        if search_query:
            search_query = search_query.lower()
            events = [e for e in events if search_query in e['event_name'].lower() or search_query in e['location'].lower()]
            
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
@cache.cached(query_string=True)
def get_events_full() -> Any:
    """
    Get upcoming UFC events with full details
    ---
    tags:
      - Events
    parameters:
      - name: type
        in: query
        type: string
        description: Filter by event type (e.g., "UFC", "UFC Fight Night")
      - name: search
        in: query
        type: string
        description: Search in event name or location
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
        from flask import request
        event_type = request.args.get('type')
        search_query = request.args.get('search')
        
        events = get_upcoming_ufc_schedule()
        
        # Apply filters
        if event_type:
            events = [e for e in events if event_type.lower() == e['event_type'].lower()]
        
        if search_query:
            search_query = search_query.lower()
            events = [e for e in events if search_query in e['event_name'].lower() or search_query in e['location'].lower()]
        
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
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)
