<#!
.SYNOPSIS
Creates a local Python environment, installs requirements, and runs the app.
.EXAMPLE
.\Start-App.ps1
.EXAMPLE
.\Start-App.ps1 -SetupOnly
.EXAMPLE
.\Start-App.ps1 -PythonExe 'C:\Python312\python.exe' -Port 8502
#>
[CmdletBinding()]
param(
    [string]$PythonExe,
    [ValidateRange(1024, 65535)][int]$Port = 8501,
    [switch]$SetupOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'

Push-Location -LiteralPath $projectRoot
try {
    if (-not (Test-Path -LiteralPath $venvPython)) {
        $pythonArgs = @()
        if ($PythonExe) {
            $bootstrapPython = (Get-Command $PythonExe -ErrorAction Stop).Source
        }
        elseif (Get-Command py -ErrorAction SilentlyContinue) {
            $bootstrapPython = (Get-Command py).Source
            $pythonArgs = @('-3')
        }
        elseif (Get-Command python -ErrorAction SilentlyContinue) {
            $bootstrapPython = (Get-Command python).Source
        }
        else {
            throw 'Install Python 3.12 from python.org, reopen VS Code, and run this script again. Or pass -PythonExe with the full path to python.exe.'
        }

        & $bootstrapPython @pythonArgs -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'
        if ($LASTEXITCODE -ne 0) { throw 'Python 3.10 or newer is required; Python 3.12 is recommended for this project.' }
        & $bootstrapPython @pythonArgs -m venv (Join-Path $projectRoot '.venv')
        if ($LASTEXITCODE -ne 0) { throw 'Could not create .venv. Check your Python installation.' }
    }

    & $venvPython -m pip install -r (Join-Path $projectRoot 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Check your internet connection and retry.' }

    if ($SetupOnly) {
        Write-Host 'Setup complete. Run .\Start-App.ps1 to open the app.'
    }
    else {
        Write-Host "Opening http://localhost:$Port - press Ctrl+C to stop."
        & $venvPython -m streamlit run (Join-Path $projectRoot 'streamlit_app.py') --server.port $Port
        if ($LASTEXITCODE -ne 0) { throw "Streamlit exited with code $LASTEXITCODE." }
    }
}
finally {
    Pop-Location
}
