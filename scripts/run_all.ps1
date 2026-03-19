# Start all services for the Gradio chat frontend.
# Run from project root: .\scripts\run_all.ps1
#
# Architecture: Gradio (7860) -> Gateway (8000) -> gRPC backends (50051/50052/50053)
# Each service runs in a separate background job; Gradio runs in foreground.

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")
Set-Location $projectRoot

Write-Host "=== Gradio Chatbot - Starting services ===" -ForegroundColor Cyan
Write-Host "Ports: Service A=50051, B=50052, C=50053, Gateway=8000, Gradio=7860"
Write-Host ""

$jobs = @()

Write-Host "[1/5] Starting Service A (OpenAI) on 50051..."
$jobs += Start-Job -ScriptBlock {
    Set-Location $using:projectRoot
    python -m services.openai_service.server 50051
}

Write-Host "[2/5] Starting Service B (Qwen) on 50052..."
$jobs += Start-Job -ScriptBlock {
    Set-Location $using:projectRoot
    python -m services.qwen_service.server 50052
}

Write-Host "[3/5] Starting Service C (Doubao) on 50053..."
$jobs += Start-Job -ScriptBlock {
    Set-Location $using:projectRoot
    python -m services.doubao_service.server 50053
}

Write-Host "[4/5] Starting Gateway on 8000..."
$jobs += Start-Job -ScriptBlock {
    Set-Location $using:projectRoot
    uvicorn gateway.main:app --host 0.0.0.0 --port 8000
}

Start-Sleep -Seconds 2

Write-Host "[5/5] Starting Gradio frontend on 7860..."
try {
    python -m frontend.app
} finally {
    Write-Host "Stopping background services..."
    $jobs | Stop-Job
    $jobs | Remove-Job
}
