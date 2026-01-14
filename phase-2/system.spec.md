# System Design Specification — Phase 2

**Project**: Todo Full-Stack Web Application
**Phase**: 2 — System Design & Architecture
**Created**: 2026-01-12
**Status**: Draft

---

## 1. System Context

### 1.1 Purpose

Transform the Phase-1 in-memory console Todo application into a production-ready, multi-user, persistent full-stack web application with authentication, database support, and AI-assisted task management capabilities.

### 1.2 System Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                         EXTERNAL ACTORS                         │
├─────────────────────────────────────────────────────────────────┤
│  End Users          AI Services (Claude)      Database (Neon)   │
│  (Web Browser)      (Task Intelligence)       (PostgreSQL)      │
└────────┬───────────────────┬─────────────────────┬──────────────┘
         │                   │                     │
         ▼                   ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TODO APP SYSTEM (Phase-2)                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │   Frontend      │◄──►│    Backend      │◄──► External APIs   │
│  │   (Next.js)     │    │   (FastAPI)     │                     │
│  └─────────────────┘    └─────────────────┘                     │
│           │                     │                               │
│           └─────────┬───────────┘                               │
│                     ▼                                           │
│           ┌─────────────────┐                                   │
│           │   Auth Layer    │                                   │
│           │ (Better Auth)   │                                   │
│           └─────────────────┘                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 External Dependencies

| Dependency         | Type             | Purpose                        | Owner           |
|--------------------|------------------|--------------------------------|-----------------|
| Neon PostgreSQL    | Database Service | Persistent data storage        | Neon (cloud)    |
| Claude API         | AI Service       | Task intelligence/suggestions  | Anthropic       |
| Better Auth        | Auth Library     | User authentication            | Open Source     |

### 1.4 Actors

| Actor | Description | Interactions |
|-------|-------------|--------------|
| End User | Registered user managing personal tasks | CRUD tasks, auth, AI suggestions |
| Anonymous User | Visitor without account | View public pages, register |
| AI Service | Claude API for task intelligence | Provide suggestions on request |
| System Admin | Ops/maintenance role | Monitor, configure, maintain |

---

## 2. System Components

### 2.1 Component Architecture

| Component    | Responsibility                                | Interfaces                                  |
|--------------|-----------------------------------------------|---------------------------------------------|
| Web Frontend | User interface, form handling, display        | REST API calls to Backend                   |
| API Backend  | Business logic, validation, orchestration     | REST endpoints, DB queries, AI service      |
| Auth Service | User registration, login, session management  | JWT tokens, session cookies                 |
| Database     | Persistent storage of users and tasks         | SQL queries via ORM                         |
| AI Module    | Task intelligence, suggestions                | API calls to Claude                         |

### 2.2 Component Interactions

```
┌──────────────┐     REST/JSON      ┌──────────────┐
│   Frontend   │◄──────────────────►│   Backend    │
│   (Next.js)  │                    │  (FastAPI)   │
└──────────────┘                    └──────┬───────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
            ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
            │  Auth Layer  │      │   Database   │      │  AI Service  │
            │ (Better Auth)│      │ (PostgreSQL) │      │   (Claude)   │
            └──────────────┘      └──────────────┘      └──────────────┘
```

### 2.3 Data Flow

1. **User Request → Frontend**: User interacts with web UI
2. **Frontend → Backend**: REST API call with JWT token
3. **Backend → Auth**: Validate JWT, extract user identity
4. **Backend → Database**: Execute query with user scope
5. **Backend → AI** (optional): Request task suggestions
6. **Backend → Frontend**: JSON response
7. **Frontend → User**: Render updated UI

---

## 3. Tooling Integration (AI Models + Memory)

### 3.1 AI Integration Design

| Capability               | Trigger                                  | Fallback                     |
|--------------------------|------------------------------------------|------------------------------|
| Task suggestions         | User requests help while creating task   | Disabled gracefully          |
| Priority recommendations | User requests task prioritization        | Manual prioritization only   |
| Smart categorization     | Task creation/update (opt-in)            | No auto-categorization       |

