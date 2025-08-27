# Check if SIGMArec is currently running and close it
$sigmarecProcess = Get-Process -Name "SIGMArec" -ErrorAction SilentlyContinue
if ($sigmarecProcess) {
    Write-Host "SIGMArec is currently running. Closing it..." -ForegroundColor Yellow
    Stop-Process -Name "SIGMArec" -Force
    Start-Sleep -Seconds 2
}

# Check if we're in a built release directory
if (Test-Path "src/__main__.py") {
    # We're in the source directory
    Write-Host "Installing dependencies..." -ForegroundColor Green
    py -m pip install -r requirements.txt
    Write-Host "Running SIGMArec from source..." -ForegroundColor Green
    py -m src
} else {
    Write-Host "Error: Could not find src/__main__.py" -ForegroundColor Red
    Write-Host "Make sure you're running this script from the project root directory (containing src/)" -ForegroundColor Red
    exit 1
}
