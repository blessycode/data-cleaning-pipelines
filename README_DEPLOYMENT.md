# Data Cleaning Pipeline - Complete Setup

## 🎯 Project Overview

Full-stack data cleaning pipeline application with:
- **Backend**: FastAPI + PostgreSQL
- **Frontend**: React + TypeScript
- **Database**: PostgreSQL with SQLAlchemy
- **Deployment**: Docker Compose ready

## 📁 Project Structure

```
data-cleaning-pipelines/
├── api/                    # FastAPI backend
│   ├── alembic/            # Database migrations
│   ├── db_models.py        # SQLAlchemy models
│   ├── db_service.py       # Database service layer
│   ├── database.py         # Database configuration
│   ├── main.py            # FastAPI app
│   └── ...
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   └── services/     # API services
│   └── ...
├── data_cleaning_pipeline/  # Core pipeline logic
├── docker-compose.yml     # Docker orchestration
├── Dockerfile            # Backend Docker image
└── .env.example          # Environment template
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone and setup
git clone <repo>
cd data-cleaning-pipelines
cp .env.example .env

# 2. Start all services
docker-compose up -d

# 3. Initialize database
docker-compose exec api python init_db.py
docker-compose exec api alembic upgrade head

# 4. Access
# Frontend: http://localhost:3000
# API: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Backend
```bash
cd api
pip install -r requirements-api.txt

# Setup PostgreSQL
createdb data_cleaning_db

# Configure .env
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/data_cleaning_db"

# Initialize
alembic upgrade head
python init_db.py

# Run
uvicorn main:app --reload
```

#### Frontend
```bash
cd frontend
npm install

# Configure
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Run
npm start
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=data_cleaning_db
DB_USER=postgres
DB_PASSWORD=postgres

# API
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

## 📊 Database Setup

### Create Initial Migration

```bash
cd api
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Reset Database

```bash
docker-compose down -v  # Removes volumes
docker-compose up -d
docker-compose exec api python init_db.py
```

## 🎨 Frontend Features

- User registration and login
- File upload with drag & drop
- Real-time task monitoring
- Task history and downloads
- Responsive design with Tailwind CSS

## 🔌 API Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /api/v1/pipeline/run` - Run data cleaning pipeline
- `GET /api/v1/tasks/{task_id}` - Get task status
- `GET /api/v1/tasks` - List user tasks
- `GET /api/v1/tasks/{task_id}/download` - Download results

See `/docs` for full API documentation.

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build

# Access shell
docker-compose exec api bash
docker-compose exec db psql -U postgres
```

## 📦 Production Deployment

See `DEPLOYMENT.md` for detailed production deployment instructions.

### Key Steps:
1. Set strong SECRET_KEY
2. Change default admin credentials
3. Use managed PostgreSQL
4. Enable HTTPS
5. Configure CORS properly
6. Set up monitoring

## 🧪 Testing

### Backend
```bash
cd api
python test_api.py
```

### Frontend
```bash
cd frontend
npm test
```

## 📝 Development

### Adding Database Models

1. Update `api/db_models.py`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Apply: `alembic upgrade head`

### Adding API Endpoints

1. Update `api/main.py`
2. Add models to `api/models.py`
3. Update frontend API service if needed

## 🆘 Troubleshooting

### Database Connection Failed
- Check DATABASE_URL format
- Verify PostgreSQL is running
- Check credentials

### Frontend Can't Connect to API
- Verify REACT_APP_API_URL
- Check CORS settings
- Check API is running

### Migration Errors
- Drop and recreate database
- Check alembic version table
- Verify model changes

## 📚 Documentation

- `DEPLOYMENT.md` - Production deployment guide
- `api/README.md` - API documentation
- `api/TESTING.md` - Testing guide
- `api/REGISTRATION.md` - User registration guide

## ✅ Status

- ✅ PostgreSQL database integration
- ✅ User authentication and registration
- ✅ React frontend with TypeScript
- ✅ Docker Compose setup
- ✅ Database migrations (Alembic)
- ✅ Production-ready configuration
- ✅ Deployment documentation

## 🎉 Ready for Deployment!

The application is fully configured and ready for deployment. Use Docker Compose for local development or follow DEPLOYMENT.md for production.

