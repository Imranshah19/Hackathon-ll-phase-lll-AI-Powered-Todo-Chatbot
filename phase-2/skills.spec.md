# Skills Library Specification — Phase 2

**Project**: Todo Full-Stack Web Application
**Phase**: 2 — System Design & Architecture
**Created**: 2026-01-12
**Status**: Draft

---

## 1. Overview

Skills are atomic, reusable capabilities assigned to agents. Each skill has a defined contract: typed inputs, typed outputs, success criteria, and enumerated failure modes. This enables predictable behavior, comprehensive error handling, and composability.

### 1.1 Skill Schema

```yaml
Skill:
  name: string                    # Unique identifier (snake_case)
  description: string             # What the skill does
  input_schema: object            # Typed inputs
  output_schema: object           # Typed outputs
  success_criteria: string[]      # Measurable success conditions
  failure_modes: FailureMode[]    # Enumerated error cases
```

### 1.2 Skill Categories

| Category | Count | Purpose |
|----------|-------|---------|
| Orchestration | 4 | Request routing, workflow management |
| Authentication | 5 | Identity verification, sessions |
| Task Management | 5 | Task CRUD with isolation |
| User Management | 4 | Account lifecycle |
| AI | 3 | Intelligent suggestions |
| Planning | 3 | Goal decomposition |
| Execution | 3 | Task execution and progress |

**Total**: 27 skills

---

## 2. Orchestration Skills

### 2.1 request_routing

| Property | Value |
|----------|-------|
| **name** | `request_routing` |
| **description** | Parse incoming requests and route to appropriate domain agent based on path, method, and content |

**input_schema**:
```yaml
request:
  method: string        # GET | POST | PUT | DELETE
  path: string          # /api/v1/tasks, /api/v1/auth/login
  headers: object       # Authorization, Content-Type
  body: object | null   # Request payload
```

**output_schema**:
```yaml
routing_result:
  target_agent: string  # AuthAgent | TaskAgent | UserAgent | AIAgent | PlannerAgent
  operation: string     # create | read | update | delete | authenticate | plan
  validated: boolean    # Request passed basic validation
```

**success_criteria**:
- 100% of valid requests routed to correct agent
- Invalid paths return 404 within 50ms
- Routing decision logged with correlation ID

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `INVALID_PATH` | Path does not match any route | Recoverable | Unknown API path |
| `METHOD_NOT_ALLOWED` | HTTP method not supported | Recoverable | Wrong method for path |
| `MALFORMED_REQUEST` | Request structure invalid | Recoverable | Missing required headers |

---

### 2.2 workflow_coordination

| Property | Value |
|----------|-------|
| **name** | `workflow_coordination` |
| **description** | Sequence multi-step operations across agents, maintaining transaction state |

**input_schema**:
```yaml
workflow:
  steps:
    - agent: string
      operation: string
      input: object
  context: object         # Shared state across steps
  rollback_on_failure: boolean
```

**output_schema**:
```yaml
workflow_result:
  completed_steps: integer
  total_steps: integer
  final_state: object
  rolled_back: boolean
```

**success_criteria**:
- All steps execute in defined order
- Partial failures trigger rollback if configured
- State remains consistent after completion or rollback

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `STEP_FAILED` | Workflow step returned error | Recoverable | Individual step error |
| `ROLLBACK_FAILED` | Unable to undo partial changes | Fatal | Rollback operation error |
| `WORKFLOW_TIMEOUT` | Workflow exceeded time limit | Recoverable | Steps took too long |

---

### 2.3 response_aggregation

| Property | Value |
|----------|-------|
| **name** | `response_aggregation` |
| **description** | Combine responses from multiple agents into unified client response |

**input_schema**:
```yaml
responses:
  - agent: string
    status: success | error
    payload: object
    duration_ms: integer
```

**output_schema**:
```yaml
aggregated_response:
  status: success | partial | error
  data: object
  errors: Error[] | null
  total_duration_ms: integer
```

**success_criteria**:
- All successful responses merged correctly
- Partial success clearly indicated in status
- Error details preserved without exposing internals

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `MERGE_CONFLICT` | Incompatible response structures | Recoverable | Schema mismatch |
| `ALL_FAILED` | Every agent returned error | Fatal | Complete failure |

---

### 2.4 error_handling

| Property | Value |
|----------|-------|
| **name** | `error_handling` |
| **description** | Standardize error responses, sanitize internal details, log for debugging |

