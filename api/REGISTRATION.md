# User Registration Guide

## Overview

The API now supports user registration! Users must register before they can use the data cleaning pipeline.

## Registration Endpoint

**POST** `/auth/register`

### Request Body (JSON)

```json
{
  "username": "newuser",
  "password": "securepassword123",
  "email": "user@example.com",
  "confirm_password": "securepassword123"
}
```

### Requirements

- **Username**: 3-50 characters, alphanumeric with underscores and hyphens only
- **Password**: Minimum 8 characters
- **Email**: Optional
- **Confirm Password**: Optional, but must match password if provided

### Response

```json
{
  "message": "User registered successfully",
  "username": "newuser",
  "email": "user@example.com"
}
```

### Error Responses

**400 Bad Request** - Username already exists:
```json
{
  "detail": "Username 'newuser' already exists"
}
```

**400 Bad Request** - Password mismatch:
```json
{
  "detail": "Password and confirmation do not match"
}
```

**400 Bad Request** - Invalid username format:
```json
{
  "detail": "Username can only contain letters, numbers, underscores, and hyphens"
}
```

## Examples

### Using cURL

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "mypassword123",
    "email": "john@example.com",
    "confirm_password": "mypassword123"
  }'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/auth/register",
    json={
        "username": "john_doe",
        "password": "mypassword123",
        "email": "john@example.com",
        "confirm_password": "mypassword123"
    }
)

print(response.json())
```

### Using JavaScript/Fetch

```javascript
fetch('http://localhost:8000/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'john_doe',
    password: 'mypassword123',
    email: 'john@example.com',
    confirm_password: 'mypassword123'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## After Registration

Once registered, users can:

1. **Login** at `/auth/login` to get a JWT token
2. **Access protected endpoints** using the token
3. **View their profile** at `/api/v1/users/me`
4. **Use all API features** with their account

## Default Admin Account

The system still maintains a default admin account for backward compatibility:
- Username: `admin` (from settings)
- Password: `admin123` (from settings)

This account is automatically created if no users exist in the system.

## User Storage

- Users are stored in `users.json` file (in the API directory)
- Passwords are hashed using bcrypt
- In production, replace with a proper database (PostgreSQL, MongoDB, etc.)

## Security Notes

- Passwords are never stored in plain text
- All passwords are hashed using bcrypt
- JWT tokens expire after 24 hours (configurable)
- Usernames are case-insensitive for login but case-preserved for display

