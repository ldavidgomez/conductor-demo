[CmdletBinding()]
param(
    [string]$Baseline = "demo-ready"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

git -C $repoRoot rev-parse --verify "$Baseline^{commit}" | Out-Null

Write-Host "Restoring demo baseline: $Baseline"
git -C $repoRoot reset --hard $Baseline

# Workflow runs can create artifacts that Git does not track. Clean only the
# known runtime locations, never arbitrary files in the repository.
$runtimePaths = @(
    ".agentops/tickets/accepted",
    ".agentops/tickets/blocked",
    ".agentops/tickets/changes-requested",
    ".agentops/tickets/done",
    ".agentops/tickets/rejected",
    ".agentops/tickets/ticket-invalid",
    ".agentops/tickets/in-progress/TASK-20261006-003-happy-path",
    "demo-app/tests",
    "demo-app/__pycache__"
)

foreach ($relativePath in $runtimePaths) {
    $path = Join-Path $repoRoot $relativePath
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Recurse -Force
    }
}

Write-Host "Demo reset complete."
git -C $repoRoot status --short
