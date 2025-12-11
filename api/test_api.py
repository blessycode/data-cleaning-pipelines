"""
Comprehensive API Testing Script
Tests all endpoints of the Data Cleaning Pipeline API
"""

import requests
import json
import time
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"
TEST_FILE = None  # Set to a test CSV file path if available


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_health_check():
    """Test health check endpoint"""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("   ❌ ERROR: Cannot connect to server. Is it running?")
        print("   Start server with: cd api && python run_server.py")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False


def test_root():
    """Test root endpoint"""
    print_section("2. Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False


def test_authentication():
    """Test authentication endpoint"""
    print_section("3. Authentication")
    try:
        # Try with default credentials
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": "admin",
                "password": "admin123"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"   ✅ Authentication successful")
            print(f"   Token: {token[:50]}...")
            print(f"   Token Type: {response.json()['token_type']}")
            print(f"   Expires In: {response.json()['expires_in']} seconds")
            return token
        else:
            print(f"   ❌ Authentication failed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return None


def test_protected_endpoint(token: str):
    """Test accessing a protected endpoint"""
    print_section("4. Protected Endpoint (Task Listing)")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/v1/tasks",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Access granted")
            print(f"   Total Tasks: {data.get('total', 0)}")
            print(f"   Recent Tasks: {len(data.get('tasks', []))}")
            return True
        else:
            print(f"   ❌ Access denied")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False


