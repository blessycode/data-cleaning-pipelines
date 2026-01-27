# Deployment Guide

Complete guide for deploying the Data Cleaning Pipeline application reliably.

## 🚀 Quick Start (Manual)

This guide covers how to set up the application manually.

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL (or use default SQLite for testing/development if configured)

### Service Setup

#### 1. Backend (API) Setup

1. **Navigate to the API directory:**
   ```bash
   cd api
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements-api.txt
   ```

3. **Set up environment:**
   Copy `.env.example` to `.env` (if available) or create one.
   ```bash
   # Linux/Mac
   export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/data_cleaning_db"
   export SECRET_KEY="your-secret-key-here"

   # Windows (PowerShell)
   $env:DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/data_cleaning_db"
   $env:SECRET_KEY="your-secret-key-here"
   ```

4. **Initialize Database:**
   Ensure your PostgreSQL server is running and the database exists.
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Initialize DB
   python init_db.py
   ```

5. **Start the API Server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
   The API will be available at http://localhost:8000.

#### 2. Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure API URL:**
   Create a `.env` file in the `frontend` directory:
   ```env
   REACT_APP_API_URL=http://localhost:8000
   ```

4. **Start Development Server:**
   ```bash
   npm start
   ```
   The frontend will be available at http://localhost:3000.

5. **Build for Production:**
   ```bash
   npm run build
   ```
   Serve the contents of `build/` using a static site server (e.g., Nginx, serve).

## ☁️ Cloud Deployment

### AWS / DigitalOcean / Heroku

Since Dockerfiles are removed, follow the standard "Platform as a Service" or "Virtual Machine" setup:

1. **Provision Server**: Ubuntu 22.04 LTS recommended.
2. **Install Dependencies**: proper python and node versions.
3. **Database**: Use a managed RDS/PostgreSQL instance or install locally on the VM.
4. **Environment Variables**: Set `DATABASE_URL`, `SECRET_KEY`, etc.
5. **Process Management**: Use `systemd` or `supervisor` to keep `uvicorn` running.
6. **Reverse Proxy**: Use Nginx to forward requests to localhost:8000 (API) and serve frontend static files.

## 🔒 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Change default admin credentials
- [ ] Use strong database passwords
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable database backups
- [ ] Monitor logs

## 🆘 Troubleshooting

### Database connection issues
- Check `DATABASE_URL` format.
- Verify database server is running.
- Verify credentials.

### API not starting
- Check logs.
- Verify all dependencies in `requirements-api.txt` are installed.

### Frontend not loading
- Check API URL in `.env`.
- Verify the API is running on port 8000.


