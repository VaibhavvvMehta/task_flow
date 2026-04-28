# TaskFlow

A modern, role-based task management system built with Django and Django REST Framework. Managers and executives assign tasks to employees, track progress in real-time, and export performance reports. Employees manage their task status and receive automatic notifications. All authentication is handled via secure httpOnly JWT cookies with Redis-backed token blacklisting.

## Overview

TaskFlow is designed for organizations with hierarchical team structures. It solves the challenge of task tracking, accountability, and performance visibility across teams.

### Key Features

- **Role-Based Access Control** — Mainly 3 distinct roles with granular permissions
- **Task Assignment & Tracking** — Create, assign, and monitor tasks across teams
- **Real-Time Notifications** — Automatic alerts for task events
- **Performance Analytics** — Built-in reporting with CSV/Excel export
- **Audit Trail** — Complete history of all status changes and reassignments
- **Secure Authentication** — JWT in httpOnly cookies + Redis token blacklist
- **Soft Deletes** — Preserve data for compliance and historical analysis
- **Multi-Device Support** — Each device gets independent token pairs

## 🛠️ Tech Stack

| Layer | Technology | Version |
|---|---|---|
| **Backend** | Django | 5.2.12 |
| **API** | Django REST Framework | 3.17.1 |
| **Auth** | SimpleJWT + Redis | 5.5.1 |
| **Database** | PostgreSQL | 12+ |
| **Cache** | Redis | 6+ |
| **Frontend** | Tailwind CSS + Vanilla JS | 4.2.0 |
| **Containerization** | Docker & Compose | Latest |
| **Testing** | Pytest & Pytest-Django | Latest |

## 📋 Prerequisites

- **Docker & Docker Compose** (recommended for quick start)
- **Python 3.10+** (for local development)
- **PostgreSQL 12+** (if running locally)
- **Redis 6+** (if running locally)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone <repo-url>
cd task_flow

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env with your values (especially SECRET_KEY, EMAIL credentials)

# 4. Start all services
docker compose up --build

# 5. In a new terminal, apply migrations and seed demo data
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_data

# 6. Access the application
# - App: http://localhost:8002
# - pgAdmin: http://localhost:5050 (optional DB admin)
```

### Option 2: Local Development

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Ensure PostgreSQL and Redis are running locally

# 4. Configure environment
cp .env.example .env
# Edit .env and set:
# - POSTGRES_HOST=localhost
# - REDIS_URL=redis://localhost:6379/0
# - SECRET_KEY=your-secret

# 5. Run migrations
python manage.py migrate

# 6. Seed demo data (optional)
python manage.py seed_data

# 7. Start development server
python manage.py runserver

# 8. In another terminal, start Tailwind
python manage.py tailwind start
```

**App will be available at:** `http://localhost:8000`

## 🔧 Environment Variables

Create a `.env` file in the project root. See `.env.example` for the complete template.

### Essential Variables

```env
# Django Core
SECRET_KEY=your-very-secret-key-min-50-chars-abcdefghijklmnop
DEBUG=True                                    # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
POSTGRES_DB=taskflow
POSTGRES_USER=taskflow_user
POSTGRES_PASSWORD=secure_password_123!
POSTGRES_HOST=db                              # 'localhost' for local dev
POSTGRES_PORT=5432

# Cache (Redis)
REDIS_URL=redis://redis:6379/0                # 'redis://localhost:6379/0' for local dev

# Email (Gmail SMTP)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# CORS (Frontend)
CORS_ALLOWED_ORIGINS=http://localhost:8002

# JWT Token Lifetimes
JWT_ACCESS_LIFETIME=70                        # minutes
JWT_REFRESH_LIFETIME=7                        # days
```

### Optional Variables

