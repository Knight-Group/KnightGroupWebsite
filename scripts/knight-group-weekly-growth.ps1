# Knight Group weekly growth loop: GSC pull + optional Serper + action report
$ErrorActionPreference = "Stop"

$siteRoot = Split-Path -Parent $PSScriptRoot
$mainSite = "E:\KnightLogics-Growth-System\MainSite"
$outreach = "E:\KnightLogics-Growth-System\CRM\OutreachEngine"
$date = Get-Date -Format "yyyy-MM-dd"
$outDir = Join-Path $siteRoot "seo-audit\$date"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$env:KNIGHTGROUP_GSC_SITE_URL = "https://www.knightgroup.com/"
$env:GSC_SITE_URL = $env:KNIGHTGROUP_GSC_SITE_URL

Write-Host "=== Knight Group weekly growth ($date) ==="

# 1) GSC API
Push-Location $mainSite
try {
    python scripts/gsc_api.py check
    python scripts/gsc_api.py queries --days 28 --export (Join-Path $outDir "gsc-queries-api.json")
    python scripts/gsc_api.py pages --days 28 --export (Join-Path $outDir "gsc-pages-api.json")
}
finally {
    Pop-Location
}

# 2) GBP reviews (if env configured)
Push-Location $siteRoot
try {
    npm run reviews:sync-google 2>&1 | Tee-Object -FilePath (Join-Path $outDir "gbp-reviews-sync.log")
}
catch {
    "GBP sync skipped or failed — see log" | Out-File (Join-Path $outDir "gbp-reviews-sync.log")
}
finally {
    Pop-Location
}

# 3) Serper SERP snapshot (uses SERPER_API_KEY from OutreachEngine .env)
$serpConfig = Join-Path $siteRoot "seo\knight-group-serp-config.json"
if ((Test-Path $serpConfig) -and (Test-Path $outreach)) {
    Push-Location $outreach
    try {
        python serp_intel.py --config $serpConfig --report --json --notes "knightgroup-$date"
        Copy-Item -Path "state\serp-reports" -Destination (Join-Path $outDir "serp-reports") -Recurse -ErrorAction SilentlyContinue
    }
    catch {
        "Serper run failed — check SERPER_API_KEY" | Out-File (Join-Path $outDir "serper-error.log")
    }
    finally {
        Pop-Location
    }
}

# 4) Simple action report (compare to prior week if exists)
$reportPath = Join-Path $outDir "WEEKLY-ACTION-REPORT.md"
$queriesPath = Join-Path $outDir "gsc-queries-api.json"
$lines = @(
    "# Knight Group weekly action report — $date",
    "",
    "## Automated pulls",
    "- GSC queries/pages (28 days)",
    "- GBP review sync (if credentials set)",
    "- Serper SERP (if API key set)",
    "",
    "## Recommended manual actions",
    "1. Review queries with impressions and 0 clicks — tighten title/meta on matching URL.",
    "2. Publish 1 GBP post linking to /booking or top service page.",
    "3. Request 1–2 Google reviews from recent jobs.",
    "4. URL-inspect any page changed on site this week.",
    "",
    "## Safe auto-improvements (next build)",
    "- Deploy refreshed google-reviews.json to homepage carousel",
    "- Flag CTR regressions vs prior week JSON",
    ""
)

if (Test-Path $queriesPath) {
    $q = Get-Content $queriesPath -Raw | ConvertFrom-Json
    $top = $q.rows | Sort-Object { [int]$_.impressions } -Descending | Select-Object -First 10
    $lines += "## Top GSC queries (this pull)"
    $lines += ""
    $lines += "| Query | Impressions | Clicks | Position |"
    $lines += "| --- | ---: | ---: | ---: |"
    foreach ($row in $top) {
        $lines += "| $($row.query) | $($row.impressions) | $($row.clicks) | $($row.position) |"
    }
}

$lines | Set-Content -Path $reportPath -Encoding utf8
Write-Host "Report: $reportPath"
Write-Host "Done."
