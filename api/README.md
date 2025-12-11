# Data Cleaning Pipeline API

FastAPI backend for the Data Cleaning Pipeline with authentication, security, and async processing.

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements-api.txt

# Copy environment file
cp api/.env.example api/.env

# Edit api/.env with your configuration
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

### Get Access Token

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Using the Token

```bash
curl -X GET "http://localhost:8000/api/v1/tasks" \
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

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    data={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# Run pipeline
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open("data.csv", "rb")}
data = {
    "file_type": "csv",
    "apply_cleaning": "true",
    "enable_feature_suggestions": "true"
}

response = requests.post(
    "http://localhost:8000/api/v1/pipeline/run",
    headers=headers,
    files=files,
    data=data
)

task_id = response.json()["task_id"]

# Check status
response = requests.get(
    f"http://localhost:8000/api/v1/tasks/{task_id}",
    headers=headers
)

print(response.json())
```

## 🐳 Docker Support (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔧 Production Deployment

1. **Change default credentials** in `.env`
2. **Use strong SECRET_KEY** (generate with: `openssl rand -hex 32`)
3. **Enable HTTPS** with reverse proxy (nginx)
4. **Set DEBUG=False**
5. **Use process manager** (systemd, supervisor, or Docker)
6. **Configure rate limiting**
7. **Set up logging**
8. **Use database** for task storage (Redis/PostgreSQL)

## 📊 Monitoring

- Health check: `GET /health`
- Task status: `GET /api/v1/tasks/{task_id}`
- List tasks: `GET /api/v1/tasks`

