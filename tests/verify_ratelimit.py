import requests
import time

def test_rate_limiting():
    url = "http://localhost:5010/api/health"
    print(f"Testing rate limiting on {url}...")
    
    # We'll try to hit it 10 times quickly. 
    # Note: If default is 50 per hour, this might not trigger 429 unless 
    # we lower the limit for testing or have a very low limit.
    # However, this script demonstrates the approach.
    
    for i in range(1, 15):
        response = requests.get(url)
        print(f"Request {i}: Status {response.status_code}")
        if response.status_code == 429:
            print("SUCCESS: Rate limit triggered!")
            print(f"Response: {response.json()}")
            return
        time.sleep(0.1)
    
    print("Rate limit NOT triggered. You may need to lower the limit in .env to verify.")

if __name__ == "__main__":
    test_rate_limiting()