**input_schema**:
```yaml
error:
  source_agent: string
  error_code: string
  internal_message: string
  stack_trace: string | null
  context: object
```

**output_schema**:
```yaml
client_error:
  code: string          # Standardized error code
  message: string       # User-safe message
  correlation_id: UUID  # For support reference
```

**success_criteria**:
- No internal details exposed to client
- All errors logged with full context internally
- Correlation ID present in every error response

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `LOG_FAILURE` | Unable to persist error log | Recoverable | Logging service unavailable |

---

## 3. Authentication Skills

### 3.1 password_hashing

| Property | Value |
|----------|-------|
| **name** | `password_hashing` |
| **description** | Securely hash passwords using industry-standard algorithms |

**input_schema**:
```yaml
password: string        # Plaintext password (8+ characters)
```

**output_schema**:
```yaml
hash: string            # Hashed password
algorithm: string       # Algorithm used (bcrypt | argon2)
```

**success_criteria**:
- Hash is non-reversible
- Same password produces different hashes (salted)
- Computation time 100-500ms (brute-force resistant)

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `WEAK_PASSWORD` | Password doesn't meet requirements | Recoverable | Too short or simple |
| `HASH_FAILURE` | Cryptographic operation failed | Fatal | System error |

---

### 3.2 token_generation

| Property | Value |
|----------|-------|
| **name** | `token_generation` |
| **description** | Create signed authentication tokens with claims and expiration |

**input_schema**:
```yaml
user_id: UUID
claims:
  email: string
  roles: string[]       # Optional additional claims
expires_in: integer     # Seconds until expiration (default: 86400)
```

**output_schema**:
```yaml
token: string           # Signed JWT
expires_at: ISO8601     # Expiration timestamp
token_type: bearer      # Token type
```

**success_criteria**:
- Token is cryptographically signed
- Expiration correctly encoded
- Claims accurately represented

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `SIGNING_FAILURE` | Unable to sign token | Fatal | Key unavailable |
| `INVALID_CLAIMS` | Claims contain invalid data | Recoverable | Malformed claim values |

---

### 3.3 token_validation

| Property | Value |
|----------|-------|
| **name** | `token_validation` |
| **description** | Verify token signature, check expiration, extract claims |

**input_schema**:
```yaml
token: string           # JWT to validate
```

**output_schema**:
```yaml
valid: boolean
user_id: UUID | null
claims: object | null
error: string | null
remaining_ttl: integer  # Seconds until expiration
```

**success_criteria**:
- Invalid signatures rejected
- Expired tokens rejected
- Valid tokens return correct user ID and claims

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `INVALID_SIGNATURE` | Token signature doesn't match | Fatal | Tampered or wrong key |
| `TOKEN_EXPIRED` | Token past expiration | Recoverable | Needs re-authentication |
| `MALFORMED_TOKEN` | Token structure invalid | Fatal | Not a valid JWT |

---

### 3.4 rate_limiting

| Property | Value |
|----------|-------|
| **name** | `rate_limiting` |
| **description** | Track and enforce request limits per client/IP/user |

**input_schema**:
```yaml
identifier: string      # IP address, user_id, or API key
action: string          # login | register | api_call
limit: integer          # Max requests per window (default varies by action)
window_seconds: integer # Time window (default: 60)
```

**output_schema**:
```yaml
allowed: boolean
remaining: integer      # Requests remaining in window
reset_at: ISO8601       # When limit resets
retry_after: integer    # Seconds to wait (if blocked)
```

**success_criteria**:
- Limits enforced accurately per identifier
- Remaining count decremented atomically
- Reset time calculated correctly

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `RATE_EXCEEDED` | Too many requests | Recoverable | Limit reached |
| `STORE_UNAVAILABLE` | Rate limit store unreachable | Recoverable | Redis/cache down |

---

### 3.5 session_management

| Property | Value |
|----------|-------|
| **name** | `session_management` |
| **description** | Create, refresh, and invalidate user sessions |

**input_schema**:
```yaml
action: create | refresh | invalidate | get
user_id: UUID
session_id: UUID | null # Required for refresh/invalidate/get
```

**output_schema**:
```yaml
session:
  id: UUID
  user_id: UUID
  created_at: ISO8601
  expires_at: ISO8601
  last_activity: ISO8601
  active: boolean
```

**success_criteria**:
- Sessions created with correct expiration
- Refresh extends expiration without creating new session
- Invalidate immediately terminates session

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `SESSION_NOT_FOUND` | Session doesn't exist | Recoverable | Invalid session ID |
| `SESSION_EXPIRED` | Cannot refresh expired session | Recoverable | Session timed out |

