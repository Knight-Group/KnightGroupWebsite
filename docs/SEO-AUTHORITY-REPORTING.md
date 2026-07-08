# SEO Authority And Reporting Follow-Up

Use this after each site deployment and each full GSC audit.

## Offsite Authority Actions

- Google Business Profile: keep the primary category aligned to handyman/home repair, keep service areas current, add the `https://www.knightgroup.com/Services/handyman` and `https://www.knightgroup.com/booking` links where available, and post recent before/after projects weekly.
- Reviews: ask satisfied customers to mention the city and job type naturally, for example “door repair in Clearwater” or “drywall repair in Safety Harbor.” Do not script or incentivize reviews.
- Citations: keep NAP consistent as `Knight Group Handyman Services LLC`, `(813) 649-3341`, and `1225 7th St S, Safety Harbor, FL 34695` across Google, Bing, Apple, Yelp, Facebook, Nextdoor, Angi, and local chamber/property-manager directories.
- Social proof: reuse gallery project photos with captions that name the service type and service area, then link back to the matching service page or gallery detail page.
- Local partnerships: prioritize links or mentions from property managers, real estate agents, HOA/vendor pages, senior living communities, and local businesses that can refer recurring repair work.

## Weekly Reporting Loop

1. Run the full audit when changes have been deployed and Google has had time to crawl:

```powershell
node E:\GSC Auditer\tools\audit.mjs --ui
```

1. Read `.gsc-audit-latest.json`, then open the latest `gsc-audit/<date>/report.md`, `analysis.json`, and `api/performance.json`.
1. Compare these query groups against `docs/QUERY-PAGE-MAP.md`:
   - `handyman`, `handyman services`, `handyman services near me`
   - `home repair near me`, `home repair services clearwater fl`
   - `handyman clearwater`, `handyman largo`, `handyman temple terrace`
   - `handyman plumbing prices`, `small job carpenter near me`, `door repair`
1. Record wins and regressions in `KNIGHT-GROUP-AUDIT-STATUS.md` without overwriting the raw audit exports.
1. If a mapped query is splitting impressions across multiple pages, update internal links and metadata so the primary page in `docs/QUERY-PAGE-MAP.md` owns the intent.

## Success Metrics

- Broad handyman terms move from positions 11-12 into top 10.
- Priority pages improve CTR before impressions grow: `/Services/handyman`, `/Services/general-repairs`, `/Services/home-repair-near-me`, `/pricing`, `/clearwater-handyman`, and `/pinellas-handyman`.
- More form submissions reach `/thank-you` with `form_success` in GTM/dataLayer.
- More phone leads fire `phone_click` from header, footer, and body CTAs.
- New gallery proof pages include real project images, complete descriptions, and links back to the service page they support.