def test_pipeline_upload(token: str, test_file: str = None):
    """Test pipeline upload endpoint"""
    print_section("5. Pipeline Upload")
    
    if not test_file or not os.path.exists(test_file):
        print("   ⚠️  SKIPPED: No test file provided")
        print("   To test this endpoint, provide a CSV file:")
        print("   test_pipeline_upload(token, 'path/to/your/file.csv')")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(test_file, 'rb') as f:
            files = {"file": (os.path.basename(test_file), f, "text/csv")}
            data = {
                "file_type": "csv",
                "profile_data": "true",
                "apply_cleaning": "true",
                "enable_feature_suggestions": "false",
                "validate_final_data": "true",
                "export_formats": json.dumps(["csv", "excel"])
            }
            
            print(f"   Uploading file: {test_file}")
            response = requests.post(
                f"{BASE_URL}/api/v1/pipeline/run",
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result["task_id"]
            print(f"   ✅ Pipeline task started")
            print(f"   Task ID: {task_id}")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            return task_id
        else:
            print(f"   ❌ Pipeline start failed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return None


def test_task_status(token: str, task_id: str):
    """Test task status endpoint"""
    print_section("6. Task Status")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/v1/tasks/{task_id}",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Task status retrieved")
            print(f"   Task ID: {data['task_id']}")
            print(f"   Status: {data['status']}")
            print(f"   Progress: {data.get('progress', 0)}%")
            print(f"   Message: {data.get('message', 'N/A')}")
            
            if data.get('result'):
                result = data['result']
                print(f"   Result Shape: {result.get('shape', {})}")
                print(f"   Reports Generated: {result.get('reports_generated', 0)}")
            
            return data
        else:
            print(f"   ❌ Failed to get task status")
            print(f"   Status Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return None


def test_validation_endpoint(token: str, test_file: str = None):
    """Test validation endpoint"""
    print_section("7. Data Validation")
    
    if not test_file or not os.path.exists(test_file):
        print("   ⚠️  SKIPPED: No test file provided")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(test_file, 'rb') as f:
            files = {"file": (os.path.basename(test_file), f, "text/csv")}
            data = {
                "schema": json.dumps({
                    "columns": {
                        "age": "int64"
                    }
                })
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/validate",
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Validation completed")
            print(f"   Status: {result['status']}")
            print(f"   Score: {result['score']}/100")
            print(f"   Total Issues: {result['total_issues']}")
            if result.get('critical_issues'):
                print(f"   Critical Issues: {len(result['critical_issues'])}")
            return True
        else:
            print(f"   ❌ Validation failed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False


def test_feature_suggestions(token: str, test_file: str = None):
    """Test feature suggestions endpoint"""
    print_section("8. Feature Engineering Suggestions")
    
    if not test_file or not os.path.exists(test_file):
        print("   ⚠️  SKIPPED: No test file provided")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(test_file, 'rb') as f:
            files = {"file": (os.path.basename(test_file), f, "text/csv")}
            data = {}
            
            response = requests.post(
                f"{BASE_URL}/api/v1/features/suggest",
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Feature suggestions retrieved")
            print(f"   Total Suggestions: {result['total_suggestions']}")
            print(f"   Categories: {len(result.get('suggestions_by_category', {}))}")
            print(f"   Priority Features: {len(result.get('priority_features', []))}")
            print(f"   Quick Wins: {len(result.get('quick_wins', []))}")
            return True
        else:
            print(f"   ❌ Feature suggestions failed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False


def monitor_task(token: str, task_id: str, max_wait: int = 300):
    """Monitor a task until completion"""
    print_section("9. Task Monitoring")
    print(f"   Monitoring task: {task_id}")
    print(f"   Maximum wait time: {max_wait} seconds")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        status_data = test_task_status(token, task_id)
        
        if status_data:
            status = status_data.get('status')
            progress = status_data.get('progress', 0)
            
            print(f"   Status: {status} | Progress: {progress}%")
            
            if status == "completed":
                print(f"   ✅ Task completed successfully!")
                return True
            elif status == "failed":
                print(f"   ❌ Task failed: {status_data.get('error', 'Unknown error')}")
                return False
        
        time.sleep(5)  # Check every 5 seconds
    
    print(f"   ⚠️  Timeout: Task did not complete within {max_wait} seconds")
    return False


def run_all_tests(test_file: str = None):
    """Run all API tests"""
    print("\n" + "=" * 70)
    print("  DATA CLEANING PIPELINE API - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Server is not running. Please start it first:")
        print("   cd api && python run_server.py")
        return
    
    # Test 2: Root endpoint
    test_root()
    
    # Test 3: Authentication
    token = test_authentication()
    if not token:
        print("\n❌ Authentication failed. Cannot continue with protected endpoints.")
        return
    
    # Test 4: Protected endpoint
    test_protected_endpoint(token)
    
    # Test 5: Pipeline upload (if file provided)
    task_id = None
    if test_file and os.path.exists(test_file):
        task_id = test_pipeline_upload(token, test_file)
        
        # Test 6: Task status
        if task_id:
            test_task_status(token, task_id)
            
            # Test 9: Monitor task
            print("\n   Waiting for task to complete...")
            monitor_task(token, task_id, max_wait=300)
    
    # Test 7: Validation
    if test_file and os.path.exists(test_file):
        test_validation_endpoint(token, test_file)
    
    # Test 8: Feature suggestions
    if test_file and os.path.exists(test_file):
        test_feature_suggestions(token, test_file)
    
    print("\n" + "=" * 70)
    print("  TEST SUITE COMPLETED")
    print("=" * 70)
    print("\n✅ All tests completed!")
    print("\n💡 Tips:")
    print("   - Check API documentation at: http://localhost:8000/docs")
    print("   - Use Swagger UI for interactive testing")
    print("   - Check server logs for detailed error messages")


if __name__ == "__main__":
    import sys
    
    # Check if test file provided as argument
    test_file = None
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        if not os.path.exists(test_file):
            print(f"⚠️  Warning: Test file not found: {test_file}")
            test_file = None
    
    # Look for common test files in project root
    if not test_file:
        project_root = Path(__file__).parent.parent
        possible_files = [
            project_root / "cleaned_dataset.csv",
            project_root / "Housing.csv",
            project_root / "data" / "test.csv"
        ]
        for file_path in possible_files:
            if file_path.exists():
                test_file = str(file_path)
                print(f"📁 Using test file: {test_file}")
                break
    
    run_all_tests(test_file)

