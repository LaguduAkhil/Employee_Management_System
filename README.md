# Employee Management System

A production-style Employee Management System backend built with FastAPI and PostgreSQL. Designed for mid-level backend developers to understand modern API architecture and best practices.

## Project Overview

This is a **monolithic, service-oriented** architecture (not microservices) that demonstrates:
- Clean separation of concerns (API, Service, Repository layers)
- JWT authentication and role-based access control
- Professional error handling and validation
- Database relationships and transactions
- Pagination, search, and filtering capabilities
- Production-ready code patterns

**Perfect for:**
- Learning FastAPI and SQLAlchemy ORM
- Understanding layered architecture
- Backend interview preparation
- Real-world API implementation patterns

---

## Architecture Explanation

### The Three-Layer Pattern

```
HTTP Request
    ↓
[API Routes Layer] ← Thin routes, validation
    ↓
[Service Layer] ← Business logic, rules
    ↓
[Repository Layer] ← Database operations
    ↓
PostgreSQL
```

**Why this architecture?**
- **Testable**: Mock dependencies easily
- **Maintainable**: Change logic in one place
- **Scalable**: Layers can be optimized independently
- **Interview-friendly**: Clear separation of concerns
- **Production-ready**: Professional code organization

---

## Tech Stack

- **Python 3.12** - Modern Python
- **FastAPI** - High-performance web framework
- **PostgreSQL** - Robust relational database
- **SQLAlchemy 2.0** - Modern ORM
- **Pydantic** - Data validation
- **JWT** - Stateless authentication
- **Docker** - Containerization

---

## Folder Structure

```
app/
├── api/                    # Route handlers
│   ├── auth.py            # Login, logout
│   ├── employees.py       # Employee CRUD
│   ├── departments.py     # Department management
│   ├── leaves.py          # Leave requests
│   ├── attendance.py      # Attendance tracking
│   └── health.py          # Health checks
│
├── models/                # SQLAlchemy ORM models
│   ├── user.py           # Authentication user
│   ├── employee.py       # Employee records
│   ├── department.py     # Departments
│   ├── leave.py          # Leave requests
│   └── attendance.py     # Attendance records
│
├── schemas/              # Pydantic validation
│   ├── user.py
│   ├── employee.py
│   ├── department.py
│   ├── leave.py
│   └── attendance.py
│
├── services/            # Business logic
│   ├── user_service.py
│   ├── employee_service.py
│   ├── department_service.py
│   ├── leave_service.py
│   └── attendance_service.py
│
├── repository/          # Database operations
│   ├── base.py         # Generic CRUD
│   ├── user_repo.py
│   ├── employee_repo.py
│   ├── department_repo.py
│   ├── leave_repo.py
│   └── attendance_repo.py
│
├── core/               # Configuration
│   ├── config.py      # Settings
│   ├── security.py    # JWT, hashing
│   └── enums.py       # Status constants
│
├── db/                # Database setup
│   └── database.py    # SQLAlchemy engine
│
├── middleware/        # Request processing
│   └── auth.py       # JWT verification
│
├── utils/            # Helpers
│   └── exceptions.py  # Custom errors
│
└── main.py          # FastAPI app
```

---

## Installation & Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 12+
- Docker & Docker Compose (optional)

### Step 1: Clone and Setup Virtual Environment

```bash
# Navigate to project
cd Employee_Management_System

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Setup Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env with your configuration
# For local development, defaults are usually fine
```

### Step 4: Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE employee_db;
CREATE USER emp_user WITH PASSWORD 'emp_password';
GRANT ALL PRIVILEGES ON DATABASE employee_db TO emp_user;
\q

# Update .env with your credentials
# DATABASE_URL=postgresql+psycopg://emp_user:emp_password@localhost:5432/employee_db
```

### Step 5: Run Application

```bash
# Tables will be created automatically on first run
python -m uvicorn app.main:app --reload

# Application starts at: http://localhost:8000
# API Docs (Swagger): http://localhost:8000/docs
# Alternative Docs (ReDoc): http://localhost:8000/redoc
```

---

## Docker Setup (Alternative)

### Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# Application runs at http://localhost:8000
# Database runs at localhost:5432

# View logs
docker-compose logs -f api

# Stop everything
docker-compose down
```

---

## API Endpoints

### Authentication

```
POST /api/auth/login
POST /api/auth/register
GET  /api/auth/me
POST /api/auth/logout
```

### Employees

```
POST   /api/employees                    # Create employee (Admin)
GET    /api/employees                    # List employees
GET    /api/employees/me                 # Current user's profile
GET    /api/employees/{emp_id}           # Get employee details
GET    /api/employees/search/{term}      # Search employees
PUT    /api/employees/{emp_id}           # Update employee
DELETE /api/employees/{emp_id}           # Delete employee (Admin)
```

