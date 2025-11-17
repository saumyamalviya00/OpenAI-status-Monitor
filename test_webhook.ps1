# PowerShell test script for the Status Monitor webhook endpoint
# This script tests webhook functionality using native PowerShell commands

$BASE_URL = "http://localhost:8000"

Write-Host "PowerShell Status Monitor Test Suite" -ForegroundColor Cyan
Write-Host "=" * 40

# Test 1: Health Check
Write-Host "`nTesting health endpoint..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "$BASE_URL/health" -Method GET
    Write-Host "Health Status: $($healthResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($healthResponse.Content)"
} catch {
    Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Incident Webhook
Write-Host "`nTesting incident webhook..." -ForegroundColor Yellow
$incidentPayload = @{
    incident = @{
        id = "inc_test_001"
        name = "OpenAI API - Chat Completions"
        components = @(
            @{ name = "Chat Completions API" }
        )
        incident_updates = @(
            @{
                id = "upd_test_001"
                created_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
                body = "We are investigating reports of degraded performance for Chat Completions API"
            }
        )
    }
} | ConvertTo-Json -Depth 5

try {
    $webhookResponse = Invoke-WebRequest -Uri "$BASE_URL/webhook" -Method POST -Body $incidentPayload -ContentType "application/json"
    Write-Host "Incident Webhook Status: $($webhookResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Check server console for the printed status update!"
} catch {
    Write-Host "Incident webhook failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Component Webhook  
Write-Host "`nTesting component webhook..." -ForegroundColor Yellow
$componentPayload = @{
    component = @{
        id = "comp_test_001"
        name = "GPT-4 API"
        status = "degraded_performance"
        updated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    }
} | ConvertTo-Json -Depth 3

try {
    $componentResponse = Invoke-WebRequest -Uri "$BASE_URL/webhook" -Method POST -Body $componentPayload -ContentType "application/json"
    Write-Host "Component Webhook Status: $($componentResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Check server console for the printed status update!"
} catch {
    Write-Host "Component webhook failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Fallback Message
Write-Host "`nTesting fallback webhook..." -ForegroundColor Yellow
$fallbackPayload = @{
    message = "Service maintenance scheduled for 2025-11-18 14:00 UTC"
    service = "OpenAI Platform"
} | ConvertTo-Json

try {
    $fallbackResponse = Invoke-WebRequest -Uri "$BASE_URL/webhook" -Method POST -Body $fallbackPayload -ContentType "application/json"
    Write-Host "Fallback Webhook Status: $($fallbackResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Check server console for the printed status update!"
} catch {
    Write-Host "Fallback webhook failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" + "=" * 40
Write-Host "Test Complete! Check the FastAPI server console for status updates." -ForegroundColor Green
Write-Host "Tip: The server should display formatted status messages like:" -ForegroundColor Cyan
Write-Host "[2025-11-18 12:34:56] Product: OpenAI API - Chat Completions" -ForegroundColor Gray
Write-Host "Status: We are investigating reports of degraded performance..." -ForegroundColor Gray