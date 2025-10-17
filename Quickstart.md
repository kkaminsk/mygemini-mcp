# Quickstart Guide

Get the MyGemini MCP Server running in under 5 minutes.

## Prerequisites
- Python 3.12+ installed
- Git (to clone the repo)
- A Gemini API key (get one at [Google AI Studio](https://aistudio.google.com/app/apikey))

## Quick Setup

### 1. Clone and navigate to the project
```bash
git clone <your-repo-url>
cd mygemini-mcp
```

### 2. Create virtual environment and install dependencies
**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux/macOS (Bash):**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
# Copy the sample env file
cp env.sample .env

# Edit .env and set your keys:
# GEMINI_API_KEY=your-actual-gemini-api-key-here
# ALLOWED_CLIENT_KEYS=dev-key-1
```

### 4. Start the server
```bash
uvicorn server.app:app --reload --port 8000 --app-dir src
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

## Verify It Works

### Test 1: Health Check
**cURL:**
```bash
curl http://localhost:8000/healthz
```

**PowerShell:**
```powershell
Invoke-RestMethod -Method Get -Uri http://localhost:8000/healthz
```

**Expected response:**
```json
{"status": "ok"}
```

### Test 2: MCP tools/list
**cURL:**
```bash
curl -X POST http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: dev-key-1' \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/list"
  }'
```

**PowerShell:**
```powershell
$headers = @{ 'Content-Type'='application/json'; 'X-API-Key'='dev-key-1' }
$payload = @{ jsonrpc="2.0"; id="1"; method="tools/list" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:8000/mcp -Headers $headers -Body $payload
```

**Expected response:**
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "tools": [
      {
        "name": "health_check",
        "description": "Check server health and uptime",
        "inputSchema": { ... }
      },
      {
        "name": "echo",
        "description": "Echo back the provided text",
        "inputSchema": { ... }
      }
    ]
  }
}
```

### Test 3: MCP tools/call (echo)
**cURL:**
```bash
curl -X POST http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: dev-key-1' \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/call",
    "params": {
      "name": "echo",
      "arguments": {"text": "Hello MCP!"}
    }
  }'
```

**PowerShell:**
```powershell
$headers = @{ 'Content-Type'='application/json'; 'X-API-Key'='dev-key-1' }
$payload = @{
  jsonrpc="2.0"; id="2"; method="tools/call";
  params = @{ name="echo"; arguments = @{ text="Hello MCP!" } }
} | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri http://localhost:8000/mcp -Headers $headers -Body $payload
```

**Expected response:**
```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "result": {
    "content": "Echo: Hello MCP!",
    "structuredContent": {
      "echo": "Hello MCP!",
      "length": 10
    }
  }
}
```

### Test 4: Check Request ID (Observability)
Notice the `X-Request-ID` header in responses. You can provide your own or let the server generate one:

```bash
curl -v -X POST http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: dev-key-1' \
  -H 'X-Request-ID: my-custom-id-123' \
  -d '{"jsonrpc":"2.0","id":"3","method":"tools/list"}' 2>&1 | grep -i x-request-id
```

Response will include:
```
< X-Request-ID: my-custom-id-123
```

## Run Tests

Verify everything is working correctly:
```bash
# Quick test
pytest -q

# With coverage
pytest --cov=src --cov-report=term-missing
```

## Docker Quickstart (Alternative)

If you prefer Docker:

### 1. Build the image
```bash
docker build -t mygemini-mcp .
```

### 2. Run the container
```bash
docker run --rm -p 8000:8000 \
  -e GEMINI_API_KEY=your-gemini-api-key \
  -e ALLOWED_CLIENT_KEYS=dev-key-1 \
  mygemini-mcp
```

### 3. Test (same as above)
```bash
curl http://localhost:8000/healthz
```

## Troubleshooting

### "Missing API key" error
- Ensure you're sending the `X-API-Key: dev-key-1` header with MCP requests
- Check that `ALLOWED_CLIENT_KEYS=dev-key-1` is set in your `.env` file

### "Invalid API key" error
- Verify the key in your request matches a key in `ALLOWED_CLIENT_KEYS`
- Keys are comma-separated if you have multiple: `ALLOWED_CLIENT_KEYS=dev-key-1,prod-key-2`

### Import errors
- Ensure virtual environment is activated: `.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (Linux/macOS)
- Reinstall dependencies: `pip install -r requirements.txt`

### Port already in use
- Change port: `uvicorn server.app:app --reload --port 8001 --app-dir src`
- Or stop the process using port 8000

## Next Steps

✅ **Server is running!** Now you can:

1. **Integrate with Windsurf/Cascade**
   - Configure the MCP client to point to `http://localhost:8000/mcp`
   - See `client/mcp_config.json` for an example configuration

2. **Add custom tools**
   - Create a new tool in `src/server/tools/`
   - Register it in the tool registry
   - See `src/server/tools/echo.py` as a template

3. **Explore the architecture**
   - Read `MyGemini MCP Server Specification 1.0.md` for design details
   - Check `openspec/specs/routing.md` for the planned triage/routing system
   - Review `CONTRIBUTING.md` to contribute

4. **Enable pre-commit hooks** (recommended for development)
   ```bash
   pre-commit install
   pre-commit run --all-files
   ```

5. **Deploy to production**
   - Use the Dockerfile for containerized deployment
   - Set production API keys via environment variables or secrets manager
   - Configure HTTPS and rate limiting

## Additional Resources

- **Full Documentation**: See `README.md`
- **Architecture**: `MyGemini MCP Server Specification 1.0.md`
- **Project Context**: `openspec/project.md`
- **Contributing**: `CONTRIBUTING.md`
- **Testing Examples**: `TestScripts/` directory

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review existing tests in `tests/` for usage patterns
3. Consult the specification docs for architectural details
