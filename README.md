# MyGemini MCP Server

## Overview
This server exposes a single MCP endpoint (`POST /mcp`) implementing JSON-RPC 2.0 for:
- `tools/list` — Discover available tools with JSON Schema derived from Pydantic models.
- `tools/call` — Invoke a tool, returning `content` and optional `structuredContent`.
 It enforces client authentication with `X-API-Key`, validates input/output with Pydantic, and is built for async I/O using FastAPI/Uvicorn. A simple tool registry is included with two example tools: `health_check` and `echo`.

 For architecture, milestones, and future phases (routing, resilience, observability), see `GPT5Plan.md` and `MyGemini MCP Server Specification 1.0.md`.

 ## Requirements
 - Python 3.12+
 - Windows PowerShell (examples use PowerShell) or Bash
 - Docker (optional)

 ## Setup (Local)
0) Install prerequisites (Windows via winget)
    ```powershell
    winget install -e --id Python.Python.3.12
    
    # Optional: Install Rust toolchain (needed if you use Python 3.13 or if pip asks to build native wheels)
    winget install -e --id Rustlang.Rustup
    
    # Optional: Install MSVC Build Tools (required for compiling native extensions on Windows, e.g., pydantic-core on Python 3.13)
    winget install -e --id Microsoft.VisualStudio.2022.BuildTools
    # After install, restart your shell or ensure $env:USERPROFILE\.cargo\bin is on PATH
    rustup --version
    ```
1. Create and activate a virtual environment
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
2. Install dependencies
  ```powershell
  pip install -r requirements.txt
  ```

3. Configure environment
- Copy `env.sample` to `.env` and set values
```ini
GEMINI_API_KEY=your-gemini-api-key
ALLOWED_CLIENT_KEYS=dev-key-1
```
Note: `.gitignore` intentionally blocks `.env.*` patterns; `env.sample` is provided for convenience.

4. Run the server
```powershell
uvicorn server.app:app --reload --port 8000 --app-dir src
```

## JSON-RPC Usage Examples
 Endpoint: `POST http://localhost:8000/mcp`

 Headers:
 ```
 Content-Type: application/json
 X-API-Key: dev-key-1
 ```

 - tools/list (PowerShell)
 ```powershell
 $headers = @{ 'Content-Type'='application/json'; 'X-API-Key'='dev-key-1' }
 $payload = @{ jsonrpc="2.0"; id="1"; method="tools/list" } | ConvertTo-Json
 Invoke-RestMethod -Method Post -Uri http://localhost:8000/mcp -Headers $headers -Body $payload
 ```

 - tools/call: echo (PowerShell)
 ```powershell
 $headers = @{ 'Content-Type'='application/json'; 'X-API-Key'='dev-key-1' }
 $payload = @{
   jsonrpc="2.0"; id="2"; method="tools/call";
   params = @{ name="echo"; arguments = @{ text="Hello MCP!" } }
 } | ConvertTo-Json -Depth 5
 Invoke-RestMethod -Method Post -Uri http://localhost:8000/mcp -Headers $headers -Body $payload
 ```

 - tools/call: health_check (curl)
 ```bash
 curl -s -X POST http://localhost:8000/mcp \
   -H 'Content-Type: application/json' \
   -H 'X-API-Key: dev-key-1' \
   -d '{
     "jsonrpc": "2.0",
     "id": "3",
     "method": "tools/call",
     "params": { "name": "health_check", "arguments": {} }
   }'
 ```

 Example success response:
 ```json
 {
   "jsonrpc": "2.0",
   "id": "3",
   "result": {
     "content": "Service healthy. Uptime: 12s",
     "structuredContent": { "status": "ok", "uptime_seconds": 12 }
   }
 }
 ```

 ## Project Structure
 ```
 src/
   server/
     app.py               # FastAPI app (/healthz, /mcp)
     security.py          # X-API-Key dependency
     mcp_handler.py       # tools/list, tools/call handler
     tools/
       registry.py        # Tool registry + JSON Schema from Pydantic
       health.py          # health_check tool
       echo.py            # echo tool
   models/
     jsonrpc.py           # JSON-RPC models
   config/
     settings.py          # Env-backed settings
   clients/
     gemini.py            # Gemini client stub (Phase 4+)
 Dockerfile
requirements.txt
env.sample
GPT5Plan.md
 ```

## Docker
Build image:
```bash
docker build -t mygemini-mcp .
```
Run container:
```bash
docker run --rm -p 8000:8000 \
  -e GEMINI_API_KEY=your-gemini-api-key \
  -e ALLOWED_CLIENT_KEYS=dev-key-1 \
  mygemini-mcp
```

## Next Steps
- Implement Gemini integration and routing (triage → dispatcher → fallbacks).
- Add observability (structured logs, metrics) and rate limiting.
- Expand toolset and add unit/integration tests.

## License
MIT