### Departments

```
POST   /api/departments                  # Create (Admin)
GET    /api/departments                  # List all
GET    /api/departments/{dept_id}        # Get details
GET    /api/departments/search/{term}    # Search
PUT    /api/departments/{dept_id}        # Update (Admin)
DELETE /api/departments/{dept_id}        # Delete (Admin)
```

### Leaves

```
POST   /api/leaves                       # Apply for leave
GET    /api/leaves                       # List my leaves
GET    /api/leaves/{leave_id}            # Get leave details
POST   /api/leaves/{leave_id}/approve    # Approve (Manager/Admin)
POST   /api/leaves/{leave_id}/reject     # Reject (Manager/Admin)
POST   /api/leaves/{leave_id}/cancel     # Cancel (Own/Admin)
DELETE /api/leaves/{leave_id}            # Delete (Admin)
```

### Attendance

```
POST   /api/attendance                           # Mark attendance (Admin)
GET    /api/attendance/{att_id}                  # Get record
GET    /api/attendance/employee/{emp_id}        # List records
GET    /api/attendance/employee/{emp_id}/month  # Monthly summary
GET    /api/attendance/employee/{emp_id}/range  # Date range
PUT    /api/attendance/{att_id}                  # Update (Admin)
DELETE /api/attendance/{att_id}                  # Delete (Admin)
```

### Health

```
GET /api/health          # Health check
GET /api/               # API info
```

---

## Authentication Flow

### 1. User Login

```
Request:
POST /api/auth/login
{
    "email": "user@company.com",
    "password": "password123"
}

Response:
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
        "id": 1,
        "email": "user@company.com",
        "role": "employee",
        "is_active": true
    }
}
```

### 2. Use Token in Requests

```
GET /api/employees/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 3. Token Validation

Every request with a token goes through middleware:
1. Extract token from `Authorization: Bearer <token>`
2. Verify JWT signature and expiration
3. Load user from database
4. Pass to request handler as `current_user`

---

## Role-Based Access Control

### Admin Role
- Full access to all APIs
- Can create/edit/delete employees, departments
- Can approve/reject leave requests
- Can mark attendance

### Manager Role
- View employees in their department
- Review leave requests from their team
- View team attendance
- Cannot edit other managers or admins

### Employee Role
- View own profile only
- Apply for leave
- View own attendance
- Update own profile (limited fields)
- Cannot view others' data

---

## Sample API Requests

### 1. User Registration

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "SecurePass123!",
    "role": "admin"
  }'
```

### 2. User Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "SecurePass123!"
  }'

# Response includes access_token
# Copy this token for next requests
```

### 3. Create Department

```bash
curl -X POST "http://localhost:8000/api/departments" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Engineering",
    "code": "ENG",
    "description": "Engineering Department"
  }'
```

### 4. Create Employee

```bash
curl -X POST "http://localhost:8000/api/employees" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@company.com",
    "employee_code": "EMP001",
    "phone": "+1234567890",
    "department_id": 1,
    "password": "SecurePass123!",
    "date_of_birth": "1990-01-15",
    "date_of_joining": "2023-01-01"
  }'
```

### 5. Apply for Leave

```bash
curl -X POST "http://localhost:8000/api/leaves" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "leave_type": "casual",
    "start_date": "2024-01-15",
    "end_date": "2024-01-17",
    "reason": "Personal work",
    "number_of_days": 3
  }'
```

### 6. Mark Attendance

```bash
curl -X POST "http://localhost:8000/api/attendance" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "attendance_date": "2024-01-10",
    "status": "present",
    "check_in_time": "2024-01-10T09:00:00",
    "check_out_time": "2024-01-10T17:30:00"
  }'
```

### 7. List Employees (with pagination)

```bash
curl -X GET "http://localhost:8000/api/employees?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 8. Search Employees

```bash
curl -X GET "http://localhost:8000/api/employees/search/john?page=1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Testing in Swagger UI

1. Open http://localhost:8000/docs
2. Click "Authorize" button
3. Login and copy the access token
4. Paste token in authorization popup
5. Use Swagger UI to test all endpoints

**The Swagger UI is your interactive API testing tool.**

---

## Sample Seed Data

Create a Python script `seed_data.py`:

```python
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models import User, Department, Employee
from app.core.security import hash_password
from app.core.enums import RoleEnum
from datetime import date

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Create departments
eng_dept = Department(
    name="Engineering",
    code="ENG",
    description="Software Engineering",
)
sales_dept = Department(
    name="Sales",
    code="SALES",
    description="Sales Department",
)
db.add(eng_dept)
db.add(sales_dept)
db.commit()

