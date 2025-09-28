$headers = @{ 'Content-Type'='application/json'; 'X-API-Key'='dev-key-1' }
 $payload = @{
   jsonrpc="2.0"; id="2"; method="tools/call";
   params = @{ name="echo"; arguments = @{ text="Hello MCP!" } }
 } | ConvertTo-Json -Depth 5
$response = Invoke-RestMethod -Method Post -Uri http://localhost:8000/mcp -Headers $headers -Body $payload
$response | ConvertTo-Json -Depth 10