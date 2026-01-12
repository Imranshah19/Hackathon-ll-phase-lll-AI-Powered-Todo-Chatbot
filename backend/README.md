# Todo Skills Backend

Skills Library for Todo Full-Stack Web Application.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Testing

```bash
pytest
```

## Structure

```
src/
├── models/          # Data models and enums
├── services/
│   └── skills/      # Skills library
│       ├── orchestration/
│       ├── auth/
│       ├── task/
│       ├── user/
│       ├── ai/
│       ├── planning/
│       └── execution/
└── api/             # FastAPI endpoints
```
