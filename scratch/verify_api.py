import httpx
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_insights():
    try:
        # Note: This will fail if not authenticated, but we want to check the route exists
        response = httpx.get(f"{BASE_URL}/admin/insights")
        print(f"Insights status: {response.status_code}")
        if response.status_code == 401:
            print("Insights route exists but requires auth (Expected)")
        else:
            print(f"Response: {response.text}")
            
        response = httpx.get(f"{BASE_URL}/admin/receivers/non-existent-id")
        print(f"Receiver detail status: {response.status_code}")
        if response.status_code == 401:
             print("Receiver detail route exists but requires auth (Expected)")
             
    except Exception as e:
        print(f"Connection failed: {e}. Make sure the server is running.")

if __name__ == "__main__":
    test_insights()
