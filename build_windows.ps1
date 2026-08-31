$ErrorActionPreference = "Stop"

Write-Host "Building SegyViewer for Windows..."

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e ".[dev]"

Write-Host "Running tests..."
& .\.venv\Scripts\python.exe -m pytest -v

Write-Host "Cleaning previous build output..."
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue

Write-Host "Running PyInstaller..."
& .\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm SegyViewer.spec

Write-Host ""
Write-Host "Build complete."
Write-Host "Executable: dist\SegyViewer\SegyViewer.exe"
