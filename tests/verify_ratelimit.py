import sys
import os
import requests
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from api import app

def test_rate_limiting():
    url = "http://localhost:5010/api/health"
    print(f"Testing rate limiting on {url}...")
    
    server_running = False
    try:
        r = requests.get(url, timeout=1)
        if r.status_code == 200:
            server_running = True
    except Exception:
        server_running = False

    client = app.test_client() if not server_running else None
    
    for i in range(1, 15):
        if server_running:
            response = requests.get(url)
            status_code = response.status_code
            json_data = response.json()
        else:
            resp = client.get('/api/health')
            status_code = resp.status_code
            json_data = resp.get_json()

        print(f"Request {i}: Status {status_code}")
        if status_code == 429:
            print("SUCCESS: Rate limit triggered!")
            print(f"Response: {json_data}")
            return
        time.sleep(0.1)
    
    print("Rate limit NOT triggered. You may need to lower the limit in .env to verify.")

if __name__ == "__main__":
    test_rate_limiting()
