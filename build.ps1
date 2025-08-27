# Check if SIGMArec is currently running and close it
$sigmarecProcess = Get-Process -Name "SIGMArec" -ErrorAction SilentlyContinue
if ($sigmarecProcess) {
    Write-Host "SIGMArec is currently running. Closing it..." -ForegroundColor Yellow
    Stop-Process -Name "SIGMArec" -Force
    Start-Sleep -Seconds 2
}

# Delete release folder if it already exists
if (Test-Path "release") {
    Remove-Item -Recurse -Force "release"
}

# Create release folder
New-Item -ItemType Directory -Path "release" -Force

# Install dependencies and build executable
py -m pip install -r requirements.txt
py -m PyInstaller --onefile --name="SIGMArec" --icon="./assets/SIGMArec.ico" --dist=./release/ --paths=src src/__main__.py --uac-admin

# Copy all assets except .ico
Copy-Item "assets/*" "release/" -Recurse -Exclude "*.ico"

# Include README.md
Copy-Item "README.md" "release/"

Write-Host "`n=== Package ready in ./release ==="