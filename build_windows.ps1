$ErrorActionPreference = "Stop"

Write-Host "Building SegyViewer for Windows..."

function Test-CondaPython([string]$PythonExe) {
    $basePrefix = & $PythonExe -c "import sys; print(sys.base_prefix)"
    return ($basePrefix -match "(?i)(conda|anaconda|miniconda)")
}

if (Test-Path ".venv\Scripts\python.exe") {
    if (Test-CondaPython ".\.venv\Scripts\python.exe") {
        Write-Host ""
        Write-Host "The current .venv was created from a Conda/Miniconda Python installation." -ForegroundColor Yellow
        Write-Host "PyInstaller may build successfully but omit Conda runtime DLLs such as ffi.dll." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Delete .venv and recreate it with the standard CPython distribution:" -ForegroundColor Yellow
        Write-Host "  Remove-Item -Recurse -Force .venv"
        Write-Host "  py -3.11 -m venv .venv"
        Write-Host "  .\build_windows.ps1"
        Write-Host ""
        throw "Unsupported Conda-based build environment. Use standard CPython for Windows packaging."
    }
}
else {
    if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
        throw "Python Launcher (py.exe) was not found. Install standard CPython 3.11 from python.org before building."
    }

    $launcherPython = & py -3.11 -c "import sys; print(sys.executable)"
    if ($LASTEXITCODE -ne 0) {
        throw "Standard CPython 3.11 was not found. Install Python 3.11 from python.org before building."
    }

    if ($launcherPython -match "(?i)(conda|anaconda|miniconda)") {
        throw "The Python 3.11 selected by py.exe is Conda-based. Install standard CPython 3.11 from python.org before building."
    }

    Write-Host "Creating virtual environment with standard CPython 3.11..."
    & py -3.11 -m venv .venv
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
