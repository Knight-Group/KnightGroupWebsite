#Requires -Version 5.1
# Pull Knight Group GBP reviews into data/google-reviews.json and ship the feed.
$ErrorActionPreference = "Stop"
$SiteRoot = Split-Path -Parent $PSScriptRoot
$LogDir = Join-Path $SiteRoot "seo-audit"
$LogPath = Join-Path $LogDir "gbp-review-sync.log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log([string]$Message) {
    $line = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -LiteralPath $LogPath -Value $line -Encoding utf8
    Write-Host $line
}

Set-Location $SiteRoot
Write-Log "Starting GBP review feed sync"

try {
    $node = Get-Command node -ErrorAction Stop
    & $node.Source "scripts/sync-google-reviews.js" --feed-only --skip-hours
    if ($LASTEXITCODE -ne 0) { throw "sync-google-reviews.js exited $LASTEXITCODE" }
} catch {
    Write-Log ("SYNC FAILED: " + $_.Exception.Message)
    exit 1
}

$paths = @(
    "data/google-reviews.json"
)
git add -- @paths
$staged = @(git diff --cached --name-only -- @paths)
if (-not $staged) {
    Write-Log "Feed unchanged; nothing to deploy"
    exit 0
}

git commit -- $paths -m "Refresh Knight Group GBP review count and homepage review feed."
if ($LASTEXITCODE -ne 0) {
    Write-Log "git commit failed"
    exit 1
}

git push origin HEAD
if ($LASTEXITCODE -ne 0) {
    Write-Log "git push failed"
    exit 1
}

Write-Log "Deployed refreshed GBP review feed"
exit 0
