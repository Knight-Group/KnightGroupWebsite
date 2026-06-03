# Weekly GSC export for knightgroup.com (uses Knight Logics gsc_api.py)
$ErrorActionPreference = "Stop"

$siteRoot = Split-Path -Parent $PSScriptRoot
$mainSite = "E:\KnightLogics-Growth-System\MainSite"
$date = Get-Date -Format "yyyy-MM-dd"
$outDir = Join-Path $siteRoot "seo-audit\$date"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$gscSite = if ($env:KNIGHTGROUP_GSC_SITE_URL) { $env:KNIGHTGROUP_GSC_SITE_URL } else { "https://www.knightgroup.com/" }
$env:GSC_SITE_URL = $gscSite

Write-Host "Knight Group weekly GSC pull"
Write-Host "  Property: $gscSite"
Write-Host "  Output:   $outDir"

Push-Location $mainSite
try {
    python scripts/gsc_api.py check
    if ($LASTEXITCODE -ne 0) { throw "gsc_api.py check failed" }

    python scripts/gsc_api.py queries --days 28 --export (Join-Path $outDir "gsc-queries-api.json")
    python scripts/gsc_api.py pages --days 28 --export (Join-Path $outDir "gsc-pages-api.json")
}
finally {
    Pop-Location
}

Write-Host "Done. Review JSON in $outDir"
