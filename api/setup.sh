#!/bin/bash
# Setup script for Data Cleaning Pipeline API
# This script fixes common installation issues

set -e

echo "=========================================="
echo "Data Cleaning Pipeline API Setup"
echo "=========================================="
echo ""

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Not in a virtual environment"
    echo "   Consider activating a virtual environment first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate  # Linux/Mac"
    echo "   venv\\Scripts\\activate     # Windows"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Uninstall wrong jose package if installed
echo "🔍 Checking for incorrect 'jose' package..."
if python -c "import jose" 2>/dev/null; then
    echo "❌ Found incorrect 'jose' package (Python 2 version)"
    echo "   Uninstalling..."
    pip uninstall -y jose || true
    echo "✅ Removed incorrect package"
else
    echo "✅ No incorrect 'jose' package found"
fi

# Install/upgrade python-jose
echo ""
echo "📦 Installing/upgrading python-jose..."
pip install --upgrade "python-jose[cryptography]>=3.3.0"

# Install all requirements
echo ""
echo "📦 Installing all API requirements..."
if [ -f "requirements-api.txt" ]; then
    pip install -r requirements-api.txt
else
    echo "❌ requirements-api.txt not found!"
    echo "   Installing core packages manually..."
    pip install fastapi uvicorn python-multipart
    pip install "python-jose[cryptography]>=3.3.0"
    pip install "passlib[bcrypt]>=1.7.4"
    pip install "pydantic>=2.0.0" "pydantic-settings>=2.1.0"
    pip install pandas numpy openpyxl pyarrow
    pip install scipy matplotlib seaborn plotly kaleido
fi

# Verify installation
echo ""
echo "🔍 Verifying installation..."
python -c "from jose import jwt; print('✅ python-jose: OK')" || (echo "❌ python-jose: FAILED" && exit 1)
python -c "from fastapi import FastAPI; print('✅ FastAPI: OK')" || (echo "❌ FastAPI: FAILED" && exit 1)
python -c "import uvicorn; print('✅ Uvicorn: OK')" || (echo "❌ Uvicorn: FAILED" && exit 1)
python -c "from pydantic_settings import BaseSettings; print('✅ pydantic-settings: OK')" || (echo "❌ pydantic-settings: FAILED" && exit 1)

echo ""
echo "=========================================="
echo "✅ Setup completed successfully!"
echo "=========================================="
echo ""
echo "You can now start the server with:"
echo "  python run_server.py"
echo ""
echo "Or with uvicorn directly:"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""