---

## 4. Task Management Skills

### 4.1 task_creation

| Property | Value |
|----------|-------|
| **name** | `task_creation` |
| **description** | Validate and persist new tasks for authenticated users |

**input_schema**:
```yaml
user_id: UUID           # Task owner (from auth)
title: string           # 1-255 characters, required
description: string     # Optional, max 4000 characters
metadata: object        # Optional extensible fields
```

**output_schema**:
```yaml
task:
  id: UUID
  user_id: UUID
  title: string
  description: string | null
  is_completed: boolean # Always false for new tasks
  created_at: ISO8601
  updated_at: ISO8601
  metadata: object
```

**success_criteria**:
- Task persisted with correct owner
- All fields validated against constraints
- Created/updated timestamps accurate

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `VALIDATION_ERROR` | Title empty or too long | Recoverable | Invalid input |
| `PERSISTENCE_ERROR` | Database write failed | Recoverable | DB unavailable |

---

### 4.2 task_retrieval

| Property | Value |
|----------|-------|
| **name** | `task_retrieval` |
| **description** | Query tasks with automatic user scoping and filtering |

**input_schema**:
```yaml
user_id: UUID           # Authenticated user
task_id: UUID | null    # null = list all user's tasks
filters:
  is_completed: boolean | null
  created_after: ISO8601 | null
  created_before: ISO8601 | null
  search: string | null # Title/description search
pagination:
  limit: integer        # Default: 50, max: 100
  offset: integer       # Default: 0
```

**output_schema**:
```yaml
tasks: Task[]
total_count: integer    # Total matching (before pagination)
has_more: boolean
```

**success_criteria**:
- Only user's own tasks returned (never cross-user)
- Filters applied correctly
- Empty list for no matches (not error)

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `NOT_FOUND` | Specific task_id doesn't exist | Recoverable | Invalid ID |
| `UNAUTHORIZED` | Task belongs to different user | Fatal | Access denied |

---

### 4.3 task_update

| Property | Value |
|----------|-------|
| **name** | `task_update` |
| **description** | Modify task properties with ownership verification |

**input_schema**:
```yaml
user_id: UUID           # Authenticated user
task_id: UUID           # Task to update
updates:
  title: string | null
  description: string | null
  is_completed: boolean | null
  metadata: object | null
```

**output_schema**:
```yaml
task: Task              # Updated task
changed_fields: string[] # List of modified fields
previous_values: object # Old values for changed fields
```

**success_criteria**:
- Ownership verified before any modification
- Only provided fields modified (partial update)
- updated_at timestamp set to current time

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `NOT_FOUND` | Task doesn't exist | Recoverable | Invalid ID |
| `UNAUTHORIZED` | User doesn't own task | Fatal | Access denied |
| `VALIDATION_ERROR` | Invalid field values | Recoverable | Bad input |

---

### 4.4 task_deletion

| Property | Value |
|----------|-------|
| **name** | `task_deletion` |
| **description** | Remove task permanently with ownership verification |

**input_schema**:
```yaml
user_id: UUID           # Authenticated user
task_id: UUID           # Task to delete
```

**output_schema**:
```yaml
deleted: boolean
task_id: UUID
deleted_at: ISO8601
```

**success_criteria**:
- Ownership verified before deletion
- Task completely removed from database
- Deletion is permanent and irreversible

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `NOT_FOUND` | Task doesn't exist | Recoverable | Invalid ID |
| `UNAUTHORIZED` | User doesn't own task | Fatal | Access denied |

---

### 4.5 ownership_validation

| Property | Value |
|----------|-------|
| **name** | `ownership_validation` |
| **description** | Verify user owns the requested resource |

**input_schema**:
```yaml
user_id: UUID           # Requesting user
resource_type: task | profile
resource_id: UUID       # Resource to check
```

**output_schema**:
```yaml
authorized: boolean
owner_id: UUID | null   # Actual owner (if found)
resource_exists: boolean
```

**success_criteria**:
- Accurate ownership determination
- No false positives (security critical)
- Fast lookup (< 10ms)

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `RESOURCE_NOT_FOUND` | Resource doesn't exist | Recoverable | Invalid ID |

---

## 5. User Management Skills

### 5.1 user_creation

| Property | Value |
|----------|-------|
| **name** | `user_creation` |
| **description** | Create new user accounts with validated data |

