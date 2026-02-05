import requests
import json

# API base URL
BASE_URL = "http://127.0.0.1:5000"

def test_api():
    """
    Test the UFC Events API
    """
    print("Testing UFC Events API...")
    print("=" * 50)
    
    # Test health endpoint
    print("1. Health Check:")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Test events endpoint (name and date only)
    print("2. Get Events (Name and Date only):")
    try:
        response = requests.get(f"{BASE_URL}/api/events")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Count: {data['count']}")
        print("Events:")
        for event in data['events']:
            print(f"  • {event['event_name']} - {event['event_date']}")
        print()
    except Exception as e:
        print(f"Error: {e}")
    
    # Test full events endpoint
    print("3. Get Full Events (with location):")
    try:
        response = requests.get(f"{BASE_URL}/api/events/full")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Count: {data['count']}")
        print("Events:")
        for event in data['events']:
            print(f"  • {event['event_name']}")
            print(f"    Date: {event['event_date']}")
            print(f"    Location: {event['location']}")
        print()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
