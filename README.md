# Data Cleaning Pipeline

A full-stack application that ingests, profiles, cleans, validates, and exports datasets. Built with an async FastAPI backend, a React + TypeScript frontend, and a modular Python data-cleaning pipeline that produces profiling reports and visualizations.

<img src="https://raw.githubusercontent.com/blessycode/data-cleaning-pipelines/main/frontend/public/logo192.png" alt="Data Cleaning Pipeline logo">

- Backend: FastAPI, async SQLAlchemy, Alembic migrations
- Frontend: React + TypeScript (Create React App)
- Pipeline: pandas, scikit-learn, Plotly visualizations
- Exports: CSV, Excel, Parquet, HTML visualizations, PNG images

Quick links:
- API docs (when running): http://localhost:8000/docs
- Backend-specific docs: api/README.md
- Deployment guide: DEPLOYMENT.md
- Frontend docs: frontend/README.md
- Example pipeline runner: run.py

---

## Quick Start (Local development)

Prerequisites:
- Python 3.9+
- Node.js 16+ / npm
- PostgreSQL recommended for production (project can run with SQLite for quick tests)

1) Copy environment variables
```bash
# from repository root
cp .env.example .env
# edit .env to adjust DATABASE_URL, SECRET_KEY, ADMIN_PASSWORD, REACT_APP_API_URL, etc.
```

2) Backend (API)

From repository root:
```bash
cd api
python -m venv .venv            # optional
source .venv/bin/activate       # or .venv\Scripts\activate on Windows
pip install -r requirements-api.txt
```

Initialize the database and create default admin:
```bash
# apply migrations (if using Alembic)
alembic upgrade head

# initialize DB schema and default admin user
python init_db.py
# or start the run_server which prints the server info
python run_server.py
```

Start the development server:
```bash
# option A: use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# option B: use the helper script from repo root
python api/run_server.py
```

API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

3) Frontend

From repository root:
```bash
cd frontend
npm install
# create .env in frontend if needed:
# REACT_APP_API_URL=http://localhost:8000

npm start
# open http://localhost:3000
```

Build for production:
```bash
npm run build
# Serve build/ static files with nginx or any static server
```

---

## Standalone data pipeline

There are two easy ways to run the pipeline:

A. Example runner script (simple)
```bash
python run.py
```
Edit run.py to point to your dataset path and to enable/disable options (visuals, export formats, cleaning steps).

B. Programmatic usage (importable API)
```python
from data_cleaning_pipeline.pipe import clean_data

cleaned_df, reports, output_files = clean_data(
    "path/to/your.csv",
    file_type="csv",
    profile_data=True,
    include_visuals=True,
    save_output=True,
    output_dir="data_pipeline_output",
    apply_cleaning=True,
    export_formats=['csv','excel','parquet']
)
```

Outputs (by default) are written to `data_pipeline_output/`:
- reports/, visualizations/, exports/, logs/

---

## API - Basic usage examples

Get a token (login):
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Run the pipeline via API (multipart upload):
```bash
curl -X POST "http://localhost:8000/api/v1/pipeline/run" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@data.csv" \
  -F "file_type=csv" \
  -F "apply_cleaning=true" \
  -F "enable_feature_suggestions=true"
```

