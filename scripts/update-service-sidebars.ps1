$services = @(
    @{ File = 'plumbing-services.html'; Prefix = 'pl'; Label = 'Plumbing Services' },
    @{ File = 'painting-finishing.html'; Prefix = 'pf'; Label = 'Painting & Finishing' },
    @{ File = 'emergency-services.html'; Prefix = 'es'; Label = 'Emergency Services' },
    @{ File = 'home-renovations.html'; Prefix = 'hr'; Label = 'Home Renovations' },
    @{ File = 'electrical-work.html'; Prefix = 'ew'; Label = 'Electrical Work' },
    @{ File = 'doors-windows.html'; Prefix = 'dw'; Label = 'Doors & Windows' },
    @{ File = 'handyman.html'; Prefix = 'hm'; Label = 'Handyman Services' },
    @{ File = 'custom-projects.html'; Prefix = 'cp'; Label = 'Custom Projects' },
    @{ File = 'carpentry-framing.html'; Prefix = 'cf'; Label = 'Carpentry & Framing' },
    @{ File = 'general-repairs.html'; Prefix = 'gr'; Label = 'General Repairs' }
)

$callCta = @'
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

$root = Join-Path $PSScriptRoot '..'
$servicesDir = Join-Path $root 'Services'

foreach ($svc in $services) {
    $path = Join-Path $servicesDir $svc.File
    if (-not (Test-Path $path)) {
        Write-Warning "Missing $path"
        continue
    }

    $content = Get-Content -Raw -Path $path
    $headingId = ($svc.File -replace '\.html$','') + '-sidebar-heading'
    $prefix = $svc.Prefix
    $label = $svc.Label

    $replacement = @"
                        <aside class="kg-service-sidebar" data-kg-enter="right" aria-labelledby="$headingId">
                            <div class="kg-pricing-sidebar-form">
                                <h4 id="$headingId">Get your free estimate</h4>
                                <p>Send the basics and we will follow up with clear pricing for your Pinellas County project.</p>
                                <form class="kg-contact-form" action="https://formspree.io/f/xzzvnpne" method="POST">
                                    <div class="kg-field">
                                        <label for="$prefix-name">Your name</label>
                                        <input type="text" id="$prefix-name" name="name" autocomplete="name" placeholder="First and last name" required>
                                    </div>
                                    <div class="kg-field">
                                        <label for="$prefix-phone">Phone</label>
                                        <input type="tel" id="$prefix-phone" name="phone" autocomplete="tel" inputmode="tel" placeholder="(813) 555-1234" required>
                                    </div>
                                    <div class="kg-field kg-field--optional">
                                        <label for="$prefix-message">Project details <span>(optional)</span></label>
                                        <textarea id="$prefix-message" name="message" rows="3" placeholder="Job type, city, or timing"></textarea>
                                    </div>
                                    <input type="hidden" name="_subject" value="Knight Group $label Estimate Request">
                                    <input type="hidden" name="request_type" value="$label / Estimate Request">
                                    <input type="hidden" name="_next" value="https://www.knightgroup.com/thank-you">
                                    <input class="kg-hp" type="text" name="address_2" autocomplete="off" tabindex="-1" aria-hidden="true">
                                    <button type="submit" class="kg-contact-form__submit">Get free estimate</button>
                                </form>
                            </div>

                            <div class="pricing-highlights">
                                <h4>Why homeowners choose Knight Group</h4>
                                <ul>
                                    <li>No 2-hour minimums</li>
                                    <li>Transparent, upfront pricing</li>
                                    <li>Registered and insured</li>
                                    <li>Free written estimates</li>
                                    <li>Local Safety Harbor business</li>
                                    <li>5.0 Google rating</li>
                                    <li>Journeyman plumbing background</li>
                                    <li>Pinellas County coverage</li>
                                </ul>
                            </div>

                            <h3>Quick contact</h3>
                            <div class="pricing-highlights">
$callCta
                                <p style="margin-top:16px;"><strong>Email:</strong> <a href="mailto:nknight@knightgroup.com">nknight@knightgroup.com</a></p>
                                <p><strong>Hours:</strong> Mon&ndash;Fri 8 AM&ndash;5 PM<br>Weekends and after hours: emergency calls only</p>
                            </div>
                        </aside>
"@

    $pattern = '(?s)<aside class="kg-service-sidebar"[^>]*>.*?</aside>'
    if ($content -notmatch $pattern) {
        Write-Warning "No sidebar match in $($svc.File)"
        continue
    }

    $updated = [regex]::Replace($content, $pattern, $replacement, 1)
    Set-Content -Path $path -Value $updated -NoNewline -Encoding utf8
    Write-Host "Updated $($svc.File)"
}