```env
# pgAdmin (Database Admin Interface)
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin

# Email (if not using Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

## 📁 Project Structure

```
task_flow/
├── config/                    # Django settings and root URL configuration
│   ├── settings.py           # Main settings file
│   ├── urls.py               # Root URL routing
│   └── wsgi.py               # WSGI application
│
├── accounts/                  # User management & authentication
│   ├── models.py             # User model with role field
│   ├── views.py              # Login, logout, profile endpoints
│   ├── permissions.py        # Role-based permission classes
│   ├── serializers.py        # User serializers
│   └── urls.py               # Auth URL routing
│
├── tasks/                     # Task management core
│   ├── models.py             # Task, TaskStatusHistory, TaskAssignment
│   ├── views.py              # Task CRUD and status update views
│   ├── serializers.py        # Task serializers
│   ├── permissions.py        # Task-specific permissions
│   └── urls.py               # Task URL routing
│
├── notifications/             # In-app notification system
│   ├── models.py             # Notification model
│   ├── views.py              # Notification endpoints
│   ├── serializers.py        # Notification serializers
│   ├── notify.py             # notify() utility function
│   └── urls.py               # Notification URL routing
│
├── reports/                   # Analytics and data export
│   ├── views.py              # Report generation endpoints
│   ├── serializers.py        # Report serializers
│   ├── export.py             # CSV/Excel export logic
│   └── urls.py               # Report URL routing
│
├── theme/                     # Tailwind CSS integration
│   └── static_src/           # Tailwind build files
│
├── templates/                 # Django templates (HTML)
│   ├── base.html             # Base template with nav, footer
│   ├── login.html            # Login page
│   ├── dashboard.html        # Main dashboard
│   ├── tasks/
│   │   ├── my_tasks.html     # Employee's task list
│   │   └── assign_task.html  # Task creation form
│   ├── manager/
│   │   ├── manager_task.html # Manager's own tasks
│   │   └── team_view.html    # Team overview
│   ├── reports/
│   │   └── reports.html      # Analytics dashboard
│   └── profile.html          # User profile page
│
├── static/                    # Static assets (JavaScript)
│   └── js/
│       ├── api.js            # API client helper
│       ├── auth.js           # Authentication logic
│       └── notifications.js  # Notification handling
│
├── tests/                     # Test suite
│   ├── conftest.py           # Pytest fixtures and configuration
│   ├── test_auth.py          # Authentication tests
│   ├── test_tasks.py         # Task management tests
│   ├── test_permissions.py   # Permission tests
│   ├── test_notifications.py # Notification tests
│   └── test_reports.py       # Report generation tests
│
├── docker-compose.yml        # Multi-container orchestration
├── Dockerfile                # Django container definition
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
├── manage.py                 # Django CLI
└── README.md                 # This file
```

## 👥 User Roles & Permissions

TaskFlow includes 6 distinct roles with a clear hierarchy. The permission model is based on the `ELEVATED_ROLES` constant: `['manager', 'admin', 'ceo', 'cfo', 'cto']`

### Role Overview

| Role | Description | Task Permissions | View Scope |
|---|---|---|---|
| **Employee** | Default role for team members | View & update own only | Own tasks |
| **Manager** | Team lead, assigns tasks | Full control of team tasks | Own team |
| **Admin** | System administrator | Full control of all tasks | All data |
| **CEO** | Executive | Full control of all tasks | All data |
| **CFO** | Finance executive | Full control of all tasks | All data |
| **CTO** | Technology executive | Full control of all tasks | All data |

### Permission Matrix

| Action | Employee | Manager | Admin | CEO | CFO | CTO |
|--------|----------|---------|-------|-----|-----|-----|
| View own tasks | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View team tasks | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create tasks | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Assign tasks | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Edit task metadata | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Delete tasks (soft) | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Update own status | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Update any status | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Reassign tasks | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View team reports | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Export team data | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |

## API Endpoints

### Quick Reference

**Base URL:** `/api/v1/`

#### Authentication (`/auth/`)
```
POST   /login/               → Login with email/password
POST   /logout/              → Logout and blacklist tokens
POST   /token/refresh/       → Get new access token
GET    /me/                  → Get current user profile
PATCH  /me/                  → Update own profile
```

#### Users (`/users/`)
```
GET    /employees/           → List team employees (Manager+)
GET    /hierarchy/           → View organizational hierarchy
```

#### Tasks (`/tasks/`)
```
GET    /                     → Get my assigned tasks
POST   /                     → Create task
GET    /<id>/                → Get task detail
PATCH  /<id>/                → Edit task (Manager+)
DELETE /<id>/                → Delete task (soft) (Manager+)
PATCH  /<id>/status/         → Update task status
PATCH  /<id>/assign/         → Reassign task (Manager+)
POST   /team-assign/         → Bulk assign to team (Manager+)
GET    /manager/tasks/       → Manager's own tasks (Manager+)
GET    /manager/team/tasks/  → Team task overview (Manager+)
```

#### Notifications (`/notifications/`)
```
GET    /                     → Get notifications (last 50)
GET    /unread-count/        → Get unread count (bell badge)
PATCH  /<id>/read/           → Mark as read
PATCH  /mark-all-read/       → Mark all as read
```

#### Reports (`/reports/`)
```
GET    /my-performance/      → Personal performance metrics
GET    /team-summary/        → Team analytics (Manager+)
GET    /export/              → Download CSV/Excel (Manager+)
```

## Frontend Pages

| URL | Purpose | Access |
|-----|---------|--------|
| `/` | Login page | Public |
| `/dashboard/` | Main dashboard | All (authenticated) |
| `/profile/` | User profile & settings | All |
| `/hierarchy/` | Org chart view | All |
| `/tasks/` | My assigned tasks | All |
| `/manager/tasks/` | Manager's own tasks | Manager+ |
| `/manager/team/` | Team overview & stats | Manager+ |
| `/manager/assign/` | Create & assign tasks | Manager+ |
| `/notifications/` | Notification center | All |
| `/reports/` | Analytics & exports | All (role-limited) |

## 🔐 Authentication & Security

### How It Works

1. **Login** → User submits email + password
2. **Validation** → Credentials verified against database
3. **Token Issuance** → Access (70 min) + Refresh (7 days) tokens generated
4. **Cookie Storage** → Tokens stored in **httpOnly cookies** (JS cannot access)
5. **API Requests** → Cookies automatically included in each request
6. **Token Validation** → `CookieJWTAuthentication` validates and checks Redis blacklist
7. **Logout** → Tokens blacklisted in Redis (immediate, not waiting for expiry)

### Why httpOnly Cookies?

- **XSS Protection** — JavaScript cannot read httpOnly cookies
- **CSRF Protection** — Cookies automatically included with same-origin requests
- **No Manual Headers** — Frontend doesn't need to manage Authorization headers

### Token Blacklist

When you log out:
- Both access and refresh token JTIs are stored in Redis
- TTL = remaining token lifetime
- Tokens become immediately invalid
- Re-login is required even if token hasn't expired

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_tasks.py

# Run with coverage report
pytest --cov=. --cov-report=html

# Run only fast tests
pytest -m "not slow"

# Verbose output
pytest -v
```

