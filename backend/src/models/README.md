# Models Package

Data models for the Todo application using SQLModel (Pydantic + SQLAlchemy).

## Entity Overview

```
User (1) ──────── (N) Task
  │                    │
  └─ cascade delete ───┘
```

## Modules

- `base.py` - Common utilities (utc_now, imports)
- `user.py` - User entity and schemas
- `task.py` - Task entity and schemas

## Schema Evolution Patterns

This section documents patterns for forward-compatible schema changes.

### 1. Optional Fields with Defaults

All optional fields have explicit defaults to ensure backward compatibility:

```python
# Good: Optional with default
description: str | None = Field(default=None, max_length=4000)
is_completed: bool = Field(default=False)

# Bad: Required field added later breaks existing clients
priority: int  # Would break existing data
```

**Pattern**: New fields should always be optional with sensible defaults.

### 2. Partial Update Schemas

Use dedicated update schemas with all fields optional:

```python
class TaskUpdate(SQLModel):
    """All fields optional for PATCH semantics."""
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    is_completed: bool | None = Field(default=None)
```

**Usage with exclude_unset**:
```python
# Only update fields that were explicitly provided
update_data = task_update.model_dump(exclude_unset=True)
for key, value in update_data.items():
    setattr(task, key, value)
```

### 3. Input vs Output Schemas

Separate schemas for API input and output:

| Schema | Purpose | Example |
|--------|---------|---------|
| `TaskCreate` | API input for creation | title, description, is_completed |
| `TaskUpdate` | API input for updates | All optional for PATCH |
| `TaskPublic` | API output | Includes id, timestamps |
| `Task` | Database model | Full entity with relationships |

### 4. Auto-Generated Fields

Fields that should be auto-generated, not provided by clients:

```python
# Auto-generated on create
id: UUID = Field(default_factory=uuid4, primary_key=True)
created_at: datetime = Field(default_factory=utc_now)

# Auto-updated on modify
updated_at: datetime = Field(default_factory=utc_now)

# Injected from auth context
user_id: UUID  # Not in TaskCreate, added by service layer
```

### 5. Relationship Configuration

One-to-many with cascade delete:

```python
# In User model
tasks: list["Task"] = Relationship(
    back_populates="user",
    sa_relationship_kwargs={"cascade": "all, delete-orphan"},
)

# In Task model
user: "User" = Relationship(back_populates="tasks")
```

### 6. Validation Constraints

Field constraints are enforced at the Pydantic level:

| Field | Constraints |
|-------|-------------|
| email | EmailStr (RFC 5322) |
| password | min_length=8 |
| title | min_length=1, max_length=255 |
| description | max_length=4000, nullable |

### 7. Adding New Fields (Evolution Guide)

When adding a new field:

1. **Make it optional** with a default value
2. **Add to all relevant schemas** (Create, Update, Public)
3. **Write tests first** verifying backward compatibility
4. **Update OpenAPI spec** in contracts/openapi.yaml

Example adding a `priority` field:

```python
# In TaskBase (shared validation)
priority: int = Field(default=0, ge=0, le=3, description="0=low, 3=urgent")

# Existing data works - defaults to 0
# New clients can set priority
# Old clients ignore it
```

### 8. Removing Fields (Deprecation)

When removing a field:

1. **Mark as deprecated** in docs/OpenAPI first
2. **Make optional** if currently required
3. **Stop using** in business logic
4. **Remove from schemas** after deprecation period
5. **Database migration** to drop column

### 9. Type Conversions

Avoid changing field types. If needed:

1. Add new field with new type
2. Migrate data in background
3. Deprecate old field
4. Remove old field

## Testing Schema Evolution

Tests in `tests/unit/test_schema_evolution.py` verify:

- Optional field handling
- Default value application
- Partial update semantics
- Extra field handling (ignored)
- JSON serialization stability

## Traceability

| Requirement | Implementation |
|-------------|----------------|
| FR-014 | description: str \| None with default=None |
| FR-015 | datetime with timezone.utc via utc_now() |
