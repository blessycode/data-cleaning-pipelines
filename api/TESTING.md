# API Testing Guide

Complete guide for testing the Data Cleaning Pipeline API.

## 🚀 Quick Start

### 1. Start the Server

```bash
# Terminal 1: Start the API server
cd api
python run_server.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 2. Run Automated Tests

```bash
# From the api directory
python test_api.py

# Or with a specific test file
python test_api.py ../cleaned_dataset.csv
```

## 📋 Manual Testing

### Using cURL

#### 1. Health Check
```bash
curl http://localhost:8000/health
```

#### 2. Register a New User (Optional)
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword123",
    "email": "test@example.com",
    "confirm_password": "testpassword123"
  }'
```

#### 3. Authentication (Login)
```bash
# Login with registered user
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword123"

# Or login with default admin
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Save the token from the response.

#### 4. Get Current User Info
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer $TOKEN"
```

#### 5. Run Pipeline
```bash
TOKEN="your-token-here"

curl -X POST "http://localhost:8000/api/v1/pipeline/run" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@path/to/your/file.csv" \
  -F "file_type=csv" \
  -F "apply_cleaning=true" \
  -F "enable_feature_suggestions=true" \
  -F "export_formats=[\"csv\",\"excel\"]"
```

#### 4. Check Task Status
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/{task_id}" \
  -H "Authorization: Bearer $TOKEN"
```

#### 5. Download Results
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/{task_id}/download?file_type=csv" \
  -H "Authorization: Bearer $TOKEN" \
  -o output.csv
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Register a new user (optional)
register_data = {
    "username": "testuser",
    "password": "testpassword123",
    "email": "test@example.com",
    "confirm_password": "testpassword123"
}
response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print("Registration:", response.json())

# 2. Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "testuser", "password": "testpassword123"}
)
token = response.json()["access_token"]
print("Login successful!")

# 3. Get current user info
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
print("User info:", response.json())

# 4. Run Pipeline
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open("data.csv", "rb")}
data = {
    "file_type": "csv",
    "apply_cleaning": "true",
    "enable_feature_suggestions": "true"
}

response = requests.post(
    f"{BASE_URL}/api/v1/pipeline/run",
    headers=headers,
    files=files,
    data=data
)

task_id = response.json()["task_id"]

# 3. Check Status
response = requests.get(
    f"{BASE_URL}/api/v1/tasks/{task_id}",
    headers=headers
)
print(response.json())
```

### Using Swagger UI (Recommended)

1. Start the server
2. Open browser: http://localhost:8000/docs
3. Click "Authorize" button
4. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
5. Click "Authorize"
6. Test endpoints interactively

## 🧪 Test Scenarios

### Scenario 1: Basic Pipeline Run

```bash
# 1. Upload a CSV file
# 2. Run pipeline with basic cleaning
# 3. Wait for completion
# 4. Download results
```

### Scenario 2: Full Pipeline with All Features

```bash
# Run with all features enabled:
# - Data cleaning
# - Profiling with visuals
# - Feature engineering suggestions
# - Final validation
# - Multiple export formats
```

### Scenario 3: Validation Only

```bash
# Test validation endpoint without running full pipeline
curl -X POST "http://localhost:8000/api/v1/validate" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@data.csv" \
  -F "schema={\"columns\":{\"age\":\"int64\"}}"
```

### Scenario 4: Feature Suggestions Only

```bash
# Get feature engineering suggestions
curl -X POST "http://localhost:8000/api/v1/features/suggest" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@data.csv" \
  -F "target_column=target"
```

## 🔍 Troubleshooting

### Server Won't Start

**Error**: `ModuleNotFoundError`
```bash
# Install dependencies
pip install -r requirements-api.txt
```

**Error**: `Address already in use`
```bash
# Change port in api/config.py or use different port
uvicorn main:app --port 8001
```

### Authentication Fails

**Error**: `401 Unauthorized`
- Check username/password in `.env` file
- Default: `admin` / `admin123`
- Make sure token is included in Authorization header

### File Upload Fails

**Error**: `413 Request Entity Too Large`
- File exceeds `MAX_FILE_SIZE` limit
- Increase limit in `api/config.py` or `.env`

**Error**: `400 Bad Request - Invalid file type`
- Check file extension matches `file_type` parameter
- Supported: `.csv`, `.xlsx`, `.xls`, `.parquet`

### Task Stuck

**Status**: `running` for too long
- Check server logs for errors
- Large files may take time
- Check `data_pipeline_output/` for partial results

## 📊 Expected Responses

### Successful Pipeline Start
```json
{
  "task_id": "uuid-here",
  "status": "pending",
  "message": "Pipeline task started..."
}
```

### Task Status (Running)
```json
{
  "task_id": "uuid-here",
  "status": "running",
  "progress": 45,
  "message": "Running pipeline...",
  "created_at": "2024-01-01T12:00:00"
}
```

### Task Status (Completed)
```json
{
  "task_id": "uuid-here",
  "status": "completed",
  "progress": 100,
  "message": "Pipeline completed successfully",
  "result": {
    "shape": {"rows": 1000, "columns": 10},
    "reports_generated": 5,
    "output_files": 3
  },
  "output_files": ["file1.csv", "file2.xlsx"]
}
```

## 🎯 Performance Testing

### Load Testing with Apache Bench

```bash
# Install ab (Apache Bench)
# On Ubuntu: sudo apt-get install apache2-utils

# Test health endpoint
ab -n 100 -c 10 http://localhost:8000/health

# Test authenticated endpoint (with token)
ab -n 50 -c 5 -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/tasks
```

### Stress Testing

```python
import asyncio
import aiohttp

async def stress_test():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(100):
            task = session.get("http://localhost:8000/health")
            tasks.append(task)
        await asyncio.gather(*tasks)
```

## ✅ Checklist

- [ ] Server starts without errors
- [ ] Health check returns 200
- [ ] Authentication works
- [ ] Can access protected endpoints
- [ ] File upload works
- [ ] Pipeline task starts
- [ ] Task status updates correctly
- [ ] Results can be downloaded
- [ ] Validation endpoint works
- [ ] Feature suggestions endpoint works
- [ ] Error handling works (invalid file, etc.)

## 📝 Notes

- Default credentials: `admin` / `admin123` (CHANGE IN PRODUCTION!)
- Token expires after 24 hours (configurable)
- File uploads are saved in `uploads/` directory
- Outputs are saved in `data_pipeline_output/` directory
- Old files are cleaned up after 24 hours (configurable)

