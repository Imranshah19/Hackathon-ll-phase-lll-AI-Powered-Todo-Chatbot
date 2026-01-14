# Agents Specification — Phase 2

**Project**: Todo Full-Stack Web Application
**Phase**: 2 — System Design & Architecture
**Created**: 2026-01-14
**Status**: Draft

---

## 1. Overview

Agents are autonomous components with defined responsibilities, inputs, outputs, and assigned skills. This specification details the agent architecture for Phase 2.

### 1.1 Agent Schema

```yaml
Agent:
  name: string                    # Unique identifier (PascalCase)
  description: string             # What the agent does
  responsibilities: string[]      # List of duties
  inputs: InputSchema[]           # Typed inputs
  outputs: OutputSchema[]         # Typed outputs
  assigned_skills: string[]       # Skills this agent uses
  calls: string[]                 # Other agents this agent invokes
  tools: string[]                 # External tools/services used
```

### 1.2 Agent Hierarchy

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

## 2. OrchestratorAgent

| Property | Value |
|----------|-------|
| **name** | `OrchestratorAgent` |
| **description** | Central coordinator that routes incoming requests to appropriate agents, manages workflow sequencing, and aggregates responses. |

### Responsibilities

- Route incoming API requests to appropriate domain agents
- Validate request structure before delegation
- Coordinate multi-agent workflows (e.g., auth → task operations)
- Aggregate responses from multiple agents
- Handle cross-cutting concerns (logging, error handling)

### Inputs

| Input | Type | Description |
|-------|------|-------------|
| `request` | HTTPRequest | Incoming API request with headers, body, params |
| `context` | RequestContext | User session, request ID, timestamp |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `response` | HTTPResponse | Aggregated response to client |
| `audit_log` | AuditEntry | Request/response audit trail |

### Assigned Skills

| Skill | Purpose |
|-------|---------|
| `request_routing` | Parse and route requests by path/method |
| `workflow_coordination` | Sequence multi-step operations |
| `response_aggregation` | Combine agent outputs |
| `error_handling` | Standardize error responses |

### Calls

- `AuthAgent.validate_token()`
- `AuthAgent.authenticate()`
- `TaskAgent.*`
- `UserAgent.*`
- `AIAgent.*`

### Tools

- `Logger` — Structured logging
- `MetricsCollector` — Request metrics
- `RateLimiter` — Request throttling

---

## 3. AuthAgent

| Property | Value |
|----------|-------|
| **name** | `AuthAgent` |
| **description** | Handles all authentication and authorization operations including login, registration, token management, and permission validation. |

### Responsibilities

- Authenticate users via email/password
- Generate and validate JWT tokens
- Manage user sessions
- Enforce rate limiting on auth endpoints
- Hash and verify passwords

### Inputs

| Input | Type | Description |
|-------|------|-------------|
| `credentials` | LoginCredentials | Email and password for login |
| `registration_data` | RegistrationData | Email, password for signup |
| `token` | JWT | Token for validation |
| `user_id` | UUID | User ID for session operations |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `auth_result` | AuthResult | Success/failure with token or error |
| `user_identity` | UserIdentity | Validated user ID and claims |
| `session` | Session | Active session metadata |

### Assigned Skills

| Skill | Purpose |
|-------|---------|
| `password_hashing` | Secure password hashing (Argon2) |
| `token_generation` | Create signed JWT tokens |
| `token_validation` | Verify and decode JWT tokens |
| `rate_limiting` | Track and enforce login attempt limits |
| `session_management` | Create, refresh, invalidate sessions |

### Calls

- `UserAgent.get_user_by_email()`
- `UserAgent.create_user()`

### Tools

- `PasswordHasher` — Argon2 implementation
- `JWTProvider` — Token signing and verification
- `RateLimitStore` — Track failed attempts
- `SessionStore` — Session state management

---

## 4. TaskAgent

| Property | Value |
|----------|-------|
| **name** | `TaskAgent` |
| **description** | Manages all task-related CRUD operations with user-scoped data isolation and validation. |

### Responsibilities

- Create new tasks for authenticated users
- Retrieve tasks scoped to owner
- Update task properties (title, description, status)
- Delete tasks with ownership verification
- Enforce user isolation at data layer

### Inputs

| Input | Type | Description |
|-------|------|-------------|
| `user_id` | UUID | Authenticated user (from AuthAgent) |
| `task_data` | TaskCreate | Title, description for new task |
| `task_id` | UUID | Task identifier for read/update/delete |
| `update_data` | TaskUpdate | Fields to update |
| `filters` | TaskFilters | Optional filters (status, date range) |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `task` | Task | Single task object |
| `tasks` | Task[] | List of tasks |
| `operation_result` | OperationResult | Success/failure with affected count |

