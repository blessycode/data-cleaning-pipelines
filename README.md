# Data Cleaning Pipeline

A robust, full-stack application designed to clean, profile, and validate datasets with ease.

## 🚀 Key Features

- **Automated Data Cleaning**: Handle missing values, outliers, and duplicates automatically.
- **Data Profiling**: Generate detailed insights and statistics about your data.
- **Feature Engineering**: Get intelligent suggestions for feature transformations.
- **RESTful API**: Fully-featured FastAPI backend with JWT authentication.
- **Modern UI**: Responsive React frontend with real-time task monitoring.

## 📁 Project Structure

- `/api`: FastAPI backend, database migrations, and authentication.
- `/frontend`: React + TypeScript frontend with Tailwind CSS.
- `/data_cleaning_pipeline`: Core Python logic for data processing.

## 🛠️ Quick Start

### 1. Backend Setup
```bash
cd api
pip install -r requirements-api.txt
# Set environment variables (see DEPLOYMENT.md)
alembic upgrade head
python init_db.py
uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
# Set REACT_APP_API_URL in .env
npm start
```

## 📖 Documentation

- [Deployment Guide](DEPLOYMENT.md): Detailed instructions for manual and cloud deployment.
- [API Documentation](api/README.md): Endpoint details and authentication guide.
- [Backend Installation](api/INSTALL.md): Troubleshooting common installation issues.

## 🔒 Security

- JWT-based authentication
- Bcrypt password hashing
- Secure file upload handling
- CORS protection

## 📜 License

This project is licensed under the MIT License.
