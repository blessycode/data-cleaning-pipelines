# Data Cleaning Pipeline API

FastAPI backend for the Data Cleaning Pipeline with authentication, security, and async processing.

## 🚀 Quick Start

### Installation

**IMPORTANT: Fix for jose/python-jose conflict**

If you see this error:
```
SyntaxError: Missing parentheses in call to 'print'
```

This means the wrong `jose` package (Python 2 version) is installed. Fix it:

```bash
# Option 1: Use the setup script (recommended)
cd api
python setup.py
# OR
bash setup.sh

# Option 2: Manual fix
pip uninstall -y jose
pip install python-jose[cryptography]>=3.3.0
pip install -r requirements-api.txt
```

### Standard Installation

```bash
# Install dependencies
cd api
pip install -r requirements-api.txt

# Or use the setup script to fix common issues
python setup.py
```

### Running the Server

```bash
# Development mode
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Authentication

### Register a New User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepassword123",
    "email": "user@example.com",
    "confirm_password": "securepassword123"
  }'
```

Response:
```json
{
  "message": "User registered successfully",
  "username": "newuser",
  "email": "user@example.com"
}
```

**Requirements:**
- Username: 3-50 characters (alphanumeric, underscores, hyphens)
- Password: Minimum 8 characters
- Email: Optional

### Get Access Token (Login)

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=newuser&password=securepassword123"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400,
  "username": "newuser",
  "role": "user"
}
```

**Default Admin Account:**
- Username: `admin` (from settings)
- Password: `admin123` (from settings)

### Using the Token

```bash
curl -X GET "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Get Current User Info

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📡 API Endpoints

### 1. Run Complete Pipeline

```bash
curl -X POST "http://localhost:8000/api/v1/pipeline/run" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@data.csv" \
  -F "file_type=csv" \
  -F "profile_data=true" \
  -F "apply_cleaning=true" \
  -F "enable_feature_suggestions=true" \
  -F "validate_final_data=true" \
  -F "export_formats=[\"csv\",\"excel\",\"parquet\"]"
```

Response:
```json
{
  "task_id": "uuid-here",
  "status": "pending",
  "message": "Pipeline task started..."
}
```

### 2. Check Task Status

```bash
curl -X GET "http://localhost:8000/api/v1/tasks/{task_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Download Results

```bash
curl -X GET "http://localhost:8000/api/v1/tasks/{task_id}/download?file_type=csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o output.csv
```

### 4. Validate Data

```bash
curl -X POST "http://localhost:8000/api/v1/validate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@data.csv" \
  -F "schema={\"columns\":{\"age\":\"int64\"}}"
```

### 5. Get Feature Suggestions

```bash
curl -X POST "http://localhost:8000/api/v1/features/suggest" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@data.csv" \
  -F "target_column=target"
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password hashing
- **CORS Protection**: Configurable CORS middleware
- **File Size Limits**: Configurable upload size limits
- **Input Validation**: Pydantic models for request validation
- **Rate Limiting**: (Can be added with slowapi)

## 🛠️ Configuration

Edit `api/.env` or set environment variables:

```bash
# Security
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-password

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False

# File Upload
MAX_FILE_SIZE=104857600  # 100 MB
```

## 📝 Example Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Register a new user (optional - can use default admin)
register_data = {
    "username": "newuser",
    "password": "securepassword123",
    "email": "user@example.com",
    "confirm_password": "securepassword123"
}
response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print("Registration:", response.json())

# 2. Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "newuser", "password": "securepassword123"}
)
token = response.json()["access_token"]
print("Login successful!")

# 3. Get current user info
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
print("User info:", response.json())

# 4. Run pipeline
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
print(f"Task started: {task_id}")

# 5. Check status
response = requests.get(
    f"{BASE_URL}/api/v1/tasks/{task_id}",
    headers=headers
)

print("Task status:", response.json())
```

## 🔧 Production Deployment

1. **Change default credentials** in `.env`
2. **Use strong SECRET_KEY** (generate with: `openssl rand -hex 32`)
3. **Enable HTTPS** with reverse proxy (nginx)
4. **Set DEBUG=False**
5. **Use process manager** (systemd, supervisor, or PM2)
6. **Configure rate limiting**
7. **Set up logging**
8. **Use database** for task storage (Redis/PostgreSQL)


## 📊 Monitoring

- Health check: `GET /health`
- Task status: `GET /api/v1/tasks/{task_id}`
- List tasks: `GET /api/v1/tasks`

