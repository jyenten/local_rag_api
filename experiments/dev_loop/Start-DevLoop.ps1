param(
    [ValidateSet('start', 'check')]
    [string]$Action = 'start',
    [string]$ConfigPath = (Join-Path $PSScriptRoot '.runs\service.json')
)

$ErrorActionPreference = 'Stop'
$resolvedConfig = (Resolve-Path -LiteralPath $ConfigPath).Path
$serviceProfile = Get-Content -LiteralPath $resolvedConfig -Raw | ConvertFrom-Json
if ($serviceProfile.schema_version -notin @(1, 2) -or $serviceProfile.service -ne 'local-rag-dev-loop') {
    throw 'Not a dev-loop service profile. Run python -m experiments.dev_loop.service init first.'
}
$pythonExecutable = $serviceProfile.python_executable
if ([string]::IsNullOrWhiteSpace($pythonExecutable) -or
    -not (Test-Path -LiteralPath $pythonExecutable -PathType Leaf)) {
    throw 'Configured Python executable is unavailable.'
}

$repositoryRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$serviceExitCode = 1
Push-Location -LiteralPath $repositoryRoot
try {
    & $pythonExecutable -m experiments.dev_loop.service $Action --config $resolvedConfig
    $serviceExitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}
exit $serviceExitCode
