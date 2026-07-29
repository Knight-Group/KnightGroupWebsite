# Knight Group Audit Status

Last updated: 2026-07-29

## 2026-07-29 GSC Audit + CTR Conversion Push

Fresh Playwright + API audit: `gsc-audit/2026-07-29/` (source: `E:/Website Audit/GSC`).

### Live GSC snapshot (period ~Apr 30–Jul 26)

- Clicks **57** · Impressions **17,198** · CTR **0.33%** · Avg position **21.6**
- User UI later in the window showed ~71 clicks / 20.1K impressions / 0.4% CTR — directionally up from Jul 18 (30 / 11K / 0.27%).
- Indexed **76** · Not indexed **56** · Sitemap **113** URLs after removing `llms.txt` (was 114).
- Still not indexed on inspection: `/services`, `/Services/general-repairs`.
- Near-page-one CTR disasters (0 clicks): `handyman temple terrace` (~pos 6.9), `handyman hillsborough county` (~pos 7.1), plus `handyman near me` (1,500 impressions / 0.07% CTR).

### Implemented this round

- Ran full GSC audit with UI exports; updated `.gsc-audit-latest.json`.
- Rewrote polluted Serper-scraped metas (Denver, Baltimore, TaskRabbit, Mr. Handyman, “definitive list,” etc.) across money + niche service pages.
- Replaced keyword-stuffed geo metas (`handyman near me small jobs`, `carpentry services near me`, Pinellas phrases on Hillsborough pages).
- CTR-focused titles on high-impression pages: `/Services/handyman`, `/pricing`, Clearwater, Largo, Temple Terrace, Hillsborough, Pinellas, Tampa, home-repair, small-job carpenter, doors/windows.
- Hero Book + Call CTAs on handyman, home-repair, general-repairs, Clearwater, Temple Terrace, Hillsborough.
- Fixed Temple Terrace body/FAQ stuffing; Hillsborough opening; Town 'n' Country false HQ claim.
- Updated `geo_serp_keywords.py` so Hillsborough/Pasco cities no longer map to Pinellas SERP queries.
- Cleaned `geo_seo_copy.py` for Temple Terrace, Tampa, Town 'n' Country, Northdale (prevents regen regressions).
- Removed `llms.txt` from sitemap builder; regenerated `sitemap.xml` (113 URLs).
- Hardened `repair-meta-descriptions.py` bad-pattern list.

### Indexing bucket interpretation (matches GSC UI)

| Bucket | Count | Likely cause / action |
| --- | ---: | --- |
| Discovered – not indexed | ~33 | New/gallery/long-tail pages; strengthen internal links + quality; wait + request indexing after deploy |
| Crawled – not indexed | ~16 | Thin/duplicate/geo-mismatch quality; geo copy cleanup this round |
| Excluded by noindex | 3 | Policy pages — intentional |
| Blocked by robots.txt | 2 | Legacy programming/furniture soft-redirect URLs — intentional |
| Page with redirect | 2 | Same legacy soft redirects — GH Pages cannot hard-301 without edge config |

Manual actions / security / HTTPS “issues” in the automated report are UI-scrape noise (tables empty; HTTPS shows 0 non-HTTPS issues).

### Next after deploy

1. Deploy this workspace to GitHub Pages.
2. `node E:\Website Audit\GSC\tools\submit-indexing.mjs --site knightgroup.com` for money URLs + `/services` + `/Services/general-repairs`.
3. Validate Temple Terrace / Hillsborough / handyman titles in live SERP after recrawl.
4. Offsite: GBP posts + review asks naming city + job type (see `docs/SEO-AUTHORITY-REPORTING.md`).

## 2026-07-08 GSC Growth Implementation

- Added sitewide lead measurement for Formspree starts/submits, thank-you success events, and phone CTA clicks.
- Cleaned off-topic and truncated metadata on priority service pages, including home repair, doors/windows, cabinet repair, custom projects, handyman, general repairs, plumbing, electrical, carpentry, small jobs, small-job carpenter, and sink/faucet repair.
- Added `docs/QUERY-PAGE-MAP.md` so high-value GSC query clusters have one assigned primary landing page.
- Strengthened revenue-page SERP and first-screen copy for key service and city pages.
- Improved crawlable links on `/services` and `/Services/general-repairs`, then removed utility `llms.txt` from `sitemap.xml`.
- Added a richer gallery proof schema pattern on `gallery/door-lock-repair-before-after.html`.
- Added `docs/SEO-AUTHORITY-REPORTING.md` for offsite authority actions and weekly audit follow-up.
