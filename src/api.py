from flask import Flask, jsonify
from scrapers.ufc_scraper import get_upcoming_ufc_schedule

app = Flask(__name__)

@app.route('/api/events', methods=['GET'])
def get_events():
    """
    API endpoint to get upcoming UFC events and dates
    Returns JSON with event names and dates
    """
    try:
        events = get_upcoming_ufc_schedule()
        
        # Return only event name and date
        simplified_events = [
            {
                'event_name': event['event_name'],
                'event_date': event['event_date']
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
def get_events_full():
    """
    API endpoint to get upcoming UFC events with full details (including location)
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
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'message': 'UFC Events API is running'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
