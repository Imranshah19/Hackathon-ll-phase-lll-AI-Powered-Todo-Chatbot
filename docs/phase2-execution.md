# Phase 2: Backend + Frontend Implementation

## Overview

Phase 2 implemented the full-stack web application with authentication, task management, and database persistence.

## Backend Implementation

### Structure
```
backend/src/
├── api/
│   ├── auth.py         # Register, Login, Me endpoints
│   └── tasks.py        # CRUD endpoints
├── models/
│   ├── user.py         # User entity + schemas
│   └── task.py         # Task entity + schemas
├── auth/
│   ├── jwt.py          # Token creation/verification
│   ├── password.py     # Argon2 hashing
│   └── dependencies.py # FastAPI DI
├── db.py               # Database connection
└── main.py             # App factory + middleware
```

### Database Schema

**Users Table**
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, auto-generated |
| email | VARCHAR | UNIQUE, NOT NULL |
| password_hash | VARCHAR | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

**Tasks Table**
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, auto-generated |
| user_id | UUID | FK → users.id |
| title | VARCHAR(255) | NOT NULL |
| description | TEXT | nullable |
| is_completed | BOOLEAN | default FALSE |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

### API Endpoints

**Authentication**
- `POST /api/auth/register` - Create user account
- `POST /api/auth/login` - Get JWT token
- `GET /api/auth/me` - Get current user

**Tasks**
- `GET /api/tasks` - List tasks (filter: completed, search)
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get task by ID
- `PATCH /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Security Features
- Argon2id password hashing
- JWT tokens (24-hour expiration)
- User isolation on all queries
- Input validation via Pydantic

## Frontend Implementation

### Structure
```
frontend/src/
├── app/
│   ├── page.tsx        # Landing page
│   ├── signin/         # Login page
│   ├── signup/         # Registration page
│   └── tasks/          # Task management
├── components/
│   ├── TaskList.tsx    # Task list display
│   ├── TaskItem.tsx    # Single task
│   ├── TaskForm.tsx    # Create/edit form
│   └── TaskFilters.tsx # Filter controls
└── lib/
    ├── api.ts          # API client
    └── auth.tsx        # Auth context
```

### Pages

| Route | Description |
|-------|-------------|
| `/` | Landing page |
| `/signin` | Login form |
| `/signup` | Registration form |
| `/tasks` | Task dashboard |
| `/tasks/{id}/edit` | Edit task |

### Features
- JWT token management (cookies)
- Protected routes
- Real-time filtering
- Responsive design
- Loading states
- Error handling

## Database Migrations

**Initial Migration** (`8335fb1bfb29_initial_schema.py`)
- Creates `users` table
- Creates `tasks` table
- Adds index on `tasks.user_id`

```bash
# Run migrations
cd backend
alembic upgrade head
```

## Testing

### Test Structure
```
backend/tests/
├── unit/           # Isolated tests
├── integration/    # Database tests
└── contract/       # Schema validation
```

### Run Tests
```bash
cd backend
pytest
pytest --cov=src  # With coverage
```

## Success Criteria

- [x] User registration/login working
- [x] JWT authentication implemented
- [x] Task CRUD complete
- [x] User isolation enforced
- [x] Frontend pages functional
- [x] API integration working
- [x] Database migrations created
