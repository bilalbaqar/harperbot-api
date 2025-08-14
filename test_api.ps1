# HarperBot API Test Script for PowerShell

Write-Host "Testing HarperBot API..." -ForegroundColor Green

# Test 1: Health endpoint
Write-Host "`n1. Testing health endpoint..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "✅ Health check passed: $($healthResponse | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Chat endpoint
Write-Host "`n2. Testing chat endpoint..." -ForegroundColor Yellow
try {
    $chatBody = @{
        messages = @(
            @{
                role = "user"
                content = "Hello! How are you today?"
            }
        )
    } | ConvertTo-Json

    $chatResponse = Invoke-RestMethod -Uri "http://localhost:8000/chat-gpt-5" -Method POST -Body $chatBody -ContentType "application/json"
    Write-Host "✅ Chat response: $($chatResponse.response)" -ForegroundColor Green
} catch {
    Write-Host "❌ Chat request failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: ReAct agent endpoint
Write-Host "`n3. Testing ReAct agent endpoint..." -ForegroundColor Yellow
try {
    $reactBody = @{
        query = "What is 15 * 23?"
        model = "gpt-4"
        max_iterations = 3
    } | ConvertTo-Json
    Write-Host "Chat request body:`n$reactBody" -ForegroundColor Gray
    
    $reactResponse = Invoke-RestMethod -Uri "http://localhost:8000/react" -Method POST -Body $reactBody -ContentType "application/json"
    Write-Host "✅ ReAct agent answer: $($reactResponse.answer)" -ForegroundColor Green
    Write-Host "   Tools used: $($reactResponse.tools_used -join ', ')" -ForegroundColor Cyan
} catch {
    Write-Host "❌ ReAct agent request failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nTest completed!" -ForegroundColor Green
