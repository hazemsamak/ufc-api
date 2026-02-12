import requests

def test_filtering():
    base_url = "http://localhost:5010/api/events"
    
    print("1. Testing No Filtering...")
    r = requests.get(base_url)
    all_count = r.json()['count']
    print(f"   Total events: {all_count}")

    print("\n2. Testing Type Filtering (UFC)...")
    r = requests.get(f"{base_url}?type=UFC")
    ufc_count = r.json()['count']
    print(f"   UFC events: {ufc_count}")
    for e in r.json()['events']:
        assert "UFC" in e['event_type']
        assert "Fight Night" not in e['event_type']

    print("\n3. Testing Search (Vegas)...")
    r = requests.get(f"{base_url}/full?search=Vegas")
    vegas_count = r.json()['count']
    print(f"   Events in Vegas: {vegas_count}")
    for e in r.json()['events']:
        assert "Vegas" in e['location']

    print("\n4. Testing Combined (UFC + Vegas)...")
    r = requests.get(f"{base_url}/full?type=UFC&search=Vegas")
    combined_count = r.json()['count']
    print(f"   UFC events in Vegas: {combined_count}")

    print("\nSUCCESS: Filtering and Search verified!")

if __name__ == "__main__":
    try:
        test_filtering()
    except Exception as e:
        print(f"\nFAILED: {e}")
        print("Note: Ensure the API is running at localhost:5010")
