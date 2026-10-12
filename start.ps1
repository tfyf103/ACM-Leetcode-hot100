# Windows PowerShell 5.1 compatible; no downloads or conda activation needed.
$appArguments = @($args)
$ErrorActionPreference = 'Continue'
$candidates = New-Object System.Collections.Generic.List[object]
$seen = @{}

function Add-PythonCandidate([string]$Executable, [string[]]$Prefix = @()) {
    if ([string]::IsNullOrWhiteSpace($Executable)) { return }
    $Executable = [Environment]::ExpandEnvironmentVariables($Executable.Trim().Trim('"'))
    # These are Microsoft Store aliases, not installed interpreters.
    if ($Executable -match '\\Microsoft\\WindowsApps\\') { return }
    $key = $Executable + '|' + ($Prefix -join ' ')
    if (!$seen.ContainsKey($key) -and (Test-Path -LiteralPath $Executable -PathType Leaf)) {
        $seen[$key] = $true
        $candidates.Add([pscustomobject]@{ Executable = $Executable; Prefix = $Prefix })
    }
}

function Add-PythonRoot([string]$Root) {
    if (![string]::IsNullOrWhiteSpace($Root)) {
        Add-PythonCandidate (Join-Path $Root 'python.exe')
    }
}

# An explicit local override should fail visibly if it is wrong.
$override = $env:ACM_PYTHON
$configPath = Join-Path $PSScriptRoot 'python-path.txt'
if (!$override -and (Test-Path -LiteralPath $configPath)) {
    $override = (Get-Content -LiteralPath $configPath -Raw -Encoding UTF8).Trim()
}
if ($override) {
    Add-PythonCandidate $override
} else {
    Add-PythonRoot (Join-Path $PSScriptRoot '.venv\Scripts')
    Add-PythonRoot $env:CONDA_PREFIX
    if ($env:VIRTUAL_ENV) { Add-PythonRoot (Join-Path $env:VIRTUAL_ENV 'Scripts') }
    foreach ($name in @('python.exe', 'python3.exe', 'py.exe')) {
        foreach ($command in @(Get-Command $name -All -CommandType Application -ErrorAction SilentlyContinue)) {
            if ($name -eq 'py.exe') { Add-PythonCandidate $command.Source @('-3') }
            else { Add-PythonCandidate $command.Source }
        }
    }
    # conda may be on PATH even when python is not (condabin or Library/bin).
    foreach ($command in @(Get-Command conda.exe, conda.bat -All -CommandType Application -ErrorAction SilentlyContinue)) {
        $directory = Split-Path -Parent $command.Source
        for ($level = 0; $level -lt 4 -and $directory; $level++) {
            Add-PythonRoot $directory
            $directory = Split-Path -Parent $directory
        }
    }
    $environments = Join-Path $env:USERPROFILE '.conda\environments.txt'
    if (Test-Path -LiteralPath $environments) {
        foreach ($root in Get-Content -LiteralPath $environments -Encoding UTF8) {
            Add-PythonRoot $root.Trim()
        }
    }
    $roots = @($env:USERPROFILE, $env:LOCALAPPDATA, $env:ProgramData)
    $roots += @(Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Root -match '^[A-Za-z]:\\$' } | ForEach-Object { $_.Root })
    foreach ($root in $roots) {
        if (!$root) { continue }
        foreach ($name in @('miniconda3', 'anaconda3', 'miniforge3', 'mambaforge')) {
            Add-PythonRoot (Join-Path $root $name)
        }
    }
    foreach ($key in @('HKCU:\Software\Python\PythonCore',
                        'HKLM:\Software\Python\PythonCore',
                        'HKLM:\Software\WOW6432Node\Python\PythonCore')) {
        foreach ($version in @(Get-ChildItem -LiteralPath $key -ErrorAction SilentlyContinue)) {
            $install = Get-Item -LiteralPath ($version.PSPath + '\InstallPath') -ErrorAction SilentlyContinue
            if ($install) {
                if ($install.GetValue('ExecutablePath')) {
                    Add-PythonCandidate $install.GetValue('ExecutablePath')
                } else {
                    Add-PythonRoot $install.GetValue('')
                }
            }
        }
    }
}

$selected = $null
foreach ($candidate in $candidates) {
    $prefix = @($candidate.Prefix)
    try {
        & $candidate.Executable @prefix -I -X utf8 -c 'import sys, sqlite3; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { $selected = $candidate; break }
    } catch {
        # Broken launchers and stale conda environments must not stop discovery.
    }
}
if (!$selected) {
    Write-Host '[ERROR] No working Python 3.9+ with sqlite3 was found.' -ForegroundColor Red
    if ($override) { Write-Host ('Invalid Python override: ' + $override) }
    Write-Host 'If Miniconda is installed, put its full python.exe path in python-path.txt.'
    Write-Host 'Example file contents: E:\Miniconda3\python.exe'
    Write-Host 'Or launch start.bat from an activated Anaconda / Miniconda Prompt.'
    exit 1
}

$prefix = @($selected.Prefix)
Write-Host ('[Python] ' + $selected.Executable)
& $selected.Executable @prefix -I -X utf8 -c 'import sys; print(sys.version.split()[0]); print(sys.executable)'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if ($appArguments.Count -eq 1 -and $appArguments[0] -eq '--check') { exit 0 }
Set-Location -LiteralPath $PSScriptRoot
& $selected.Executable @prefix -X utf8 (Join-Path $PSScriptRoot 'app.py') @appArguments
exit $LASTEXITCODE
