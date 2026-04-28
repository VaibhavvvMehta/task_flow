# TaskFlow Documentation

## Table of Contents

1. Quick Start & Overview
2. System Architecture
3. Getting Started
4. Authentication Guide
5. User Roles & Permissions
6. Managing Users
7. Task Management
8. Notifications
9. Reports & Analytics
10. API Reference
11. Database Schema
12. Deployment & Configuration

---

## Quick Start & Overview

**TaskFlow** is a modern task management platform built for organizations with hierarchical teams. It enables managers and executives to assign tasks, track progress, and generate performance insights—while employees can view their assignments and update their work status.

### What Can You Do?

- **Assign tasks** to individuals or groups with one click
- **Track progress** with real-time status updates and due date monitoring
- **Get notified** automatically when tasks are assigned, due, or updated
- **Generate reports** on team and individual performance with CSV/Excel export
- **Audit everything** with complete history of status changes and reassignments
- **Manage teams** through department hierarchies and manager-employee relationships

### Technology Stack

```
Backend:      Django 5.2 + Django REST Framework 3.17
Database:     PostgreSQL
Cache:        Redis
Authentication: JWT (stored in httpOnly cookies)
Frontend:     Tailwind CSS
Email:        Gmail SMTP
```

---

## System Architecture

### High-Level Flow

```
┌─────────────┐
│   Browser   │ ──→ Sends login credentials
└─────────────┘
       ↓
┌─────────────────────────────┐
│   Django REST Backend       │ ──→ Validates & issues JWT
│   (Port 8000)               │
└─────────────────────────────┘
       ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Redis     │  │    Gmail     │
│  (Data)      │  │  (Sessions)  │  │  (Email)     │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Core Modules

| Module | Purpose | Key Models |
|--------|---------|-----------|
| **Accounts** | User management, authentication, team hierarchy | User, roles |
| **Tasks** | Task creation, assignment, status tracking | Task, TaskStatusHistory, TaskAssignment |
| **Notifications** | Real-time alerts for task events | Notification |
| **Reports** | Performance analytics and exports | (Calculated on-the-fly) |

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- Django 5.2

### Environment Setup

Create a `.env` file in your project root with the following variables:

```bash
# Database
POSTGRES_DB=taskflow
POSTGRES_USER=taskflow_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# Django
SECRET_KEY=your-django-secret-key
DEBUG=True  # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1

# Frontend
CORS_ALLOWED_ORIGINS=http://localhost:8002
```

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Start the development server
python manage.py runserver

# In another terminal, start Tailwind
python manage.py tailwind start
```

The application will be available at `http://localhost:8000`

---

## Authentication Guide

### How Login Works

TaskFlow uses **JWT tokens stored in secure cookies**. This approach protects against XSS attacks because tokens are never accessible to JavaScript.

#### Step 1: User Logs In

```
POST /api/v1/auth/login/
```

**Send this:**
```json
{
  "email": "manager@company.com",
  "password": "securepassword123"
}
```

**You'll receive:**
```json
{
  "message": "Login successful",
  "role": "manager",
  "user": {
    "id": 1,
    "email": "manager@company.com",
    "full_name": "John Smith",
    "role": "manager",
    "department": "Engineering"
  }
}
```

Two cookies are automatically set in your browser:
- `access_token` — Valid for 70 minutes (used for API calls)
- `refresh_token` — Valid for 7 days (used to get new access token)

#### Step 2: Using the API

Once logged in, all subsequent requests automatically include your access token in the cookie. You don't need to add headers manually.

#### Step 3: Token Refresh

When your access token is about to expire, the frontend automatically calls:

```
POST /api/v1/auth/token/refresh/
```

This returns a fresh access token without requiring re-login.

#### Step 4: Logout

To log out:

```
POST /api/v1/auth/logout/
```