### 3.2 Memory Architecture

| Memory Type | Storage | Scope | Persistence |
|-------------|---------|-------|-------------|
| Session Memory | JWT Token | User session | Until logout/expiry |
| User Data | PostgreSQL | Per-user | Permanent |
| Task Data | PostgreSQL | Per-user | Permanent |
| AI Context | Request-scoped | Single API call | None (stateless) |

### 3.3 AI Model Configuration

- **Model**: Claude (Anthropic)
- **Context Window**: Single request (no cross-session memory)
- **Rate Limiting**: Respect API quotas, queue excess requests
- **Timeout**: 30 seconds per request
- **Retry Policy**: 3 attempts with exponential backoff

### 3.4 AI Safety Boundaries

| Rule | Enforcement |
|------|-------------|
| AI suggestions are advisory only | User must confirm all actions |
| No automatic task creation/deletion | AI cannot modify data without user action |
| User data isolation | Task data sent to AI scoped to requesting user only |
| Credential protection | Passwords/tokens NEVER sent to AI |
| Graceful degradation | Core app works without AI |

---

## 4. Safety & Control Policies

### 4.1 Authentication Controls

| Control | Policy |
|---------|--------|
| Password Storage | MUST be hashed (bcrypt/argon2) before storage |
| JWT Expiration | Tokens MUST expire (default: 24 hours) |
| Rate Limiting | Failed logins limited to 5/minute per IP |
| Session Invalidation | Logout MUST invalidate all active tokens |
| Password Requirements | Minimum 8 characters, complexity rules |

### 4.2 Authorization Controls

| Control | Policy |
|---------|--------|
| Resource Ownership | All task operations MUST verify user ownership |
| JWT Validation | Every protected endpoint MUST validate JWT |
| Frontend Isolation | Direct DB access from frontend PROHIBITED |
| Role Enforcement | Users can only access own resources |

### 4.3 Data Protection

| Control | Policy |
|---------|--------|
| Transport Security | All connections MUST use TLS/HTTPS |
| Database Encryption | Connection strings encrypted, data at rest encrypted |
| Log Sanitization | Passwords, tokens, PII MUST NOT appear in logs |
| Error Messages | No internal details leaked to users |
| Data Isolation | API responses MUST NOT leak other users' data |

### 4.4 AI Safety Controls

| Control | Policy |
|---------|--------|
| Credential Exclusion | AI requests MUST NOT include passwords/secrets |
| User Consent | AI features require explicit user action |
| Output Validation | AI responses sanitized before display |
| Failure Handling | AI errors MUST NOT break core functionality |

### 4.5 Operational Controls

| Control | Policy |
|---------|--------|
| Monitoring | All API endpoints logged with request ID |
| Alerting | Error rate > 5% triggers alert |
| Backup | Database backed up daily, 30-day retention |
| Incident Response | Documented runbook for common failures |

---

## 5. Future Phase Dependencies

### 5.1 Phase-3 Planned Features

| Future Feature              | Phase-2 Dependency                         | Notes |
|-----------------------------|-------------------------------------------|-------|
| Task sharing/collaboration  | User model, task ownership model          | Requires ACL extension |
| Task categories/tags        | Task model extensibility                  | Add metadata field |
| Recurring tasks             | Task model, scheduling infrastructure     | Add recurrence rules |
| Mobile app                  | REST API design, auth token portability   | JWT works cross-platform |
| Offline support             | Sync protocol design                      | Add conflict resolution |
| Team workspaces             | User model, org hierarchy                 | Multi-tenant extension |

### 5.2 Extension Points (Built into Phase-2)

| Extension Point | Design Decision | Future Use |
|-----------------|-----------------|------------|
| Task metadata field | JSON/JSONB column in Task table | Categories, tags, custom fields |
| API versioning | `/api/v1/` prefix | Backward-compatible evolution |
| Auth token claims | Extensible JWT payload | Roles, permissions, org ID |
| Webhook support | Event emission hooks in backend | Integrations, notifications |
| Plugin architecture | Service interface abstractions | Custom AI providers, storage |

