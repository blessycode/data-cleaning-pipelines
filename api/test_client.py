"""
Example API Client
Test script for API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_api():
    """Test API endpoints"""
    
    # 1. Health check
    print("1. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    
    # 2. Login
    print("2. Testing authentication...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"   ✓ Authentication successful")
        print(f"   Token: {token[:50]}...\n")
    else:
        print(f"   ✗ Authentication failed: {response.text}\n")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Run pipeline (if you have a test file)
    print("3. Testing pipeline endpoint...")
    print("   (Skipping - requires test file)")
    print("   Example usage:")
    print(f"   curl -X POST '{BASE_URL}/api/v1/pipeline/run' \\")
    print(f"     -H 'Authorization: Bearer {token[:20]}...' \\")
    print(f"     -F 'file=@data.csv' \\")
    print(f"     -F 'file_type=csv' \\")
    print(f"     -F 'apply_cleaning=true'\n")
    
    # 4. List tasks
    print("4. Testing task listing...")
    response = requests.get(f"{BASE_URL}/api/v1/tasks", headers=headers)
    if response.status_code == 200:
        print(f"   ✓ Tasks retrieved: {len(response.json().get('tasks', []))} tasks\n")
    else:
        print(f"   ✗ Error: {response.text}\n")
    
    print("API test completed!")


if __name__ == "__main__":
    test_api()

