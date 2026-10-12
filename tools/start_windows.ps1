# Use ASCII here so Windows PowerShell 5.1 can read this without a BOM.
# This launcher does not install packages or change the user's PATH.
$projectRoot = Split-Path -Parent $PSScriptRoot
$appArguments = @($args)
$candidates = New-Object 'System.Collections.Generic.List[string]'
$seen = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)

function Add-PythonCandidate([string] $path) {
    if ($path -and $seen.Add($path)) {
        $candidates.Add($path)
    }
}

function Find-WorkingPython([string] $command) {
    # Skip Microsoft Store aliases: probing them can open the Store.
    if ($command -like '*\Microsoft\WindowsApps\*' -or
        !(Test-Path -LiteralPath $command -PathType Leaf)) {
        return $null
    }
    $probeArguments = @('-I', '-X', 'utf8', '-c',
        'import sys; assert sys.version_info >= (3, 9); import sqlite3, http.server; print(sys.executable)')
    if ((Split-Path -Leaf $command) -ieq 'py.exe') {
        $probeArguments = @('-3') + $probeArguments
    }
    try {
        $result = @(& $command @probeArguments 2>$null)
        if ($LASTEXITCODE -eq 0 -and $result.Count -eq 1 -and
            (Test-Path -LiteralPath ([string] $result[0]) -PathType Leaf)) {
            return [string] $result[0]
        }
    } catch {
        # A stale launcher/installation must not hide a later working Python.
    }
    return $null
}

if ($env:ACM_PYTHON) {
    # An explicit choice should fail clearly instead of silently using another environment.
    Add-PythonCandidate $env:ACM_PYTHON
} else {
    Add-PythonCandidate (Join-Path $projectRoot '.venv\Scripts\python.exe')
    if ($env:CONDA_PREFIX) {
        Add-PythonCandidate (Join-Path $env:CONDA_PREFIX 'python.exe')
    }
    foreach ($name in @('python.exe', 'python3.exe', 'py.exe')) {
        foreach ($command in @(Get-Command $name -CommandType Application -All -ErrorAction SilentlyContinue)) {
            Add-PythonCandidate $command.Source
        }
    }
    # Conda records custom-drive installs here even when it is not on PATH.
    $environmentsFile = Join-Path $env:USERPROFILE '.conda\environments.txt'
    if (Test-Path -LiteralPath $environmentsFile) {
        foreach ($environment in Get-Content -LiteralPath $environmentsFile -Encoding UTF8) {
            if ($environment.Trim()) {
                Add-PythonCandidate (Join-Path $environment.Trim() 'python.exe')
            }
        }
    }
    foreach ($base in @($env:USERPROFILE, $env:LOCALAPPDATA, $env:ProgramData)) {
        if ($base) {
            foreach ($distribution in @('miniconda3', 'anaconda3', 'miniforge3')) {
                Add-PythonCandidate (Join-Path $base "$distribution\python.exe")
            }
        }
    }
    foreach ($key in @('HKCU:\Software\Python\PythonCore',
                        'HKLM:\Software\Python\PythonCore',
                        'HKLM:\Software\WOW6432Node\Python\PythonCore')) {
        foreach ($version in @(Get-ChildItem -LiteralPath $key -ErrorAction SilentlyContinue)) {
            $installKey = Get-Item -LiteralPath ($version.PSPath + '\InstallPath') -ErrorAction SilentlyContinue
            if ($installKey) {
                $executable = $installKey.GetValue('ExecutablePath')
                if ($executable) {
                    Add-PythonCandidate $executable
                } elseif ($installKey.GetValue('')) {
                    Add-PythonCandidate (Join-Path $installKey.GetValue('') 'python.exe')
                }
            }
        }
    }
}

$selectedPython = $null
foreach ($candidate in $candidates) {
    $selectedPython = Find-WorkingPython $candidate
    if ($selectedPython) { break }
}
if (!$selectedPython) {
    Write-Host 'No working Python 3.9+ (with sqlite3) was found.'
    Write-Host 'Miniconda / Anaconda are supported. In an Anaconda Prompt, run start.bat.'
    Write-Host 'Or set ACM_PYTHON to the full path of python.exe before starting:'
    Write-Host '  set "ACM_PYTHON=E:\Miniconda3\python.exe"'
    Write-Host '  start.bat'
    exit 1
}

Write-Host "Python: $selectedPython"
if ($appArguments.Count -eq 1 -and $appArguments[0] -eq '--check') {
    & $selectedPython --version
    exit $LASTEXITCODE
}
Set-Location -LiteralPath $projectRoot
& $selectedPython -X utf8 (Join-Path $projectRoot 'app.py') @appArguments
exit $LASTEXITCODE
