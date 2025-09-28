@echo off
setlocal
set URL=http://localhost:8000/mcp
set API_KEY=dev-key-1

curl -s -X POST "%URL%" ^
  -H "Content-Type: application/json" ^
  -H "X-API-Key: %API_KEY%" ^
  --data "{\"jsonrpc\":\"2.0\",\"id\":\"3\",\"method\":\"tools/call\",\"params\":{\"name\":\"health_check\",\"arguments\":{}}}"