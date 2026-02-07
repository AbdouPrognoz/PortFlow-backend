# Port Terminal Backend

A FastAPI backend for managing port terminal operations, including user management, terminal operations, and booking systems.

## Tech Stack

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **PostgreSQL (Neon)** - Database
- **python-jose** - JWT tokens
- **passlib** - Password hashing

## Setup Instructions

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your database credentials:
   ```bash
   cp .env.example .env
   ```
4. Run database migrations:
   ```bash
   alembic upgrade head
   ```
5. Seed the database with initial data:
   ```bash
   python seed.py
   ```
6. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

After starting the server, visit:
- Interactive docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Features

- User authentication and authorization
- Role-based access control (Admin, Operator, Carrier, Driver)
- Terminal management
- Booking system
- Profile management for different user types
- Notification system

## Database Schema

The application uses PostgreSQL with the following main entities:
- Users (with roles: ADMIN, OPERATOR, CARRIER, DRIVER)
- Terminals
- Profiles (Operator, Carrier, Driver)
- Bookings
- Notifications
- Audit logs
- Anomalies
- Chat system

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Secret key for JWT tokens
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time (default: 30)
- `PROJECT_NAME` - Project name (default: Port Terminal API)
- `API_V1_STR` - API version prefix (default: /api/v1)