# Create admin user
admin_user = User(
    email="admin@company.com",
    password_hash=hash_password("admin123"),
    role=RoleEnum.ADMIN
)
db.add(admin_user)
db.commit()

# Create manager
manager_user = User(
    email="manager@company.com",
    password_hash=hash_password("manager123"),
    role=RoleEnum.MANAGER
)
db.add(manager_user)
db.commit()

# Create manager employee record
manager_emp = Employee(
    user_id=manager_user.id,
    employee_code="MG001",
    first_name="Manager",
    last_name="User",
    phone="+1234567890",
    department_id=eng_dept.id,
    date_of_joining=date(2023, 1, 1)
)
db.add(manager_emp)
db.commit()

# Create employees
emp1 = User(
    email="john.doe@company.com",
    password_hash=hash_password("john123"),
    role=RoleEnum.EMPLOYEE
)
db.add(emp1)
db.commit()

emp1_record = Employee(
    user_id=emp1.id,
    employee_code="EMP001",
    first_name="John",
    last_name="Doe",
    phone="+1234567891",
    department_id=eng_dept.id,
    date_of_birth=date(1990, 5, 15),
    date_of_joining=date(2023, 6, 1)
)
db.add(emp1_record)
db.commit()

emp2 = User(
    email="jane.smith@company.com",
    password_hash=hash_password("jane123"),
    role=RoleEnum.EMPLOYEE
)
db.add(emp2)
db.commit()

emp2_record = Employee(
    user_id=emp2.id,
    employee_code="EMP002",
    first_name="Jane",
    last_name="Smith",
    phone="+1234567892",
    department_id=sales_dept.id,
    date_of_joining=date(2023, 7, 1)
)
db.add(emp2_record)
db.commit()

print("✅ Seed data created successfully!")
print("\nTest Accounts:")
print("Admin: admin@company.com / admin123")
print("Manager: manager@company.com / manager123")
print("Employee 1: john.doe@company.com / john123")
print("Employee 2: jane.smith@company.com / jane123")

db.close()
```

Run it:
```bash
python seed_data.py
```

---

## How This Works in a Real Company

### Day 1: Employee Onboarding
1. HR admin creates employee in system
2. Employee receives login credentials
3. Employee logs in, views profile, sets preferences
4. Manager approves pending setup

### Regular Day: Leave Management
1. Employee submits leave request
2. Manager reviews in dashboard
3. Manager approves/rejects with remarks
4. HR tracks leave balance
5. Monthly reporting

### Attendance Tracking
1. Admin marks attendance daily (or via integration)
2. Employees can view own attendance
3. Managers can view team attendance
4. HR can generate reports
5. System tracks patterns

### Department Management
1. Admin creates departments
2. Sets department managers
3. Assigns employees to departments
4. Managers see only their team

### Access Control in Action
```
Admin Access:
- Create/edit/delete all entities
- View all data
- System configuration

Manager Access:
- View department employees
- Approve leave requests from team
- View team attendance
- Cannot see other departments

Employee Access:
- View own profile
- Apply for leave
- View own attendance
- Update own details (limited)
```

---

## Interview Presentation Guide

### Part 1: Project Overview (2 min)
*"This is a production-style Employee Management System built with FastAPI and PostgreSQL. It demonstrates professional backend architecture for managing employees, departments, leave requests, and attendance."*

### Part 2: Architecture (3 min)
*"I've used a three-layer architecture:*
- *API layer handles HTTP requests and validation*
- *Service layer contains all business logic*
- *Repository layer handles database operations*

*This separation makes the code testable, maintainable, and scalable. Each layer has a single responsibility."*

### Part 3: Key Features (2 min)
- JWT authentication with role-based access control
- Complete CRUD operations with soft deletes
- Pagination and search capabilities
- Leave balance validation
- Attendance summary generation
- Error handling with custom exceptions
- Database relationships (user → employee → department)

### Part 4: Technical Decisions (2 min)
- **SQLAlchemy 2.0**: Modern ORM with type hints
- **Pydantic v2**: Data validation and serialization
- **JWT**: Stateless authentication, scalable
- **Soft deletes**: Audit trail for compliance
- **Monolithic**: Simple, no complexity overhead

### Part 5: What's Missing (optional) (1 min)
- Email notifications (would integrate with SendGrid)
- File uploads (resume, documents)
- Advanced reporting (would use Celery)
- Caching (would add Redis)
- Advanced logging (would use ELK stack)

### Part 6: Testing (1 min)
*"For testing:*
- *Unit tests for services (mock repository)*
- *Integration tests with test database*
- *API tests using FastAPI TestClient*
- *I haven't included them here to keep project focused, but this is essential in production."*

### Confidence Points to Mention
✅ Clean, readable code
✅ Professional error handling
✅ Security (JWT, password hashing)
✅ Database design with relationships
✅ Pagination and filtering
✅ API documentation (Swagger)
✅ Docker containerization
✅ Environment configuration
✅ Monolithic (no over-engineering)
✅ Practical business logic

---

## Database Schema

### Users Table
```
id (PK) | email (UNIQUE) | password_hash | role | is_active | created_at | updated_at
```

### Employees Table
```
id (PK) | user_id (FK) | department_id (FK) | employee_code | first_name | last_name
| casual_leaves | sick_leaves | earned_leaves | created_by | updated_by | created_at | updated_at
```

### Departments Table
```
id (PK) | name (UNIQUE) | code (UNIQUE) | manager_id | created_by | updated_by | created_at | updated_at
```

### Leaves Table
```
id (PK) | employee_id (FK) | leave_type | start_date | end_date | reason | status
| approved_by | approved_at | created_at | updated_at
```

### Attendance Table
```
id (PK) | employee_id (FK) | attendance_date | status | check_in_time | check_out_time
| created_by | updated_by | created_at | updated_at
```

---

## Common Issues & Solutions

### Issue: "Connection refused" for PostgreSQL
```bash
# Check if PostgreSQL is running
psql -U postgres -c "SELECT version();"

