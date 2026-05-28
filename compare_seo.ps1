$pages = @(
    @{ local = "index.html"; live = "https://www.knightgroup.com/" },
    @{ local = "booking.html"; live = "https://www.knightgroup.com/booking" },
    @{ local = "contact.html"; live = "https://www.knightgroup.com/contact" },
    @{ local = "Services/handyman.html"; live = "https://www.knightgroup.com/Services/handyman" },
    @{ local = "Services/general-repairs.html"; live = "https://www.knightgroup.com/Services/general-repairs" },
    @{ local = "Services/painting-finishing.html"; live = "https://www.knightgroup.com/Services/painting-finishing" },
    @{ local = "Services/home-renovations.html"; live = "https://www.knightgroup.com/Services/home-renovations" },
    @{ local = "galleries.html"; live = "https://www.knightgroup.com/galleries" },
    @{ local = "service-areas.html"; live = "https://www.knightgroup.com/service-areas" }
)

function Get-Info($content) {
    $title = ""
    if ($content -match "<title[^>]*>(.*?)</title>") {
        $title = $Matches[1].Trim()
    }
    $desc = ""
    # Try to find meta description
    if ($content -match '<meta\s+name=["'']description["'']\s+content=["'']([^"'']*)["'']') {
        $desc = $Matches[1].Trim()
    } elseif ($content -match '<meta\s+content=["'']([^"'']*)["'']\s+name=["'']description["'']') {
        $desc = $Matches[1].Trim()
    }
    return @{ title = $title; desc = $desc }
}

foreach ($page in $pages) {
    Write-Host "Page: $($page.local)"
    
    $localPath = Join-Path (Get-Location) $page.local
    if (Test-Path $localPath) {
        $localContent = Get-Content $localPath -Raw
        $localInfo = Get-Info $localContent
    } else {
        $localInfo = @{ title = "[N/A]"; desc = "[N/A]" }
    }
    
    try {
        $response = Invoke-WebRequest -Uri $page.live -UseBasicParsing -TimeoutSec 15
        $liveInfo = Get-Info $response.Content
    } catch {
        $liveInfo = @{ title = "[ERROR]"; desc = "[ERROR]" }
    }
    
    Write-Host "  Local Title: $($localInfo.title)"
    Write-Host "  Live Title:  $($liveInfo.title)"
    Write-Host "  Local Desc:  $($localInfo.desc)"
    Write-Host "  Live Desc:   $($liveInfo.desc)"
    
    if ($localInfo.title -eq $liveInfo.title -and $localInfo.desc -eq $liveInfo.desc) {
        Write-Host "  STATUS: MATCH"
    } else {
        Write-Host "  STATUS: MISMATCH"
    }
    Write-Host ""
}