This:
- Blacklists both tokens in Redis (immediate logout, even if tokens haven't expired)
- Deletes both cookies from your browser
- Prevents token reuse

### Authentication Features

| Feature | How It Works |
|---------|-------------|
| **Cookie Storage** | Tokens stored in httpOnly cookies (JS cannot access) |
| **Token Lifetime** | Access: 70 min, Refresh: 7 days |
| **Logout Behavior** | Immediate via Redis blacklist (not just cookie deletion) |
| **Multi-Device Support** | Each device gets its own token pair |
| **Security** | Cookies marked as secure, SameSite=Lax |

---

## User Roles & Permissions

### Role Hierarchy

TaskFlow uses a **role-based access control (RBAC)** system with three (employee,manager,admin,) distinct roles:

```
┌─────────────┐
│ Employee    │  ← Can only see and update their own tasks
└─────────────┘

┌─────────────────────────────────────┐
│ Manager / Admin / CEO / CFO / CTO   │  ← Can manage team tasks
└─────────────────────────────────────┘
```

### Role Definitions

#### 1. **Employee** (Default)
- View only their assigned tasks
- Update status of only their own tasks
- View personal performance reports
- Cannot assign or create tasks

#### 2. **Manager**
- Create and assign tasks to direct reports
- View and manage all tasks assigned to their team
- Update task metadata (title, priority, due date)
- Soft-delete tasks
- View team performance reports
- Export team data

#### 3. **Admin**
- Same permissions as Manager
- Intended for system administrators
- Can view company-wide data when appropriate

#### 4. **CEO / CFO / CTO**
- Same API-level permissions as Manager/Admin
- Elevated role designation for executive tracking

### Permission Matrix

| Action | Employee | Manager / Admin / CEO / CFO / CTO |
|--------|----------|----------------------------------|
| **View own tasks** | ✅ | ✅ |
| **View team tasks** | ❌ | ✅ |
| **Create/assign tasks** | ❌ | ✅ |
| **Edit task details** | ❌ | ✅ |
| **Delete task (soft)** | ❌ | ✅ |
| **Update own task status** | ✅ | ✅ |
| **Update any task status** | ❌ | ✅ |
| **Reassign tasks** | ❌ | ✅ |
| **View team hierarchy** | Own dept | Company (admin) / Own dept (mgr) |
| **View performance reports** | Own only | Team + own |
| **Export reports** | Own tasks | Team + own |

---

## Managing Users

### User Profiles

Every user in TaskFlow has the following information:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| **Username** | Text | Yes | Unique identifier (150 chars max) |
| **Email** | Email | Yes | Unique; used for login |
| **First Name** | Text | No | Display in reports |
| **Last Name** | Text | No | Display in reports |
| **Role** | Choice | Yes | employee / manager / admin / ceo / cfo / cto |
| **Department** | Text | No | For team organization (100 chars max) |
| **Manager** | User | No | Self-referential; creates reporting structure |
| **Active** | Boolean | Yes | Deactivated accounts cannot log in |

### API Endpoints for User Management

#### Get Current User Info

```
GET /api/v1/auth/me/
```

**Returns:**
```json
{
  "id": 1,
  "email": "john@company.com",
  "username": "jsmith",
  "first_name": "John",
  "last_name": "Smith",
  "full_name": "John Smith",
  "role": "manager",
  "department": "Engineering",
  "is_active": true,
  "date_joined": "2024-01-15T10:30:00Z"
}
```

#### Update Your Profile

```
PATCH /api/v1/auth/me/
```

**You can only edit:** First name, Last name

**Send:**
```json
{
  "first_name": "Jonathan",
  "last_name": "Smith"
}
```

**Response:**
```json
{
  "message": "Updated: first_name, last_name",
  "full_name": "Jonathan Smith"
}
```

#### View Team Employees

```
GET /api/v1/users/employees/
```

**What you see depends on your role:**
- **Managers** → Only their direct reports
- **Admins** → All employees in the company
- **Employees** → Restricted

**Response:**
```json
[
  {
    "id": 5,
    "full_name": "Jane Doe",
    "email": "jane@company.com",
    "department": "Engineering"
  },
  {
    "id": 6,
    "full_name": "Bob Wilson",
    "email": "bob@company.com",
    "department": "Engineering"
  }
]
```

#### View Organization Hierarchy

```
GET /api/v1/users/hierarchy/?scope=team
```

**Query Parameters:**
- `scope=team` (default) → Show only your department
- `scope=company` → Show entire company (admin only)

**Response:**
```json
[
  {
    "department": "Engineering",
    "manager": {
      "id": 1,
      "full_name": "John Smith",
      "email": "john@company.com"
    },
    "employees": [
      {
        "id": 5,
        "full_name": "Jane Doe",
        "email": "jane@company.com"
      }
    ]
  }
]
```

---

## Task Management

### Understanding Tasks

A **task** in TaskFlow is a unit of work assigned to an employee. Managers create and assign tasks, while employees update their status and progress.

### Task Lifecycle

```
┌──────────┐    "in_progress"    ┌────────────────┐    "done"    ┌────────┐
│   TODO   │ ──────────────────→ │ IN PROGRESS    │ ───────────→ │  DONE  │
└──────────┘                      └────────────────┘              └────────┘
     ↑                                    ↓
     └────────────────── Can revert ─────┘
```

### Task Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| **Title** | Text | Yes | Task name (500 chars max) |
| **Description** | Long text | No | Detailed instructions |
| **Status** | Choice | Yes | todo / in_progress / done |
| **Priority** | Choice | Yes | low / medium / high (default: medium) |
| **Due Date** | Date | Yes | When task should be completed |
| **Assigned To** | User | Yes | Which employee owns it |
| **Created By** | User | Auto | Who created it (system-set) |
| **Is Deleted** | Boolean | Auto | Soft-deleted flag |
| **Done At** | Timestamp | Auto | When it was marked complete |

### Creating Tasks

#### Assign to One Person

```
POST /api/v1/tasks/
```

**Send:**
```json
{
  "title": "Design login page mockup",
  "description": "Create UI mockup for the new login flow in Figma",
  "priority": "high",
  "due_date": "2024-06-15",
  "assigned_to": 5
}
```

**Response (201 Created):**
```json
{
  "id": 42,
  "title": "Design login page mockup",
  "description": "Create UI mockup for the new login flow in Figma",
  "status": "todo",
  "priority": "high",
  "due_date": "2024-06-15",
  "assigned_to": 5,
  "assigned_to_detail": {
    "id": 5,
    "full_name": "Jane Doe",
    "email": "jane@company.com"
  },
  "created_by_name": "John Smith",
  "is_overdue": false,
  "days_overdue": 0,
  "created_at": "2024-06-01T10:30:00Z",
  "updated_at": "2024-06-01T10:30:00Z",
  "status_history": []
}
```

#### Bulk Assign to Multiple People

```
POST /api/v1/tasks/team-assign/
```

**Send:**
```json
{
  "title": "Quarterly training module",
  "description": "Complete the Q2 security training",
  "priority": "medium",
  "due_date": "2024-06-30",
  "assigned_to": [5, 6, 7, 8]
}
```

**What happens:**
- 4 separate Task records are created (one per user)
- 4 TaskAssignment records are created (tracking who assigned it)
- Each assignee gets a `task_assigned` notification

**Response (201 Created):**
```json
{
  "created": 4,
  "tasks": [
    {
      "id": 42,
      "title": "Quarterly training module",
      "assigned_to": 5,
      ...
    },
    {
      "id": 43,
      "title": "Quarterly training module",
      "assigned_to": 6,
      ...
    }
  ],
  "errors": []
}
```

### Viewing Tasks

#### My Tasks (What I'm Assigned To)

```
GET /api/v1/tasks/
```

**Query filters:**
- `?status=in_progress` → Only in-progress tasks
- `?priority=high` → Only high-priority tasks
- `?search=design` → Search by title

**Response:**
```json
[
  {
    "id": 42,
    "title": "Design login page mockup",
    "status": "in_progress",
    "priority": "high",
    "due_date": "2024-06-15",
    "is_overdue": false,
    "days_overdue": 0,
    "assigned_to_detail": {
      "id": 5,
      "full_name": "Jane Doe"
    },
    "created_by_name": "John Smith",
    "created_at": "2024-06-01T10:30:00Z"
  }
]
```

#### Manager's Own Tasks

```
GET /api/v1/tasks/manager/tasks/
```

Tasks assigned directly to you (the logged-in manager).

#### Manager's Team Tasks

```
GET /api/v1/tasks/manager/team/tasks/
```

**Response:** Each direct report with their tasks and summary:

```json
[
  {
    "id": 5,
    "full_name": "Jane Doe",
    "email": "jane@company.com",
    "department": "Engineering",
    "task_counts": {
      "total": 10,
      "todo": 3,
      "in_progress": 4,
      "done": 3,
      "overdue": 1
    },
    "tasks": [
      {
        "id": 42,
        "title": "Design login page mockup",
        "status": "in_progress",
        "priority": "high",
        ...
      }
    ]
  }
]
```

#### Single Task Details

```
GET /api/v1/tasks/{id}/
```

**Response:** Full task object with status history:

```json
{
  "id": 42,
  "title": "Design login page mockup",
  "description": "Create UI mockup for the new login flow in Figma",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2024-06-15",
  "assigned_to": 5,
  "assigned_to_detail": {
    "id": 5,
    "full_name": "Jane Doe",
    "email": "jane@company.com"
  },
  "created_by_name": "John Smith",
  "is_overdue": false,
  "days_overdue": 0,
  "created_at": "2024-06-01T10:30:00Z",
  "updated_at": "2024-06-05T14:22:00Z",
  "status_history": [
    {
      "old_status": "todo",
      "new_status": "in_progress",
      "changed_by": "Jane Doe",
      "changed_at": "2024-06-05T14:22:00Z"
    }
  ]
}
```

### Updating Tasks

#### Update Task Details (Managers Only)

```
PATCH /api/v1/tasks/{id}/
```

**You can edit:**
- Title
- Description
- Priority
- Due date

**Send:**
```json
{
  "priority": "medium",
  "due_date": "2024-06-20"
}
```

**Response:** Updated task object

#### Update Task Status

```
PATCH /api/v1/tasks/{id}/status/
```

**Send:**
```json
{
  "status": "in_progress"
}
```

**What happens automatically:**
- Creates a TaskStatusHistory record (audit trail)
- If transitioning to `done`: records completion timestamp
- If reverting from `done`: clears completion timestamp
- **Notifications:**
  - Employee updates status → Manager gets notified
  - Manager updates status → Employee gets notified

**Response:**
```json
{
  "message": "Status updated: todo → in_progress",
  "task": {
    "id": 42,
    "status": "in_progress",
    "updated_at": "2024-06-05T14:22:00Z",
    ...
  }
}
```

#### Reassign a Task (Managers Only)

```
PATCH /api/v1/tasks/{id}/assign/
```

**Send:**
```json
{
  "assigned_to": 8
}
```

**What happens:**
- Updates task assignment
- Creates TaskAssignment history record
- New assignee gets `task_assigned` notification

**Response:**
```json
{
  "message": "Task reassigned to Bob Wilson",
  "task": {
    "id": 42,
    "assigned_to": 8,
    "assigned_to_detail": {
      "id": 8,
      "full_name": "Bob Wilson"
    },
    ...
  }
}
```

### Deleting Tasks (Managers Only)

```
DELETE /api/v1/tasks/{id}/
```

**Important:** This is a **soft delete**. The task is hidden but not destroyed, preserving the audit trail.

**Response:**
```json
{
  "message": "Task deleted successfully."
}
```

---

## Notifications

### Notification Types

TaskFlow automatically sends notifications for important events:

| Event | Trigger | Recipient | Type |
|-------|---------|-----------|------|
| Task assigned | Manager creates task | Assigned employee | `task_assigned` |
| Task reassigned | Manager reassigns task | New assignee | `task_assigned` |
| Status changed | Employee updates status | Task creator (manager) | `task_status_changed` |
| Status changed | Manager updates status | Assigned employee | `task_status_changed` |
| Task overdue | (Planned feature) | Assigned employee | `task_overdue` |
| Due reminder | (Planned feature) | Assigned employee | `task_due_reminder` |
| Comment added | (Planned feature) | Task stakeholders | `task_comment_added` |

### Notification Fields

| Field | Type | Notes |
|-------|------|-------|
| **Type** | Choice | task_assigned, task_overdue, task_status_changed, etc. |
| **Title** | Text | Short label (e.g., "New task assigned") |
| **Message** | Text | Full content |
| **Task ID** | Reference | Which task triggered it (optional) |
| **Is Read** | Boolean | Whether user has viewed it |
| **Created At** | Timestamp | When notification was generated |

### Notification API

#### Get All Notifications

```
GET /api/v1/notifications/
```

**Response:** Last 50 notifications (newest first):

```json
[
  {
    "id": 1,
    "type": "task_assigned",
    "title": "New task assigned",
    "message": "John Smith assigned you 'Design login page mockup'",
    "task_id": 42,
    "is_read": false,
    "created_at": "2024-06-05T10:30:00Z"
  },
  {
    "id": 2,
    "type": "task_status_changed",
    "title": "Task status updated",
    "message": "Jane Doe changed 'Design login page mockup' to in_progress",
    "task_id": 42,
    "is_read": true,
    "created_at": "2024-06-05T14:22:00Z"
  }
]
```

#### Get Unread Count

```
GET /api/v1/notifications/unread-count/
```

**Response:** Used for the notification bell badge:

```json
{
  "count": 3
}
```

#### Filter by Read Status

```
GET /api/v1/notifications/?unread=true
```

Returns only unread notifications.

#### Mark as Read

```
PATCH /api/v1/notifications/{id}/read/
```

**Response:**
```json
{
  "message": "Marked as read."
}
```

#### Mark All as Read

```
PATCH /api/v1/notifications/mark-all-read/
```

**Response:**
```json
{
  "message": "5 notification(s) marked as read."
}
```

---

## Reports & Analytics

### Performance Reports

TaskFlow generates real-time performance reports from your task data. No separate reporting database—everything is calculated on-demand from tasks.

#### My Performance

```
GET /api/v1/reports/my-performance/
```

**Who can see:**
- Employees → Only their own
- Managers → Their own + direct reports
- Admins → Anyone

**Optional param:** `?user_id=5` (to view someone else's performance)

**Response:**
```json
{
  "total_tasks": 15,
  "done_tasks": 9,
  "completion_rate": 60.0,
  "on_time_count": 7,
  "late_count": 2,
  "user": {
    "id": 5,
    "full_name": "Jane Doe",
    "role": "employee"
  }
}
```

**Metrics explained:**
- **Completion Rate** = (Done tasks / Total tasks) × 100
- **On Time** = Completed on or before due date
- **Late** = Completed after due date

#### Team Summary

```
GET /api/v1/reports/team-summary/?range=all
```

**Managers only** (for direct reports)

**Range options:**
- `?range=all` (default) → All time
- `?range=7` → Last 7 days
- `?range=30` → Last 30 days
- `?range=month` → Current calendar month

**Response:**
```json
{
  "total_tasks": 50,
  "done_tasks": 35,
  "completion_rate": 70.0,
  "total_overdue": 2,
  "by_employee": [
    {
      "id": 5,
      "full_name": "Jane Doe",
      "department": "Engineering",
      "total_tasks": 10,
      "done_tasks": 9,
      "in_progress_tasks": 1,
      "todo_tasks": 0,
      "overdue_tasks": 0,
      "completion_rate": 90.0
    }
  ]
}
```

### Export Data

#### Export to CSV or Excel

```
GET /api/v1/reports/export/?format=excel&type=my_tasks&range=30
```

**Parameters:**

| Param | Options | Required |
|-------|---------|----------|
| `format` | csv, excel | No (default: csv) |
| `type` | my_tasks, team | Yes |
| `range` | all, 7, 30, month | No (default: all) |

**My Tasks Export Columns:**
- Title
- Description
- Priority
- Status
- Due Date
- Completed At
- Created At

**Team Export Columns:**
- Employee Name
- Department
- Total Tasks
- Done
- In Progress
- To Do
- Overdue
- Completion Rate (%)

**Response:** File download with correct MIME type and filename

---

## API Reference

### Complete Endpoint Map

#### Authentication Endpoints

| Method | Path | Purpose | Auth Required |
|--------|------|---------|--------------|
| POST | `/api/v1/auth/login/` | Log in with email & password | No |
| POST | `/api/v1/auth/logout/` | Log out and blacklist tokens | No (cookie-based) |
| POST | `/api/v1/auth/token/refresh/` | Get new access token | No (cookie-based) |
| GET | `/api/v1/auth/me/` | Get current user profile | Yes |
| PATCH | `/api/v1/auth/me/` | Update own profile | Yes |

#### User Management Endpoints

| Method | Path | Purpose | Auth Required | Role Required |
|--------|------|---------|--------------|---------------|
| GET | `/api/v1/users/employees/` | List team employees | Yes | Elevated only |
| GET | `/api/v1/users/hierarchy/` | View org hierarchy | Yes | All |

#### Task Endpoints

| Method | Path | Purpose | Auth Required | Role Required |
|--------|------|---------|--------------|---------------|
| GET | `/api/v1/tasks/` | Get my tasks | Yes | All |
| POST | `/api/v1/tasks/team-assign/` | Assign to multiple people | Yes | Elevated only |
| GET | `/api/v1/tasks/manager/tasks/` | Get my (manager's) tasks | Yes | Elevated only |
| GET | `/api/v1/tasks/manager/team/tasks/` | Get team's tasks | Yes | Elevated only |
| GET | `/api/v1/tasks/{id}/` | Get task details | Yes | Own (emp) / Any (elevated) |
| PATCH | `/api/v1/tasks/{id}/` | Edit task | Yes | Elevated only |
| DELETE | `/api/v1/tasks/{id}/` | Delete task (soft) | Yes | Elevated only |
| PATCH | `/api/v1/tasks/{id}/status/` | Update status | Yes | Own (emp) / Any (elevated) |
| PATCH/PUT | `/api/v1/tasks/{id}/assign/` | Reassign task | Yes | Elevated only |

#### Notification Endpoints

| Method | Path | Purpose | Auth Required |
|--------|------|---------|--------------|
| GET | `/api/v1/notifications/` | Get all notifications | Yes |
| GET | `/api/v1/notifications/unread-count/` | Get unread count | Yes |
| PATCH | `/api/v1/notifications/{id}/read/` | Mark as read | Yes |
| PATCH | `/api/v1/notifications/mark-all-read/` | Mark all as read | Yes |

#### Report Endpoints

| Method | Path | Purpose | Auth Required | Role Required |
|--------|------|---------|--------------|---------------|
| GET | `/api/v1/reports/my-performance/` | Performance analytics | Yes | All |
| GET | `/api/v1/reports/team-summary/` | Team analytics | Yes | Elevated only |
| GET | `/api/v1/reports/export/` | Export to CSV/Excel | Yes | team type: elevated only |

---

## Database Schema

### Entity Relationship Diagram

```
┌──────────────────┐
│      User        │
├──────────────────┤
│ id (PK)          │
│ username         │
│ email            │
│ role             │
│ department       │
│ manager_id (FK)  │ ──┐
└──────────────────┘   │
        ↑              │
        └──────────────┘
        
        │
        │ assigned_to
        │ created_by
        ↓
┌──────────────────┐
│      Task        │
├──────────────────┤
│ id (PK)          │
│ title            │
│ description      │
│ status           │
│ priority         │
│ due_date         │
│ assigned_to (FK) │
│ created_by (FK)  │
│ is_deleted       │
│ done_at          │
│ created_at       │
│ updated_at       │
└──────────────────┘
        │
        │ 1:N
        ├─────────────────────┐
        │                     │
        ↓                     ↓
┌────────────────────┐   ┌──────────────────┐
│ TaskStatusHistory  │   │  TaskAssignment  │
├────────────────────┤   ├──────────────────┤
│ id (PK)            │   │ id (PK)          │
│ task_id (FK)       │   │ task_id (FK)     │
│ changed_by (FK)    │   │ assigned_to (FK) │
│ old_status         │   │ assigned_by (FK) │
│ new_status         │   │ assigned_at      │
│ changed_at         │   └──────────────────┘
└────────────────────┘

┌──────────────────────┐
│  Notification        │
├──────────────────────┤
│ id (PK)              │
│ user_id (FK)         │
│ type                 │
│ title                │
│ message              │
│ task_id (FK, null)   │
│ is_read              │
│ created_at           │
└──────────────────────┘
```

### Key Model Details

#### User Model

```python
class User(AbstractUser):
    role = CharField(
        max_length=20,
        choices=['employee', 'manager', 'admin', 'ceo', 'cfo', 'cto'],
        default='employee'
    )
    department = CharField(max_length=100, blank=True, null=True)
    manager = ForeignKey('self', SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
```

#### Task Model

```python
class Task(Model):
    title = CharField(max_length=500)
    description = TextField(blank=True, null=True)
    status = CharField(
        max_length=20,
        choices=['todo', 'in_progress', 'done'],
        default='todo'
    )
    priority = CharField(
        max_length=20,
        choices=['low', 'medium', 'high'],
        default='medium'
    )
    due_date = DateField()
    assigned_to = ForeignKey(User, CASCADE, related_name='assigned_tasks')
    created_by = ForeignKey(User, CASCADE, related_name='created_tasks')
    is_deleted = BooleanField(default=False)
    done_at = DateTimeField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

#### Notification Model

```python
class Notification(Model):
    TYPE_CHOICES = [
        ('task_assigned', 'Task Assigned'),
        ('task_overdue', 'Task Overdue'),
        ('task_due_reminder', 'Task Due Reminder'),
        ('task_status_changed', 'Task Status Changed'),
        ('task_comment_added', 'Comment Added'),
    ]
    
    user = ForeignKey(User, CASCADE, related_name='notifications')
    type = CharField(max_length=30, choices=TYPE_CHOICES)
    title = CharField(max_length=255)
    message = TextField()
    task = ForeignKey(Task, CASCADE, null=True, blank=True)
    is_read = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
```

## Key Design Decisions

### Why JWT in Cookies?

Traditional methods store tokens in Authorization headers, but JavaScript can access them (XSS vulnerability). TaskFlow stores tokens in **httpOnly cookies**, which JavaScript cannot access, making XSS attacks less dangerous.

### Why Redis Blacklist?

Token expiry doesn't allow immediate logout. If you log out, the old token is still valid until it expires. TaskFlow stores invalidated JTIs (token IDs) in Redis, enabling instant logout.

### Why Soft Deletes?

Tasks are never physically deleted—they're marked with `is_deleted=True`. This preserves the complete audit trail, allowing historical analysis and recovery if needed.

### Why TaskStatusHistory?

Every status change is recorded with the actor, timestamp, and old/new values. This enables compliance audits and helps managers understand the complete lifecycle of work.

### Why Separate Tasks for Bulk Assign?

When you bulk-assign one task to 5 people, TaskFlow creates 5 separate Task records. This allows each person's task to evolve independently (different status, due date, etc.) while remaining semantically related.

### Why Silence Notification Failures?

A notification bug should never break task operations. All notification exceptions are caught and logged, ensuring task creation/updates always succeed.


Vaibhav Mehta
