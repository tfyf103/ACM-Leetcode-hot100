# Compatibility entry point; keep all discovery logic in the root launcher.
& (Join-Path (Split-Path -Parent $PSScriptRoot) "start.ps1") @args
exit $LASTEXITCODE