### 5.3 Migration Path

```
Phase-2 (Current)          Phase-3 (Planned)          Phase-4 (Future)
─────────────────          ─────────────────          ────────────────
Single-user tasks    →     Shared tasks         →     Team workspaces
Basic auth           →     OAuth providers      →     SSO/SAML
AI suggestions       →     AI automation        →     Custom AI models
Web only             →     Mobile apps          →     Desktop apps
```

---

## 6. Key Entities

### 6.1 User

| Attribute | Type | Constraints |
|-----------|------|-------------|
| id | UUID | Primary key, immutable |
| email | String | Unique, validated format |
| password_hash | String | Never exposed, hashed |
| created_at | Timestamp | Auto-set on creation |
| updated_at | Timestamp | Auto-set on modification |

### 6.2 Task

| Attribute | Type | Constraints |
|-----------|------|-------------|
| id | UUID | Primary key, immutable |
| user_id | UUID | Foreign key to User, required |
| title | String | Required, max 255 chars |
| description | String | Optional, max 4000 chars |
| is_completed | Boolean | Default: false |
| created_at | Timestamp | Auto-set on creation |
| updated_at | Timestamp | Auto-set on modification |
| metadata | JSON | Optional, extensible |

### 6.3 Entity Relationships

```
┌──────────┐       1:N       ┌──────────┐
│   User   │────────────────►│   Task   │
└──────────┘                 └──────────┘
     │
     │ owns
     ▼
  [Tasks scoped to owner only]
```

---

## 7. Success Criteria

| ID | Criterion | Metric | Target |
|----|-----------|--------|--------|
| SC-001 | Registration speed | Time to complete | < 60 seconds |
| SC-002 | Task CRUD reliability | Error rate | 0% for valid operations |
| SC-003 | Data persistence | Data loss rate | 0% across sessions |
| SC-004 | Concurrent users | Supported load | 100 users |
| SC-005 | Multi-user isolation | Cross-user access | 0 violations |
| SC-006 | AI degradation | Core function availability | 100% when AI down |
| SC-007 | Onboarding success | First task creation | 90% within 2 minutes |
| SC-008 | Page performance | Load time | < 3 seconds |

---

## 8. Assumptions

- Users have modern web browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)
- Users have stable internet connection for web application access
- Neon PostgreSQL provides 99.9% uptime SLA
- Claude API has rate limits that may affect AI feature availability during high usage
- Email is the sole authentication identifier (no username or phone alternatives)
- Single-language interface (English) for Phase-2
- No mobile-native app in Phase-2 (responsive web only)

---

## 9. Agents

### 9.1 Agent Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR AGENT                         │
│              (Routes requests, coordinates agents)              │
└───────────┬─────────────┬─────────────┬─────────────┬──────────┘
            │             │             │             │
            ▼             ▼             ▼             ▼
      ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
      │   Auth   │  │   Task   │  │   User   │  │    AI    │
      │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │
      └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

---

### 9.2 OrchestratorAgent

| Property | Value |
|----------|-------|
| **name** | `OrchestratorAgent` |
| **description** | Central coordinator that routes incoming requests to appropriate agents, manages workflow sequencing, and aggregates responses. |

**responsibilities**:
- Route incoming API requests to appropriate domain agents
- Validate request structure before delegation
- Coordinate multi-agent workflows (e.g., auth → task operations)
- Aggregate responses from multiple agents
- Handle cross-cutting concerns (logging, error handling)

**inputs**:
| Input | Type | Description |
|-------|------|-------------|
| `request` | HTTPRequest | Incoming API request with headers, body, params |
| `context` | RequestContext | User session, request ID, timestamp |

**outputs**:
| Output | Type | Description |
|--------|------|-------------|
| `response` | HTTPResponse | Aggregated response to client |
| `audit_log` | AuditEntry | Request/response audit trail |

