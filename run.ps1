# Check if SIGMArec is currently running and close it
$sigmarecProcess = Get-Process -Name "SIGMArec" -ErrorAction SilentlyContinue
if ($sigmarecProcess) {
    Write-Host "SIGMArec is currently running." -ForegroundColor Yellow
    $response = Read-Host "Do you want to close it? (Y/n)"
    if ($response -eq 'n' -or $response -eq 'N') {
        Write-Host "Skipping process termination." -ForegroundColor Yellow
    } else {
        Write-Host "Stopping SIGMArec..." -ForegroundColor Yellow
        Stop-Process -Name "SIGMArec" -Force
        Start-Sleep -Seconds 2
    }
}

# Check for python.exe processes running SIGMArec and close them
$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
foreach ($process in $pythonProcesses) {
    try {
        $commandLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine
        if ($commandLine -and ($commandLine -like "*sigmarec*" -or $commandLine -like "*src*")) {
            Write-Host "SIGMArec process maybe running from source (PID: $($process.Id))." -ForegroundColor Yellow
            $response = Read-Host "Do you want to close it? (Y/n)"
            if ($response -eq 'n' -or $response -eq 'N') {
                Write-Host "Skipping process termination." -ForegroundColor Yellow
            } else {
                Write-Host "Stopping SIGMArec..." -ForegroundColor Yellow
                Stop-Process -Id $process.Id -Force
            }
        }
    } catch {
        # Ignore errors when checking command line (process might have already exited)
    }
}
Start-Sleep -Seconds 1

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
