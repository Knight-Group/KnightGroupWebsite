# Google Search Console — re-index checklist

After deploying Phase 2 content (trust guides + hurricane page), request indexing for stale and new URLs.

## One-time hosting checks (Phase 3)

GitHub Pages hosts `knightgroup.com`. In the repo **Settings → Pages**:

1. **Enforce HTTPS** — must be enabled so `http://www.knightgroup.com/` redirects to HTTPS (Ahrefs still flags dual HTTP/HTTPS 200 responses when this is off).
2. Confirm **Custom domain** is `www.knightgroup.com` (CNAME file matches).
3. **Resubmit sitemap** in GSC: `https://www.knightgroup.com/sitemap.xml` (also Bing Webmaster Tools).

These cannot be fixed in `.htaccess` on GitHub Pages — that file is reference-only for a future cPanel move.

## Priority URLs — request indexing in GSC

Use **URL Inspection → Request indexing** for each (batch over 2–3 days if GSC rate-limits).

### Stale snippets (pre-2024 rebrand)

Google may still show “Auto Services & Remote IT” on these:

- `https://www.knightgroup.com/`
- `https://www.knightgroup.com/Services/handyman`
- `https://www.knightgroup.com/Services/plumbing-services`
- `https://www.knightgroup.com/about`

### New trust and conversion pages (Phase 2)

- `https://www.knightgroup.com/pricing-no-2-hour-minimum`
- `https://www.knightgroup.com/plumber-background-handyman`
- `https://www.knightgroup.com/rental-turnover-handyman`
- `https://www.knightgroup.com/handyman-scope-florida`
- `https://www.knightgroup.com/hurricane-repair-handyman-pinellas`

### Hubs to refresh

- `https://www.knightgroup.com/services`
- `https://www.knightgroup.com/service-areas`
- `https://www.knightgroup.com/pinellas-handyman`
- `https://www.knightgroup.com/clearwater-handyman`

## After requesting indexing

1. GSC → **Sitemaps** → resubmit `sitemap.xml`.
2. Wait 7–14 days, then check **Performance → Pages** for impressions on service URLs (not just homepage).
3. Run [Rich Results Test](https://search.google.com/test/rich-results) on one trust page and one service page to confirm FAQ schema.
4. Optional: IndexNow ping if your host supports it (GitHub Pages does not natively).

## What to skip for now

- **Review follow-up automation** — see `REVIEW-FOLLOW-UP-STRATEGY.md`; manual process only until approved.
- **Bulk new city pages** — wait until core service URLs earn clicks (see `KNIGHT-GROUP-GROWTH-PLAYBOOK-2026-06-03.md`).

## Weekly scorecard (fill in)

| Week | URLs indexed (new) | Homepage snippet updated? | Service page impressions | Notes |
| --- | --- | --- | --- | --- |
| 1 | | | | |
| 2 | | | | |
