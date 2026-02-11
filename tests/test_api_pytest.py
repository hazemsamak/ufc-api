import pytest
import sys
import os

# Add src to the path so we can import the app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from api import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'UFC Events API is running' in data['message']

def test_get_events(client):
    """Test the /api/events endpoint"""
    response = client.get('/api/events')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'count' in data
    assert 'events' in data
    if data['count'] > 0:
        event = data['events'][0]
        assert 'event_name' in event
        assert 'event_date' in event
        assert 'event_type' in event
        assert 'event_number' in event

def test_get_events_full(client):
    """Test the /api/events/full endpoint"""
    response = client.get('/api/events/full')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'count' in data
    assert 'events' in data
    if data['count'] > 0:
        event = data['events'][0]
        assert 'location' in event
