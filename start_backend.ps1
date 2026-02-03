$env:PYTHONPATH = "src"
$venvPython = ".\.venv\Scripts\python.exe"

# Load .env file
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim().Trim('"')
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
    Write-Host "Loaded environment variables from .env" -ForegroundColor Green
}

if (Test-Path $venvPython) {
    Write-Host "Found virtual environment. Starting backend..." -ForegroundColor Cyan
    # Run uvicorn as a module, treating 'app' as the entry point since 'src' is in PYTHONPATH
    & $venvPython -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
} else {
    Write-Host "Error: Virtual environment not found at $venvPython" -ForegroundColor Red
    Write-Host "Trying global python..."
    python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
}