Check task status:
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/{task_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Download results:
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/{task_id}/download?file_type=csv" \
  -H "Authorization: Bearer YOUR_TOKEN" -o cleaned.csv
```

See `api/README.md` for more endpoints and request/response examples.

---

## Configuration

Key environment variables are in `.env.example`. Notable entries:
- DATABASE_URL: postgresql+asyncpg://user:pass@host:port/dbname
- SECRET_KEY: strong 32+ byte secret for JWT
- ADMIN_USERNAME / ADMIN_PASSWORD: default admin user (change in production)
- UPLOAD_DIR / OUTPUT_DIR: file handling directories
- RATE_LIMIT_ENABLED / RATE_LIMIT_REQUESTS: simple rate limiting toggles
- REACT_APP_API_URL: frontend -> backend base URL

Always change default secrets before deploying to production.

---

## Deployment & Production tips

See DEPLOYMENT.md for full deployment instructions. Key items:
- Set DEBUG=False in production and use a strong SECRET_KEY
- Use a PostgreSQL database and perform Alembic migrations
- Serve API via uvicorn behind a reverse proxy (Nginx) and enable HTTPS
- Run frontend build with CI/CD and serve statics via Nginx or CDN
- Use process management (systemd, supervisor) for reliability
- Consider object storage for large outputs and S3-compatible backups

Security checklist:
- Rotate default admin credentials
- Use HTTPS (TLS)
- Limit allowed CORS origins
- Monitor logs and enable DB backups

---

## Tests

Backend contains tests (api/test_api.py, api/test_client.py). Run tests with pytest:
```bash
cd api
pip install pytest
pytest -q
```

(Tests may rely on environment or test DB; see api/README.md for details.)

---

## Project structure (high level)

- api/ — FastAPI backend, authentication, tasks, DB integration, migrations
- frontend/ — React + TypeScript UI (Create React App)
- data_cleaning_pipeline/ — main pipeline modules:
  - pipe.py — orchestration & visualization export
  - pipeline.py — cleaning pipeline (ingestion, profiling, missing/outlier/dup handling, feature engineering)
  - cleaning/ — modular cleaning steps
- run.py — example script to run the pipeline directly
- .env.example — environment variable template
- DEPLOYMENT.md — deployment guide

---

## Contributing

Contributions welcome. Typical workflow:
1. Fork the repository
2. Create a feature branch
3. Add tests and documentation
4. Open a PR describing changes

Please run linters and tests before submitting a PR.

---

## License

This project is MIT licensed. See LICENSE for details.

---

## For your portfolio (copy-paste friendly)

Short description (1-2 lines)
- Developed a full-stack Data Cleaning Pipeline that automates profiling, cleaning, feature suggestions and exports for tabular datasets. The system includes an async FastAPI backend, a React TypeScript frontend, and a modular Python pipeline for production-ready data preprocessing.

Highlights / bullet points (use these on your portfolio or resume)
- Built and maintained an async FastAPI backend with JWT authentication, rate limiting, and secure file uploads.
- Implemented a modular data cleaning pipeline (ingestion, profiling, missing/outlier/duplicate handling, feature engineering) using pandas, scikit-learn and Plotly for visualizations.
- Designed programmatic and API-driven interfaces so users can run the pipeline locally or through REST endpoints (task-based processing with downloadable exports).
- Integrated export options (CSV, Excel, Parquet, HTML visualizations, PNG) and produced reproducible cleaning reports.
- Automated DB initialization and seeding (admin user), SQLAlchemy async support and Alembic migrations for schema management.
- Frontend implemented in React + TypeScript (Create React App) with environment-driven API base URL and Tailwind dev setup.
- Focus on security and production readiness: secret management, bcrypt password hashing, CORS configuration, and deployment checklist for HTTPS & reverse proxy.

Suggested single-line achievement metrics (customize with your numbers)
- Processed datasets up to X GB locally and reduced manual cleaning time by Y% using automated rules & profiling.
- Delivered a pipeline that reduced data-prep turnaround from days to hours for ML-ready datasets.

Example portfolio blurb (short)
- "Designed and implemented an end-to-end Data Cleaning Pipeline with an async FastAPI backend and a React frontend. The system automatically profiles and cleans datasets, provides feature engineering suggestions, and exports reproducible reports and visualizations — improving data-prep efficiency for downstream ML and analytics."

---

If you want, I can:
- Generate a shorter one-paragraph portfolio description,
- Craft bullet points for LinkedIn or a tailored CV item,
- Or create a condensed README (one-page) for GitHub project cards.

Which would you prefer next?
