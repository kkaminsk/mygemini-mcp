# Project Context

## Purpose
Build a high-performance Python MCP server that acts as an LLM Gateway/Router for the Windsurf Cascade client. The server exposes a single JSON-RPC MCP endpoint (`POST /mcp`) to:
- Provide tool discovery via `tools/list` with JSON Schema from Pydantic models.
- Execute tools via `tools/call`, returning `content` and optional `structuredContent`.

Primary goals:
- Simplify integration with multiple Gemini models via a routing layer (triage → dispatcher → fallbacks).
- Enforce security via API-key authentication (`X-API-Key`) and env-based secret management.
- Optimize for cost/latency using Gemini 2.5 model family, with Flash-Lite for triage.

## Tech Stack
- Language: Python 3.12+
- Framework: FastAPI (ASGI) + Uvicorn
- Data modelling/validation: Pydantic
- Protocol: JSON-RPC 2.0 over HTTP at `/mcp`
- Containerization: Docker (optional)
- OS/dev: Windows PowerShell examples included; works cross-platform
- Future integration: Google Gemini SDK/API client (Phase 4+)

## Project Conventions

### Code Style
- Async-first I/O using FastAPI/ASGI.
- Pydantic models as single source of truth for schemas (MCP tool inputs/outputs, internal DTOs).
- Environment variables for secrets (`GEMINI_API_KEY`, `ALLOWED_CLIENT_KEYS`). `.env` is gitignored; `env.sample` provided.
- JSON-RPC 2.0 compliance: `id` must be non-null; methods `tools/list`, `tools/call`.
- Minimal, focused tools with a registry pattern under `src/server/tools/`.

### Architecture Patterns
- Layered design:
  - Transport: FastAPI `/mcp` endpoint.
  - Security: `X-API-Key` via dependency injection.
  - MCP Handler: JSON-RPC parsing, `tools/list` and `tools/call`.
  - Orchestration (planned):
    - Triage Engine using Gemini 2.5 Flash-Lite to classify intent into a structured Pydantic `RouteDecision`.
    - Dynamic Dispatcher routes to Pro/Flash/Flash-Lite per policy.
    - Resilience: timeouts, retries, fallbacks, circuit breaker.
- Schema-driven development with Pydantic to generate JSON Schema for both MCP and Gemini function calling.

### Testing Strategy
- Current: Examples included in `README.md` (curl/PowerShell) for manual JSON-RPC testing.
- Planned: Unit and integration tests for `mcp_handler`, tools, and security dependency.
- TODO: Confirm test framework preference (e.g., pytest) and coverage thresholds.

### Git Workflow
- TODO: Confirm branching model (e.g., trunk-based vs. GitFlow) and commit conventions.
- Recommendation: Enforce PR reviews for security-sensitive changes (auth, routing) and schema changes.

## Domain Context
- MCP server integrates with Windsurf/Cascade via HTTP `/mcp` using JSON-RPC 2.0.
- Tooling requires JSON Schema; Pydantic models generate schemas for `tools/list` and are used to validate inputs/outputs.
- LLM Gateway routes among Gemini models:
  - `gemini-2.5-pro`: complex reasoning/code analysis.
  - `gemini-2.5-flash`: balanced performance, function calling.
  - `gemini-2.5-flash-lite`: triage, high-throughput classification.
  - `gemini-2.0-flash`: fallback layer.
- Two-step function calling workflow (planned): model decides function call → server executes tool → result injected back for final synthesis.

## Important Constraints
- Strict API key auth on all protected endpoints using `X-API-Key`.
- Secrets must be loaded from environment; never commit keys. `.env` is ignored by git.
- JSON-RPC `id` must be non-null; adhere to 2.0 spec.
- Performance target: ASGI/async to support high throughput; FastAPI/Uvicorn mandated by spec.
- Resilience requirements (planned): timeouts, retries, fallbacks, circuit breaker for upstream LLMs.

## External Dependencies
- Google Gemini API (requires `GEMINI_API_KEY`).
- Windsurf/Cascade client (MCP consumer) hitting `/mcp`.
- Docker runtime (optional) for deployment consistency.
- Future: Observability stack and rate limiting (to be selected).