**assigned_skills**:
- `request_routing` — Parse and route requests by path/method
- `workflow_coordination` — Sequence multi-step operations
- `response_aggregation` — Combine agent outputs
- `error_handling` — Standardize error responses

**calls**:
- `AuthAgent.validate_token()`
- `AuthAgent.authenticate()`
- `TaskAgent.*`
- `UserAgent.*`
- `AIAgent.*`

**tools**:
- `Logger` — Structured logging
- `MetricsCollector` — Request metrics
- `RateLimiter` — Request throttling

---

### 9.3 AuthAgent

| Property | Value |
|----------|-------|
| **name** | `AuthAgent` |
| **description** | Handles all authentication and authorization operations including login, registration, token management, and permission validation. |

**responsibilities**:
- Authenticate users via email/password
- Generate and validate JWT tokens
- Manage user sessions
- Enforce rate limiting on auth endpoints
- Hash and verify passwords

**inputs**:
| Input | Type | Description |
|-------|------|-------------|
| `credentials` | LoginCredentials | Email and password for login |
| `registration_data` | RegistrationData | Email, password for signup |
| `token` | JWT | Token for validation |
| `user_id` | UUID | User ID for session operations |

**outputs**:
| Output | Type | Description |
|--------|------|-------------|
| `auth_result` | AuthResult | Success/failure with token or error |
| `user_identity` | UserIdentity | Validated user ID and claims |
| `session` | Session | Active session metadata |

**assigned_skills**:
- `password_hashing` — Secure password hashing (bcrypt/argon2)
- `jwt_generation` — Create signed JWT tokens
- `jwt_validation` — Verify and decode JWT tokens
- `rate_limiting` — Track and enforce login attempt limits
- `session_management` — Create, refresh, invalidate sessions

**calls**:
- `UserAgent.get_user_by_email()`
- `UserAgent.create_user()`

**tools**:
- `PasswordHasher` — bcrypt/argon2 implementation
- `JWTProvider` — Token signing and verification
- `RateLimitStore` — Track failed attempts
- `SessionStore` — Session state management

---

### 9.4 TaskAgent

| Property | Value |
|----------|-------|
| **name** | `TaskAgent` |
| **description** | Manages all task-related CRUD operations with user-scoped data isolation and validation. |

**responsibilities**:
- Create new tasks for authenticated users
- Retrieve tasks scoped to owner
- Update task properties (title, description, status)
- Delete tasks with ownership verification
- Enforce user isolation at data layer

**inputs**:
| Input | Type | Description |
|-------|------|-------------|
| `user_id` | UUID | Authenticated user (from AuthAgent) |
| `task_data` | TaskCreate | Title, description for new task |
| `task_id` | UUID | Task identifier for read/update/delete |
| `update_data` | TaskUpdate | Fields to update |
| `filters` | TaskFilters | Optional filters (status, date range) |

**outputs**:
| Output | Type | Description |
|--------|------|-------------|
| `task` | Task | Single task object |
| `tasks` | Task[] | List of tasks |
| `operation_result` | OperationResult | Success/failure with affected count |

**assigned_skills**:
- `task_creation` — Validate and persist new tasks
- `task_retrieval` — Query tasks with user scoping
- `task_update` — Modify task properties
- `task_deletion` — Remove tasks with ownership check
- `ownership_validation` — Verify user owns resource

**calls**:
- `AIAgent.get_suggestions()` (optional)

**tools**:
- `TaskRepository` — Database access layer
- `Validator` — Input validation
- `EventEmitter` — Publish task events

---

### 9.5 UserAgent

| Property | Value |
|----------|-------|
| **name** | `UserAgent` |
| **description** | Manages user account operations including profile management and account settings. |

**responsibilities**:
- Create new user accounts
- Retrieve user profile data
- Update user preferences
- Handle account deletion requests
- Validate email uniqueness

**inputs**:
| Input | Type | Description |
|-------|------|-------------|
| `user_id` | UUID | User identifier |
| `email` | String | Email for lookup or creation |
| `profile_data` | ProfileUpdate | Fields to update |
| `registration_data` | RegistrationData | New user data |