**input_schema**:
```yaml
email: string           # Valid email format
password_hash: string   # Already hashed password
```

**output_schema**:
```yaml
user:
  id: UUID
  email: string         # Normalized (lowercase)
  created_at: ISO8601
  # password_hash NEVER in output
```

**success_criteria**:
- User persisted with unique UUID
- Email stored normalized (lowercase, trimmed)
- Password hash never in any response

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `DUPLICATE_EMAIL` | Email already registered | Recoverable | Existing account |
| `PERSISTENCE_ERROR` | Database write failed | Recoverable | DB unavailable |

---

### 5.2 user_retrieval

| Property | Value |
|----------|-------|
| **name** | `user_retrieval` |
| **description** | Fetch user profile by ID or email (password never exposed) |

**input_schema**:
```yaml
user_id: UUID | null    # Lookup by ID
email: string | null    # Lookup by email (one required)
include_password_hash: boolean # For internal auth use only (default: false)
```

**output_schema**:
```yaml
user:
  id: UUID
  email: string
  created_at: ISO8601
  updated_at: ISO8601
  password_hash: string | null # Only if explicitly requested internally
found: boolean
```

**success_criteria**:
- Password hash excluded by default
- Lookup works by either ID or email
- Not found returns null user with found=false

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `INVALID_QUERY` | Neither ID nor email provided | Recoverable | Bad request |

---

### 5.3 email_validation

| Property | Value |
|----------|-------|
| **name** | `email_validation` |
| **description** | Validate email format and optionally check uniqueness |

**input_schema**:
```yaml
email: string
check_uniqueness: boolean # Query database for existing
```

**output_schema**:
```yaml
valid: boolean          # Format is valid
normalized: string      # Lowercased, trimmed
unique: boolean | null  # null if not checked
error: string | null    # Specific validation error
```

**success_criteria**:
- RFC 5322 compliant format validation
- Uniqueness check against database
- Consistent normalization applied

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `INVALID_FORMAT` | Email doesn't match pattern | Recoverable | Bad format |
| `ALREADY_EXISTS` | Email already registered | Recoverable | Duplicate |

---

### 5.4 account_deletion

| Property | Value |
|----------|-------|
| **name** | `account_deletion` |
| **description** | Delete user account with cascade to owned resources |

**input_schema**:
```yaml
user_id: UUID
cascade: boolean        # Delete all owned tasks (default: true)
```

**output_schema**:
```yaml
deleted: boolean
user_id: UUID
tasks_deleted: integer  # Count of cascaded task deletions
deleted_at: ISO8601
```

**success_criteria**:
- User record completely removed
- All owned tasks deleted if cascade=true
- Deletion is atomic (all or nothing)

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `USER_NOT_FOUND` | User doesn't exist | Recoverable | Invalid ID |
| `CASCADE_FAILED` | Unable to delete tasks | Fatal | Partial failure |

---

## 6. AI Skills

### 6.1 suggestion_generation

| Property | Value |
|----------|-------|
| **name** | `suggestion_generation` |
| **description** | Generate task suggestions using AI based on context |

**input_schema**:
```yaml
task_context:
  title: string
  description: string | null
existing_tasks: Task[]  # User's current tasks for context
max_suggestions: integer # Default: 3
```

**output_schema**:
```yaml
suggestions:
  - text: string
    confidence: float   # 0.0 - 1.0
    type: subtask | improvement | related
available: boolean      # AI service was reachable
```

**success_criteria**:
- Suggestions relevant to provided context
- Confidence scores calibrated (higher = more relevant)
- Response within 5 seconds

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `AI_UNAVAILABLE` | AI service unreachable | Recoverable | Network/service down |
| `RATE_LIMITED` | API quota exceeded | Recoverable | Too many requests |
| `TIMEOUT` | Response took too long | Recoverable | Slow AI response |

---

### 6.2 priority_analysis

| Property | Value |
|----------|-------|
| **name** | `priority_analysis` |
| **description** | Analyze and rank tasks by priority using AI |

**input_schema**:
```yaml
tasks: Task[]           # Tasks to prioritize
criteria: string | null # User's prioritization preferences
```

**output_schema**:
```yaml
priorities:
  - task_id: UUID
    rank: integer       # 1 = highest priority
    reasoning: string   # Why this ranking
available: boolean
```

