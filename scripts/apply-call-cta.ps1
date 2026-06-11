$root = "e:\All Client Websites\KnightGroupWebsite"

$ctaDark = @'
<a href="tel:+18136493341" class="header-btn-primary kg-header-call" title="Click to call or text (813) 649-3341" aria-label="Call or text (813) 649-3341">
    <span class="kg-header-call__icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="18" height="18" focusable="false"><path fill="currentColor" d="M6.6 10.8c1.5 2.9 3.7 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.5.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.3 21 3 13.7 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.2.2 2.4.6 3.5.1.3 0 .7-.2 1L6.6 10.8z"/></svg>
    </span>
    <span class="kg-header-call__text">
        <span class="kg-header-call__label">Call or Text</span>
        <span class="kg-header-call__number">(813) 649-3341</span>
    </span>
</a>
'@

$ctaLight = @'
<a href="tel:+18136493341" class="header-btn-primary kg-header-call kg-header-call--light" title="Click to call or text (813) 649-3341" aria-label="Call or text (813) 649-3341">
    <span class="kg-header-call__icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="18" height="18" focusable="false"><path fill="currentColor" d="M6.6 10.8c1.5 2.9 3.7 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.5.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.3 21 3 13.7 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.2.2 2.4.6 3.5.1.3 0 .7-.2 1L6.6 10.8z"/></svg>
    </span>
    <span class="kg-header-call__text">
        <span class="kg-header-call__label">Call or Text</span>
        <span class="kg-header-call__number">(813) 649-3341</span>
    </span>
</a>
'@

$patterns = @(
    @{ Old = '<a href="tel:+18136493341" class="kg-btn kg-btn--ghost">Call (813) 649-3341</a>'; New = $ctaDark },
    @{ Old = '<a class="kg-btn kg-btn--ghost" href="tel:+18136493341">Call (813) 649-3341</a>'; New = $ctaDark },
    @{ Old = '<a href="tel:+18136493341" class="btn-primary">Call (813) 649-3341</a>'; New = $ctaDark },
    @{ Old = '<a class="btn-primary" href="tel:+18136493341">Call (813) 649-3341</a>'; New = $ctaDark },
    @{ Old = '<a class="btn" href="tel:+18136493341">Call (813) 649-3341</a>'; New = $ctaDark },
    @{ Old = '<a href="tel:8136493341" class="btn-primary">Call (813) 649-3341</a>'; New = $ctaDark },
    @{ Old = '<a href="tel:8136493341" class="emergency-call">Call Now! (813) 649-3341</a>'; New = $ctaDark },
    @{ Old = '<a class="btn" href="tel:+18136493341" style="background:#fff;color:#9a2f2f">Call (813) 649-3341</a>'; New = $ctaDark },
    @{ Old = 'class="kg-call-cta kg-call-cta--dark"'; New = 'class="header-btn-primary kg-header-call"' },
    @{ Old = 'class="kg-call-cta kg-call-cta--light"'; New = 'class="header-btn-primary kg-header-call kg-header-call--light"' }
)

$files = Get-ChildItem -Path $root -Filter *.html -Recurse |
    Where-Object { $_.FullName -notmatch 'Chess-Game-main' }

$changed = 0
foreach ($file in $files) {
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    $original = $content
    foreach ($pattern in $patterns) {
        $content = $content.Replace($pattern.Old, $pattern.New)
    }
    if ($content -ne $original) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
        Write-Host "Updated: $($file.FullName)"
        $changed++
    }
}

Write-Host "Done. $changed file(s) updated."
