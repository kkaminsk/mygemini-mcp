$headers = @{ 'Content-Type'='application/json'; 'X-API-Key'='dev-key-1' }
$payload = @{ jsonrpc="2.0"; id="1"; method="tools/list" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:8000/mcp -Headers $headers -Body $payload