**success_criteria**:
- All provided tasks ranked
- Reasoning provided for each ranking
- Consistent ordering (deterministic for same input)

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `AI_UNAVAILABLE` | AI service unreachable | Recoverable | Service down |
| `INSUFFICIENT_DATA` | Not enough tasks | Recoverable | Need 2+ tasks |

---

### 6.3 graceful_degradation

| Property | Value |
|----------|-------|
| **name** | `graceful_degradation` |
| **description** | Handle AI service failures without breaking core functionality |

**input_schema**:
```yaml
operation: string       # What was attempted
error: object           # Error details from AI call
```

**output_schema**:
```yaml
fallback_applied: boolean # Always true
user_message: string    # Friendly explanation
core_affected: boolean  # Always false by design
```

**success_criteria**:
- Core features completely unaffected
- User informed of reduced AI functionality
- No error propagation to calling agent

**failure_modes**:
- None (this skill cannot fail by design)

---

## 7. Planning Skills

### 7.1 goal_decomposition

| Property | Value |
|----------|-------|
| **name** | `goal_decomposition` |
| **description** | Break down high-level user goals into discrete executable tasks |

**input_schema**:
```yaml
user_goal:
  description: string   # Natural language goal
  constraints: string[] # Any limitations or requirements
context:
  existing_tasks: Task[]
  user_preferences: object
```

**output_schema**:
```yaml
tasks:
  - id: string          # Temporary planning ID
    description: string
    depends_on: string[] # IDs of prerequisite tasks
    estimated_complexity: low | medium | high
total_tasks: integer
```

**success_criteria**:
- Goal fully covered by generated tasks
- Dependencies correctly identified
- No circular dependencies

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `AMBIGUOUS_GOAL` | Cannot interpret user intent | Recoverable | Unclear input |
| `GOAL_TOO_COMPLEX` | Exceeds decomposition limits | Recoverable | Too many tasks |

---

### 7.2 task_sequencing

| Property | Value |
|----------|-------|
| **name** | `task_sequencing` |
| **description** | Order tasks respecting dependencies with optimization options |

**input_schema**:
```yaml
tasks: PlannedTask[]
optimization: fastest | safest | parallel
```

**output_schema**:
```yaml
sequence:
  - task_id: string
    order: integer
    can_parallelize: boolean
    blocking: string[]  # Tasks that must wait for this one
execution_path: string  # Visual representation
```

**success_criteria**:
- All dependencies respected in ordering
- Parallelization opportunities identified
- Valid topological sort produced

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `CIRCULAR_DEPENDENCY` | Tasks have circular references | Fatal | Invalid plan |
| `MISSING_DEPENDENCY` | Referenced task not in list | Recoverable | Incomplete input |

---

### 7.3 feasibility_check

| Property | Value |
|----------|-------|
| **name** | `feasibility_check` |
| **description** | Validate whether a plan can be executed given current state |

**input_schema**:
```yaml
plan: TaskPlan
current_state: object   # System state
constraints: object     # Resource/time limits
```

**output_schema**:
```yaml
feasible: boolean
blockers: string[]      # What prevents execution
warnings: string[]      # Potential issues (non-blocking)
estimated_duration: string # Human-readable estimate
```

**success_criteria**:
- All blockers accurately identified
- No false positives on feasibility
- Warnings capture edge cases

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `STATE_UNKNOWN` | Cannot determine current state | Recoverable | Missing context |

---

## 8. Execution Skills

### 8.1 task_execution

| Property | Value |
|----------|-------|
| **name** | `task_execution` |
| **description** | Execute a single planned task by coordinating with domain agents |

**input_schema**:
```yaml
task: PlannedTask       # Task to execute
context: ExecutionContext # User, state, constraints
```

**output_schema**:
```yaml
result:
  success: boolean
  output: object        # Task-specific output
  duration_ms: integer
  side_effects: string[] # State changes made
```

**success_criteria**:
- Task completed as specified
- All side effects tracked
- Duration accurately recorded

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `EXECUTION_ERROR` | Task logic failed | Recoverable | Task-specific error |
| `AGENT_UNAVAILABLE` | Required agent not responding | Recoverable | Agent down |
| `TIMEOUT` | Execution exceeded time limit | Recoverable | Slow operation |

---

### 8.2 progress_reporting

| Property | Value |
|----------|-------|
| **name** | `progress_reporting` |
| **description** | Report execution progress for multi-step operations |

**input_schema**:
```yaml
plan_id: UUID
current_step: integer
total_steps: integer
status: running | completed | failed
message: string | null
```

