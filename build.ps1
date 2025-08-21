# Delete release folder if it already exists
if (Test-Path "release") {
    Remove-Item -Recurse -Force "release"
}

# Create release folder
New-Item -ItemType Directory -Path "release" -Force

# Install dependencies and build executable
py -m pip install -r requirements.txt
py -m PyInstaller --onefile --name="SIGMArec" --icon="./assets/SIGMArec.ico" --dist=./release/ --paths=src src/__main__.py --uac-admin

# Copy all assets except .ico and config.toml=
Copy-Item "assets/*" "release/" -Recurse -Exclude "*.ico", "config.toml"

# Include README.md
Copy-Item "README.md" "release/"

Write-Host "`n=== Package ready in ./release ==="