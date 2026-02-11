import requests
import time

def test_caching(endpoint):
    print(f"Testing caching for: {endpoint}")
    
    # First request
    start_time = time.time()
    response = requests.get(f"http://127.0.0.1:5000{endpoint}")
    first_duration = time.time() - start_time
    print(f"First request duration: {first_duration:.2f} seconds")
    
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        return

    # Second request (should be cached)
    start_time = time.time()
    response = requests.get(f"http://127.0.0.1:5000{endpoint}")
    second_duration = time.time() - start_time
    print(f"Second request duration: {second_duration:.2f} seconds")
    
    if first_duration > second_duration * 10:
        print("SUCCESS: Caching is working correctly!")
    else:
        print("WARNING: Caching might not be effective or the difference is too small.")
    
    print("-" * 30)

if __name__ == "__main__":
    # Wait a bit for the server to start
    time.sleep(2)
    try:
        test_caching("/api/events")
        test_caching("/api/events/full")
    except Exception as e:
        print(f"Failed to connect to API: {e}")