**outputs**:
| Output | Type | Description |
|--------|------|-------------|
| `user` | User | User profile (password excluded) |
| `exists` | Boolean | Email existence check result |
| `operation_result` | OperationResult | Success/failure status |

**assigned_skills**:
- `user_creation` — Create new user records
- `user_retrieval` — Fetch user by ID or email
- `profile_update` — Modify user profile
- `email_validation` — Check email format and uniqueness
- `account_deletion` — Soft/hard delete with cascade

**calls**:
- `TaskAgent.delete_user_tasks()` (for account deletion)

**tools**:
- `UserRepository` — Database access layer
- `EmailValidator` — Format and deliverability check
- `Anonymizer` — PII removal for deletion

---

### 9.6 AIAgent

| Property | Value |
|----------|-------|
| **name** | `AIAgent` |
| **description** | Provides AI-powered task intelligence including suggestions, prioritization, and smart categorization. Designed for graceful degradation. |

**responsibilities**:
- Generate task suggestions based on context
- Provide priority recommendations
- Suggest task categorization
- Handle AI service failures gracefully
- Sanitize AI outputs before returning

**inputs**:
| Input | Type | Description |
|-------|------|-------------|
| `task_context` | TaskContext | Current task title/description |
| `user_tasks` | Task[] | User's existing tasks for context |
| `request_type` | AIRequestType | suggestion \| prioritization \| categorization |

**outputs**:
| Output | Type | Description |
|--------|------|-------------|
| `suggestions` | Suggestion[] | AI-generated suggestions |
| `priorities` | PriorityRecommendation[] | Ordered task priorities |
| `categories` | CategorySuggestion[] | Suggested categories |
| `available` | Boolean | AI service availability status |

**assigned_skills**:
- `suggestion_generation` — Create task suggestions via Claude
- `priority_analysis` — Analyze and rank task priorities
- `category_inference` — Suggest task categories
- `context_building` — Build prompts from task data
- `output_sanitization` — Clean and validate AI responses
- `graceful_degradation` — Return empty results on failure

**calls**:
- None (leaf agent)

**tools**:
- `ClaudeClient` — Anthropic API client
- `PromptBuilder` — Construct AI prompts
- `ResponseParser` — Parse and validate AI output
- `CircuitBreaker` — Prevent cascade failures
- `RateLimitManager` — Respect API quotas

---

### 9.7 Agent Interaction Matrix

| Caller | AuthAgent | TaskAgent | UserAgent | AIAgent |
|--------|-----------|-----------|-----------|---------|
| **Orchestrator** | ✓ validate, authenticate | ✓ all CRUD | ✓ profile ops | ✓ suggestions |
| **AuthAgent** | — | — | ✓ get/create user | — |
| **TaskAgent** | — | — | — | ✓ suggestions |
| **UserAgent** | — | ✓ delete tasks | — | — |
| **AIAgent** | — | — | — | — |

---

### 9.8 Agent Communication Protocol

```yaml
request:
  id: UUID
  timestamp: ISO8601
  source_agent: string
  target_agent: string
  operation: string
  payload: object
  context:
    user_id: UUID | null
    request_id: UUID
    correlation_id: UUID

response:
  id: UUID
  request_id: UUID
  timestamp: ISO8601
  status: success | error
  payload: object
  error:
    code: string
    message: string
    details: object | null
```

---

## 10. Glossary

| Term | Definition |
|------|------------|
| JWT | JSON Web Token - stateless authentication token |
| CRUD | Create, Read, Update, Delete operations |
| ORM | Object-Relational Mapping - database abstraction |
| SLA | Service Level Agreement |
| TLS | Transport Layer Security - encrypted connections |
| ACL | Access Control List - permission management |
| Agent | Autonomous component with defined responsibilities, inputs, outputs |
| Skill | Reusable capability assigned to an agent |
| Circuit Breaker | Pattern to prevent cascade failures in distributed systems |
