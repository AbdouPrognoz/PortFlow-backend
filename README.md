# Port Terminal Management System - Backend

A professional, high-performance FastAPI backend designed to streamline port terminal logistics. This system manages complex booking workflows, user role-based permissions, and terminal operations with real-time updates and robust data validation.

## 🚀 Overview

The Port Terminal Management System provides a centralized platform for:
- **Terminal Operations**: Managing slots, availability, and operator assignments.
- **Booking Lifecycle**: Handling the complete flow from carrier request to driver consumption.
- **Role-Based Access**: Specialized interfaces and permissions for Admins, Operators, Carriers, and Drivers.
- **Real-Time Logistics**: Tracking bookings, anomalies, and notifications to ensure smooth terminal flow.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.9+)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Database**: **PostgreSQL** (Neon)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Security**: JWT Authentication (python-jose), Password Hashing (passlib with bcrypt)

## 📖 API Reference

### Authentication
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Authenticate and obtain a JWT access token |
| `POST` | `/api/v1/auth/register` | Register a new user (Operator, Carrier, or Driver) |

### Admin Operations
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/admin/users` | List all users with optional role filtering |
| `GET` | `/api/v1/admin/users/{user_id}` | Retrieve detailed user profile |
| `PATCH` | `/api/v1/admin/users/{user_id}` | Update user status or email |
| `DELETE` | `/api/v1/admin/users/{user_id}` | Permanently delete a user |
| `GET` | `/api/v1/admin/terminals` | List all terminals in the system |
| `POST` | `/api/v1/admin/terminals` | Register a new terminal |
| `PUT` | `/api/v1/admin/terminals/{terminal_id}` | Update terminal details (slots, coordinates) |
| `GET` | `/api/v1/admin/carriers` | List all carriers with status filtering |
| `POST` | `/api/v1/admin/carriers/approve` | Approve or reject carrier registrations |
| `GET` | `/api/v1/admin/bookings` | Global booking overview with filters |
| `POST` | `/api/v1/admin/operators/{id}/assign-terminal` | Assign an operator to a specific terminal |

### Operator Operations (Terminal Specific)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/operator/my-terminal` | Get details of the assigned terminal |
| `GET` | `/api/v1/operator/bookings` | View all bookings for the assigned terminal |
| `POST` | `/api/v1/operator/bookings/confirm` | Confirm or reject a pending booking |
| `PUT` | `/api/v1/operator/bookings/{id}` | Update booking details (e.g., assign driver) |

### Carrier Operations
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/carrier/my-bookings` | List all bookings created by the carrier |
| `POST` | `/api/v1/carrier/bookings` | Request a new booking slot at a terminal |
| `GET` | `/api/v1/carrier/drivers` | List all drivers registered under this carrier |
| `DELETE` | `/api/v1/carrier/bookings/{id}` | Cancel a pending booking |

### Driver Operations
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/driver/my-bookings` | View personal booking assignments |
| `GET` | `/api/v1/driver/available-bookings` | Browse confirmed bookings ready for assignment |
| `POST` | `/api/v1/driver/assign-to-booking/{id}`| Self-assign to a carrier's confirmed booking |
| `POST` | `/api/v1/driver/consume-booking/{id}` | Mark a booking as completed (consumed) |

### Common Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/common/terminals` | Public list of available terminals |
| `GET` | `/api/v1/common/profile` | Retrieve current authenticated user's profile |
| `GET` | `/health` | API health check |

## ⚙️ Setup & Installation

1. **Clone & Environment**:
   ```bash
   git clone <repository-url>
   cd port-terminal-backend
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**:
   Copy `.env.example` to `.env` and configure your `DATABASE_URL` (PostgreSQL) and `SECRET_KEY`.

4. **Database Setup**:
   ```bash
   alembic upgrade head
   python seed.py
   ```

5. **Run Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

Visit `http://localhost:8000/docs` for interactive Swagger documentation.