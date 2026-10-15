[CmdletBinding()]
param(
    [string]$Baseline = "main"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

git -C $repoRoot rev-parse --verify "$Baseline^{commit}" | Out-Null

# Restore only the demo data that workflow runs modify. The branch is not
# moved, so workflows, scripts, tests and docs keep their latest version.
$demoPaths = @(".agentops", "demo-app")

Write-Host "Restoring demo data from: $Baseline"
git -C $repoRoot restore --source=$Baseline --staged --worktree -- @demoPaths
if ($LASTEXITCODE -ne 0) {
    throw "git restore failed with exit code $LASTEXITCODE"
}

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
    ".agentops/tickets/in-progress/TASK-20261006-002-reviewer-changes/review-result.md",
    ".agentops/demo-runtime",
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