**output_schema**:
```yaml
reported: boolean
percentage: float       # 0.0 - 100.0
eta_seconds: integer | null
```

**success_criteria**:
- Progress updates delivered reliably
- Percentage accurately calculated
- ETA reasonably estimated based on elapsed time

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `REPORTING_FAILED` | Unable to send update | Recoverable | Channel unavailable |

---

### 8.3 retry_logic

| Property | Value |
|----------|-------|
| **name** | `retry_logic` |
| **description** | Determine if and how to retry failed operations |

**input_schema**:
```yaml
error: object           # Error from failed operation
attempt: integer        # Current attempt number
max_attempts: integer   # Maximum retries (default: 3)
```

**output_schema**:
```yaml
should_retry: boolean
delay_ms: integer       # Wait before retry
strategy: immediate | exponential | fixed
reason: string          # Why retry/not retry
```

**success_criteria**:
- Transient errors retried appropriately
- Permanent errors not retried (waste prevention)
- Exponential backoff prevents thundering herd

**failure_modes**:

| Code | Message | Severity | Cause |
|------|---------|----------|-------|
| `MAX_RETRIES_EXCEEDED` | All attempts exhausted | Fatal | Persistent failure |

---

## 9. Failure Mode Taxonomy

### 9.1 Standard Failure Codes

| Code | Category | Description | Severity | Retry |
|------|----------|-------------|----------|-------|
| `VALIDATION_ERROR` | Input | Input failed schema validation | Recoverable | No |
| `NOT_FOUND` | Data | Resource doesn't exist | Recoverable | No |
| `UNAUTHORIZED` | Security | Permission denied | Fatal | No |
| `RATE_EXCEEDED` | Limit | Too many requests | Recoverable | Yes |
| `TIMEOUT` | Execution | Operation took too long | Recoverable | Yes |
| `PERSISTENCE_ERROR` | Data | Database operation failed | Recoverable | Yes |
| `EXTERNAL_SERVICE_ERROR` | Integration | External API failed | Recoverable | Yes |
| `INTERNAL_ERROR` | System | Unexpected system failure | Fatal | No |

### 9.2 Failure Response Schema

```yaml
failure:
  code: string              # From failure mode enum
  message: string           # Human-readable explanation
  details:                  # Context-specific data
    field: string           # Which field failed (for validation)
    expected: string        # What was expected
    actual: string          # What was received
  correlation_id: UUID      # For troubleshooting
  timestamp: ISO8601
  recoverable: boolean      # Can operation be retried?
  retry_after: integer      # Seconds to wait (if applicable)
```

---

## 10. Skill-Agent Assignment Matrix

| Skill | Orchestrator | Auth | Task | User | AI | Planner | Executor |
|-------|--------------|------|------|------|-----|---------|----------|
| request_routing | ✓ | | | | | | |
| workflow_coordination | ✓ | | | | | | |
| response_aggregation | ✓ | | | | | | |
| error_handling | ✓ | | | | | | |
| password_hashing | | ✓ | | | | | |
| token_generation | | ✓ | | | | | |
| token_validation | | ✓ | | | | | |
| rate_limiting | | ✓ | | | | | |
| session_management | | ✓ | | | | | |
| task_creation | | | ✓ | | | | |
| task_retrieval | | | ✓ | | | | |
| task_update | | | ✓ | | | | |
| task_deletion | | | ✓ | | | | |
| ownership_validation | | | ✓ | | | | |
| user_creation | | | | ✓ | | | |
| user_retrieval | | | | ✓ | | | |
| email_validation | | | | ✓ | | | |
| account_deletion | | | | ✓ | | | |
| suggestion_generation | | | | | ✓ | | |
| priority_analysis | | | | | ✓ | | |
| graceful_degradation | | | | | ✓ | | |
| goal_decomposition | | | | | | ✓ | |
| task_sequencing | | | | | | ✓ | |
| feasibility_check | | | | | | ✓ | |
| task_execution | | | | | | | ✓ |
| progress_reporting | | | | | | | ✓ |
| retry_logic | | | | | | | ✓ |

---

## 11. Glossary

| Term | Definition |
|------|------------|
| Skill | Atomic, reusable capability with defined contract |
| Input Schema | Typed structure of required/optional inputs |
| Output Schema | Typed structure of success response |
| Failure Mode | Enumerated error case with code and metadata |
| Success Criteria | Measurable conditions for skill success |
| Recoverable | Error that can be retried or handled gracefully |
| Fatal | Error that cannot be recovered from |
