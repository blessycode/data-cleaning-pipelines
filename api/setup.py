#!/usr/bin/env python3
"""
Setup script for Data Cleaning Pipeline API
Fixes common installation issues, especially the jose/python-jose conflict
"""

import subprocess
import sys
import os

def run_command(cmd, check=True):
    """Run a shell command"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    return True

def check_package(package_name, import_test):
    """Check if a package is installed correctly"""
    try:
        exec(import_test)
        print(f"✅ {package_name}: OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name}: FAILED - {e}")
        return False

def main():
    print("=" * 50)
    print("Data Cleaning Pipeline API Setup")
    print("=" * 50)
    print()
    
    # Check if in virtual environment
    if not os.environ.get('VIRTUAL_ENV'):
        print("⚠️  Warning: Not in a virtual environment")
        print("   Consider activating a virtual environment first")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
        print()
    
    # Uninstall wrong jose package
    print("🔍 Checking for incorrect 'jose' package...")
    try:
        import jose
        # Check if it's the wrong one (Python 2 version)
        import inspect
        jose_file = inspect.getfile(jose)
        if 'jose.py' in jose_file or 'site-packages/jose' in jose_file:
            print("❌ Found incorrect 'jose' package (Python 2 version)")
            print("   Uninstalling...")
            run_command("pip uninstall -y jose", check=False)
            print("✅ Removed incorrect package")
    except ImportError:
        print("✅ No incorrect 'jose' package found")
    except Exception as e:
        print(f"⚠️  Could not check jose package: {e}")
    
    # Install/upgrade python-jose
    print()
    print("📦 Installing/upgrading python-jose...")
    run_command("pip install --upgrade 'python-jose[cryptography]>=3.3.0'")
    
    # Install requirements
    print()
    print("📦 Installing all API requirements...")
    requirements_file = os.path.join(os.path.dirname(__file__), "requirements-api.txt")
    if os.path.exists(requirements_file):
        run_command(f"pip install -r {requirements_file}")
    else:
        print("❌ requirements-api.txt not found!")
        print("   Installing core packages manually...")
        packages = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "python-multipart>=0.0.6",
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.4",
            "pydantic>=2.0.0",
            "pydantic-settings>=2.1.0",
            "pandas>=2.0.0",
            "numpy>=1.24.0",
            "openpyxl>=3.1.0",
            "pyarrow>=12.0.0",
            "scipy>=1.11.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "plotly>=5.17.0",
            "kaleido>=0.2.1",
        ]
        for package in packages:
            run_command(f"pip install {package}")
    
    # Verify installation
    print()
    print("🔍 Verifying installation...")
    checks = [
        ("python-jose", "from jose import jwt"),
        ("FastAPI", "from fastapi import FastAPI"),
        ("Uvicorn", "import uvicorn"),
        ("pydantic-settings", "from pydantic_settings import BaseSettings"),
        ("pandas", "import pandas"),
    ]
    
    all_ok = True
    for name, test in checks:
        if not check_package(name, test):
            all_ok = False
    
    print()
    if all_ok:
        print("=" * 50)
        print("✅ Setup completed successfully!")
        print("=" * 50)
        print()
        print("You can now start the server with:")
        print("  python run_server.py")
        print()
        print("Or with uvicorn directly:")
        print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        print()
    else:
        print("=" * 50)
        print("⚠️  Setup completed with some issues")
        print("=" * 50)
        print("Please check the errors above and install missing packages manually")
        sys.exit(1)

if __name__ == "__main__":
    main()

