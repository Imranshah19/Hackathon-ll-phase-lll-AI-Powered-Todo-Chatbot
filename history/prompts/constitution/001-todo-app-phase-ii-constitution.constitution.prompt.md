---
id: 001
title: Todo App Phase II Constitution
stage: constitution
date: 2026-01-12
surface: agent
model: claude-opus-4-5-20250114
feature: none
branch: master
user: system
command: /sp.constitution
labels: ["constitution", "phase-ii", "full-stack", "authentication"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - n/a
---

## Prompt

Todo App Constitution — Phase II Extension: Multi-user, persistent, full-stack web application with authentication. System: Next.js frontend, FastAPI backend, PostgreSQL (Neon Serverless), Better Auth + JWT, SQLModel ORM. Goals: Task CRUD via web UI, multi-user isolation via JWT, PostgreSQL persistence, responsive Next.js App Router UI. Constraints: No manual coding, Spec-Kit + Claude Code generation only, specs precede implementation.

## Response snapshot

Created constitution v1.0.0 for Todo App Phase II Extension with 6 core principles:
1. Spec-First Development - All code generated through Spec-Kit + Claude Code
2. Layered Architecture - Clean separation (Next.js | FastAPI | PostgreSQL | JWT Auth)
3. Test-First Development (NON-NEGOTIABLE) - TDD with Red-Green-Refactor
4. Secure by Design - JWT auth, multi-user isolation, env-based secrets
5. API-First Integration - REST contracts with OpenAPI
6. Minimal Viable Diff - YAGNI, smallest changes only

Additional sections: Technology Stack, Development Workflow, Governance with semantic versioning.

## Outcome

- Impact: Established foundational governance for Phase II development
- Tests: n/a (constitution document)
- Files: .specify/memory/constitution.md created
- Next prompts: /sp.specify for first feature, /sp.plan for architecture
- Reflection: Clear principles enable consistent AI-assisted development

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS - all placeholders filled, principles testable
- Prompt variant (if applicable): standard constitution creation
- Next experiment (smallest change to try): validate principles during first /sp.plan execution
