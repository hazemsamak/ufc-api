import sys
import os
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from api import app

class APIClient:
    def __init__(self, base_url="http://localhost:5010"):
        self.base_url = base_url
        self.server_running = False
        try:
            r = requests.get(f"{base_url}/api/health", timeout=0.1)
            if r.status_code == 200:
                self.server_running = True
        except Exception:
            self.server_running = False

        if not self.server_running:
            app.config['TESTING'] = True
            self.flask_client = app.test_client()

    def get(self, endpoint):
        if self.server_running:
            return requests.get(f"{self.base_url}{endpoint}")
        else:
            class DummyResponse:
                def __init__(self, res):
                    self._res = res
                def json(self):
                    return self._res.get_json()
            return DummyResponse(self.flask_client.get(endpoint))

def test_filtering():
    client = APIClient()

    print("1. Testing No Filtering...")
    r = client.get('/api/events')
    data = r.json()
    all_count = data['count']
    print(f"   Total events: {all_count}")

    print("\n2. Testing Type Filtering (UFC)...")
    r = client.get('/api/events?type=UFC')
    data = r.json()
    ufc_count = data['count']
    print(f"   UFC events: {ufc_count}")
    for e in data['events']:
        assert "UFC" in e['event_type']
        assert "Fight Night" not in e['event_type']

    print("\n3. Testing Search (Vegas)...")
    r = client.get('/api/events/full?search=Vegas')
    data = r.json()
    vegas_count = data['count']
    print(f"   Events in Vegas: {vegas_count}")
    for e in data['events']:
        assert "Vegas" in e['location']

    print("\n4. Testing Combined (UFC + Vegas)...")
    r = client.get('/api/events/full?type=UFC&search=Vegas')
    data = r.json()
    combined_count = data['count']
    print(f"   UFC events in Vegas: {combined_count}")

    print("\nSUCCESS: Filtering and Search verified!")

if __name__ == "__main__":
    try:
        test_filtering()
    except Exception as e:
        print(f"\nFAILED: {e}")
