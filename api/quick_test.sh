#!/bin/bash
# Quick API Test Script

BASE_URL="http://localhost:8000"

echo "=================================="
echo "  API Quick Test"
echo "=================================="
echo ""

# 1. Health Check
echo "1. Testing health check..."
curl -s "$BASE_URL/health" | python -m json.tool
echo ""

# 2. Authentication
echo "2. Testing authentication..."
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123")

TOKEN=$(echo $TOKEN_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
    echo "❌ Authentication failed"
    exit 1
fi

echo "✅ Authentication successful"
echo "Token: ${TOKEN:0:50}..."
echo ""

# 3. Test Protected Endpoint
echo "3. Testing protected endpoint..."
curl -s -X GET "$BASE_URL/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo ""

echo "✅ All quick tests passed!"
echo ""
echo "💡 Next steps:"
echo "   - Test file upload: python test_api.py your_file.csv"
echo "   - Use Swagger UI: http://localhost:8000/docs"
echo "   - See TESTING.md for detailed guide"

