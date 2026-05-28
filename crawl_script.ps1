$sites = @(
    "https://www.knightgroup.com/",
    "https://screenteamllc.com/",
    "https://momsresintables.com/",
    "https://jnsbuilds.com/",
    "https://evidencedeskai.com/",
    "https://salspaintingrenovation.com/"
)
$exe = "C:\Program Files (x86)\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe"
$basePath = "E:\Nothing\screaming-frog-audits\2026-05-24"

# Metrics list to look for
$metricsToExtract = @(
    "Total Internal URLs",
    "Total Internal Indexable URLs",
    "Internal Client Error (4xx)",
    "Internal Server Error (5xx)",
    "Page Titles Over 60 Characters",
    "Meta Descriptions Over 155 Characters",
    "Low Content Pages",
    "Images Missing Alt Text",
    "Images Missing Alt Attribute",
    "Images Missing Size Attributes",
    "Canonicals Missing"
)

$results = @()

foreach ($site in $sites) {
    $domain = ($site -replace "https?://", "" -replace "/", "").Replace(".", "_")
    $siteFolder = Join-Path $basePath $domain
    if (!(Test-Path $siteFolder)) { New-Item -ItemType Directory -Path $siteFolder }

    Write-Host "Crawling $site..."
    # Run the crawl
    & $exe --crawl $site --headless --save-report "Crawl Overview" --output-folder "$siteFolder"
    
    $reportPath = Join-Path $siteFolder "crawl_overview.csv"
    if (Test-Path $reportPath) {
        $content = Import-Csv $reportPath -Header "Metric", "Count"
        $siteResults = [PSCustomObject]@{ Site = $site }
        foreach ($metricName in $metricsToExtract) {
            $row = $content | Where-Object { $_.Metric -like "*$metricName*" } | Select-Object -First 1
            $val = if ($row) { $row.Count } else { "N/A" }
            $siteResults | Add-Member -MemberType NoteProperty -Name $metricName -Value $val
        }
        $results += $siteResults
    } else {
        Write-Warning "Report not found for $site at $reportPath"
    }
}

$results | Format-Table -AutoSize