### Assigned Skills

| Skill | Purpose |
|-------|---------|
| `task_creation` | Validate and persist new tasks |
| `task_retrieval` | Query tasks with user scoping |
| `task_update` | Modify task properties |
| `task_deletion` | Remove tasks with ownership check |
| `ownership_validation` | Verify user owns resource |

### Calls

- `AIAgent.get_suggestions()` (optional)

### Tools

- `TaskRepository` — Database access layer
- `Validator` — Input validation
- `EventEmitter` — Publish task events

---

## 5. UserAgent

| Property | Value |
|----------|-------|
| **name** | `UserAgent` |
| **description** | Manages user account operations including profile management and account settings. |

### Responsibilities

- Create new user accounts
- Retrieve user profile data
- Update user preferences
- Handle account deletion requests
- Validate email uniqueness

### Inputs

| Input | Type | Description |
|-------|------|-------------|
| `user_id` | UUID | User identifier |
| `email` | String | Email for lookup or creation |
| `profile_data` | ProfileUpdate | Fields to update |
| `registration_data` | RegistrationData | New user data |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `user` | User | User profile (password excluded) |
| `exists` | Boolean | Email existence check result |
| `operation_result` | OperationResult | Success/failure status |

### Assigned Skills

| Skill | Purpose |
|-------|---------|
| `user_creation` | Create new user records |
| `user_retrieval` | Fetch user by ID or email |
| `email_validation` | Check email format and uniqueness |
| `account_deletion` | Soft/hard delete with cascade |

### Calls

- `TaskAgent.delete_user_tasks()` (for account deletion)

### Tools

- `UserRepository` — Database access layer
- `EmailValidator` — Format and deliverability check

---

## 6. AIAgent

| Property | Value |
|----------|-------|
| **name** | `AIAgent` |
| **description** | Provides AI-powered task intelligence including suggestions, prioritization, and smart categorization. Designed for graceful degradation. |

### Responsibilities

- Generate task suggestions based on context
- Provide priority recommendations
- Suggest task categorization
- Handle AI service failures gracefully
- Sanitize AI outputs before returning

### Inputs

| Input | Type | Description |
|-------|------|-------------|
| `task_context` | TaskContext | Current task title/description |
| `user_tasks` | Task[] | User's existing tasks for context |
| `request_type` | AIRequestType | suggestion \| prioritization \| categorization |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `suggestions` | Suggestion[] | AI-generated suggestions |
| `priorities` | PriorityRecommendation[] | Ordered task priorities |
| `categories` | CategorySuggestion[] | Suggested categories |
| `available` | Boolean | AI service availability status |

### Assigned Skills

| Skill | Purpose |
|-------|---------|
| `suggestion_generation` | Create task suggestions via Claude |
| `priority_analysis` | Analyze and rank task priorities |
| `graceful_degradation` | Return empty results on failure |

### Calls

- None (leaf agent)

### Tools

- `ClaudeClient` — Anthropic API client
- `PromptBuilder` — Construct AI prompts
- `ResponseParser` — Parse and validate AI output
- `CircuitBreaker` — Prevent cascade failures
- `RateLimitManager` — Respect API quotas

---

## 7. Agent Interaction Matrix

| Caller | AuthAgent | TaskAgent | UserAgent | AIAgent |
|--------|-----------|-----------|-----------|---------|
| **Orchestrator** | ✓ validate, authenticate | ✓ all CRUD | ✓ profile ops | ✓ suggestions |
| **AuthAgent** | — | — | ✓ get/create user | — |
| **TaskAgent** | — | — | — | ✓ suggestions |
| **UserAgent** | — | ✓ delete tasks | — | — |
| **AIAgent** | — | — | — | — |

---

## 8. Communication Protocol

### Request Format

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
```

### Response Format

```yaml
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

## 9. Implementation Status

| Agent | Status | Implementation Location |
|-------|--------|------------------------|
| OrchestratorAgent | Planned | `backend/src/agents/orchestrator.py` |
| AuthAgent | Partial | `backend/src/auth/` (password hashing complete) |
| TaskAgent | Planned | `backend/src/agents/task.py` |
| UserAgent | Partial | `backend/src/models/user.py` (model complete) |
| AIAgent | Planned | `backend/src/agents/ai.py` |

---

## 10. Related Documents

- [System Specification](./system.spec.md) — System architecture overview
- [Skills Specification](./skills.spec.md) — Detailed skill contracts
- [Schemas Specification](./schemas.spec.md) — Data models
