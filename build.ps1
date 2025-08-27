# Check if SIGMArec is currently running and close it
$sigmarecProcess = Get-Process -Name "SIGMArec" -ErrorAction SilentlyContinue
if ($sigmarecProcess) {
    Write-Host "SIGMArec is currently running. Closing it..." -ForegroundColor Yellow
    Stop-Process -Name "SIGMArec" -Force
    Start-Sleep -Seconds 2
}

# Delete release folder if it already exists
if (Test-Path "release") {
    Write-Host "Deleting release folder..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "release"
}

# Create release folder
Write-Host "Creating new release folder..." -ForegroundColor Green
New-Item -ItemType Directory -Path "release" -Force

# Rewrite src/defaults.py with the contents of assets/games.json and assets/example.config.toml
if ((Test-Path "assets/games.json") -and (Test-Path "assets/example.config.toml")) {
    Write-Host "Updating defaults.py..." -ForegroundColor Green
    $gamesJsonContent = Get-Content "assets/games.json" -Raw
    $exampleConfigTomlContent = Get-Content "assets/example.config.toml" -Raw
    Set-Content "src/defaults.py" @"
"""
Default config.toml and games.json
"""

DEFAULT_GAMES = """$gamesJsonContent
"""

DEFAULT_CONFIG = """$exampleConfigTomlContent
"""
"@
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Green
py -m pip install -r requirements.txt

# Build executable
Write-Host "Building executable..." -ForegroundColor Green
py -m PyInstaller --onefile --name="SIGMArec" --icon="./assets/SIGMArec.ico" --dist=./release/ --paths=src src/__main__.py --uac-admin

# Copy all assets except .ico
Write-Host "Copying assets..." -ForegroundColor Green
Copy-Item "assets/*" "release/" -Recurse -Exclude "*.ico"

# Include README.md
Write-Host "Copying README.md..." -ForegroundColor Green
Copy-Item "README.md" "release/"

Write-Host "`n=== Package ready in ./release ==="