Test fixtures are defined in `conftest.py` and include:
- `authenticated_user` — Employee account
- `manager_user` — Manager account
- `admin_user` — Admin account
- `sample_task` — Pre-created task
- `api_client` — Django test client with auth

## 📊 Database Models

### Core Models

**User**
- Extends Django's AbstractUser
- Fields: username, email, role, department, manager (self-referential)
- Related: assigned_tasks, created_tasks, direct_reports

**Task**
- Fields: title, description, status, priority, due_date, assigned_to, created_by
- Computed: is_overdue, days_overdue, done_at
- Related: status_history, assignments, notifications

**TaskStatusHistory** (Audit Trail)
- Records every status change with actor and timestamp
- Fields: task, changed_by, old_status, new_status, changed_at

**TaskAssignment** (Reassignment History)
- Tracks who assigned a task and when
- Fields: task, assigned_to, assigned_by, assigned_at

**Notification**
- Types: task_assigned, task_overdue, task_due_reminder, task_status_changed, task_comment_added
- Fields: user, type, title, message, task, is_read, created_at

## 🔑 Key Design Decisions

### JWT in httpOnly Cookies
Tokens stored in httpOnly cookies prevent XSS-based token theft since JavaScript cannot access them. The `CookieJWTAuthentication` class reads from cookies first, then falls back to the `Authorization` header (for tests).

### Redis Token Blacklist
Logout doesn't rely on token expiry. When a user logs out, both token JTIs are stored in Redis with TTL matching the token's remaining lifetime. This enables true immediate logout without database lookups on every request.

### Soft Deletes
Tasks are never physically deleted—they're marked with `is_deleted=True`. This preserves the audit trail, enables historical analysis, and allows recovery if needed.

### TaskStatusHistory
Every status change is recorded with:
- Old status → New status
- Who changed it (user)
- Exact timestamp

This creates a complete audit log for compliance and analysis.

### Separate Tasks for Bulk Assign
When assigning one task to 5 people, TaskFlow creates 5 independent Task records. This allows:
- Each person's task to evolve separately (different status, completion time)
- Detailed per-person tracking
- Individual notifications

### Silent Notification Failures
All notification exceptions are caught and logged. Notification bugs never break task operations. The system always succeeds and logs failures for manual review.

## Troubleshooting

### Common Issues

**"Permission denied" when accessing tasks**
- Check your role (employees can only see own tasks)
- Managers can see direct reports; admins see all
- Verify the `role` field on your user

**Notifications not sending**
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env
- Check Gmail app password is set (not regular password)
- Verify Redis is running: `docker compose logs redis`
- Check application logs: `docker compose logs web`

**Token expired or login not working**
- Clear browser cookies and cache
- Check Redis connection: `docker compose exec redis redis-cli ping`
- Verify SECRET_KEY is set in .env
- Try re-logging in

**Database migration errors**
- Ensure PostgreSQL is running and accessible
- Check POSTGRES_* env vars in .env
- Run: `docker compose down && docker compose up -d db`
- Retry migrations

**Slow API responses**
- Check Redis connection
- Verify database indexes: `psql -c "\d+ tasks"`
- Monitor with: `docker stats`

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and commit: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a pull request
5. Ensure tests pass: `pytest`

## 📝 License

This project is proprietary. Unauthorized copying or distribution is prohibited.

## ✉️ Support

For issues, questions, or feature requests:
1. Check the [Full Documentation](./taskflow_documentation.md)
2. Review [Troubleshooting](#troubleshooting)
3. Open a GitHub issue with:
   - Detailed description of the problem
   - Steps to reproduce
   - Your environment (OS, Python version, etc.)
   - Error logs
