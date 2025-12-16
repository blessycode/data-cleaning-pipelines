# Deployment Guide

Complete guide for deploying the Data Cleaning Pipeline application.

## 🚀 Quick Start with Docker Compose

The easiest way to deploy the entire stack is using Docker Compose.

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 3000, 8000, and 5432 available

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd data-cleaning-pipelines
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize database**
   ```bash
   docker-compose exec api python init_db.py
   ```

5. **Run migrations**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Database: localhost:5432

### Stop services
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

## 📦 Manual Deployment

### Backend (API)

1. **Install dependencies**
   ```bash
   cd api
   pip install -r requirements-api.txt
   ```

2. **Set up PostgreSQL**
   ```bash
   # Create database
   createdb data_cleaning_db
   
   # Or using psql
   psql -U postgres
   CREATE DATABASE data_cleaning_db;
   ```

3. **Configure environment**
   ```bash
   export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/data_cleaning_db"
   export SECRET_KEY="your-secret-key-here"
   ```

4. **Run migrations**
   ```bash
   alembic upgrade head
   ```

5. **Initialize database**
   ```bash
   python init_db.py
   ```

6. **Start server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Frontend

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API URL**
   ```bash
   # Create .env file
   echo "REACT_APP_API_URL=http://localhost:8000" > .env
   ```

3. **Build for production**
   ```bash
   npm run build
   ```

4. **Serve with nginx** (see nginx.conf in frontend/)

## 🐳 Docker Production Build

### Build images
```bash
# Build API
docker build -t data-cleaning-api .

# Build Frontend
cd frontend
docker build -t data-cleaning-frontend .
```

### Run with Docker
```bash
# Start database
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=data_cleaning_db \
  -p 5432:5432 \
  postgres:15-alpine

# Start API
docker run -d \
  --name api \
  --link postgres:db \
  -e DATABASE_URL="postgresql+asyncpg://postgres:postgres@db:5432/data_cleaning_db" \
  -p 8000:8000 \
  data-cleaning-api

# Start Frontend
docker run -d \
  --name frontend \
  -p 3000:3000 \
  data-cleaning-frontend
```

## ☁️ Cloud Deployment

### AWS (EC2 + RDS)

1. **Launch EC2 instance**
   - Ubuntu 22.04 LTS
   - t3.medium or larger
   - Security group: Allow ports 22, 80, 443, 8000

2. **Set up RDS PostgreSQL**
   - Create RDS instance (PostgreSQL 15)
   - Note connection details

3. **Deploy application**
   ```bash
   # On EC2 instance
   git clone <repository>
   cd data-cleaning-pipelines
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Update .env with RDS connection
   # Start services
   docker-compose up -d
   ```

4. **Set up Nginx reverse proxy**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:3000;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
       }
   }
   ```

### Heroku

1. **Install Heroku CLI**

2. **Create apps**
   ```bash
   heroku create data-cleaning-api
   heroku create data-cleaning-frontend
   ```

3. **Add PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev -a data-cleaning-api
   ```

4. **Deploy**
   ```bash
   # API
   cd api
   heroku git:remote -a data-cleaning-api
   git push heroku main
   
   # Frontend
   cd ../frontend
   heroku git:remote -a data-cleaning-frontend
   git push heroku main
   ```

### DigitalOcean App Platform

1. **Create App**
   - Connect GitHub repository
   - Select "Docker" as build type

2. **Configure services**
   - API service: Port 8000
   - Frontend service: Port 3000
   - Database: Managed PostgreSQL

3. **Set environment variables**
   - DATABASE_URL
   - SECRET_KEY
   - REACT_APP_API_URL

## 🔒 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Change default admin credentials
- [ ] Use strong database passwords
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable database backups
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity

## 📊 Monitoring

### Health Checks

- API: `GET /health`
- Database: Check connection
- Frontend: Check if serving files

### Logs

```bash
# Docker logs
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f db

# Application logs
tail -f api/logs/app.log
```

## 🔄 Updates

### Update application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Run migrations
docker-compose exec api alembic upgrade head
```

## 🆘 Troubleshooting

### Database connection issues
- Check DATABASE_URL format
- Verify database is running
- Check firewall rules
- Verify credentials

### API not starting
- Check logs: `docker-compose logs api`
- Verify database connection
- Check environment variables

### Frontend not loading
- Check API URL in .env
- Verify CORS settings
- Check browser console for errors

## 📝 Environment Variables

See `.env.example` for all required variables.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `ADMIN_USERNAME`: Default admin username
- `ADMIN_PASSWORD`: Default admin password
- `REACT_APP_API_URL`: Frontend API URL