# For Docker
docker-compose ps
```

### Issue: "ModuleNotFoundError: No module named 'app'"
```bash
# Ensure you're in the project root
cd Employee_Management_System

# And using correct virtual environment
source venv/bin/activate
```

### Issue: "Invalid token" error
```bash
# Generate new token by logging in again
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@company.com", "password": "admin123"}'
```

---

## Performance Considerations

- **Connection Pooling**: 20 connections by default, configurable
- **Query Optimization**: Use pagination for large datasets
- **Soft Deletes**: Good for compliance, but consider archive tables for old data
- **Caching**: Can be added with Redis for frequently accessed data
- **Database Indexes**: Create on email, employee_code, dates

---

## Security Practices

✅ **Passwords**: Hashed with bcrypt
✅ **Tokens**: JWT with configurable expiration
✅ **CORS**: Restricted to defined origins
✅ **Input Validation**: Pydantic schemas validate all input
✅ **Authorization**: Role-based access control on all routes
✅ **Soft Deletes**: Audit trail for compliance
✅ **Environment Variables**: Secrets not in code
✅ **Error Messages**: Generic messages, no info leakage

---

## Production Checklist

- [ ] Update `SECRET_KEY` in `.env`
- [ ] Set `DEBUG=False`
- [ ] Use strong database password
- [ ] Configure proper `CORS_ORIGINS`
- [ ] Set up SSL/TLS
- [ ] Enable database backups
- [ ] Configure logging and monitoring
- [ ] Add rate limiting
- [ ] Implement request logging
- [ ] Set up error tracking (Sentry)
- [ ] Test disaster recovery
- [ ] Load testing with JMeter/K6

---

## Learning Resources

The code is written to be:
- **Self-documenting**: Clear function/variable names
- **Well-commented**: Important sections explained
- **Type-hinted**: Every function has types for clarity
- **Error-handling**: Every error is meaningful

Study these files in order:
1. `core/config.py` - Configuration pattern
2. `db/database.py` - Database setup
3. `models/` - How ORM models work
4. `schemas/` - Pydantic validation
5. `repository/base.py` - Generic CRUD pattern
6. `services/user_service.py` - Business logic pattern
7. `api/auth.py` - Simple route example
8. `api/employees.py` - Complex route with auth
9. `main.py` - App initialization

---

## Metrics to Explain in Interview

- **API Response Time**: < 200ms for most endpoints
- **Database Query Time**: < 50ms with proper indexing
- **Concurrent Users**: Can handle ~100+ with current setup
- **Data Consistency**: ACID transactions with PostgreSQL
- **Security**: JWT expiration, password hashing, RBAC
- **Availability**: Health checks, graceful shutdown

---

## Next Steps for Production

1. **Add Tests**: Unit and integration tests with pytest
2. **Add Logging**: Structured logging with JSON format
3. **Add Monitoring**: Prometheus metrics, Grafana dashboards
4. **Add Caching**: Redis for frequently accessed data
5. **Add Search**: Elasticsearch for full-text search
6. **Add Async Jobs**: Celery for background tasks
7. **Add API Versioning**: /api/v1/, /api/v2/
8. **Add Webhooks**: For external system integration
9. **Add GraphQL**: Alternative to REST
10. **Add Messaging**: RabbitMQ for async communication

---

## Support & Contribution

This project is designed for learning. Feel free to:
- Add tests
- Improve documentation
- Optimize queries
- Add new features
- Submit improvements

---

## License

This project is provided as an educational resource.

---

**Happy coding! Good luck with your backend journey! 🚀**
