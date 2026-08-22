# Monthly Knight Group SEO monitor

Run on the first business day of each month from this machine:

```powershell
node "E:\Website Audit\GSC\tools\audit.mjs" --site knightgroup.com --api-only --skip-inspection
node "E:\Website Audit\GSC\tools\resubmit-sitemaps.mjs" --site knightgroup.com --ui
```

If the GSC API token is expired (`invalid_grant`), finish `npm run auth` in `E:\Website Audit\GSC` first.

Compare every new run against the **2026-08-19 control group** (May 21–Aug 16, pre site changes):

`E:\All Client Websites\KnightGroupWebsite\gsc-audit\2026-08-19\CONTROL-GROUP.md`

Site totals to beat: **119 clicks / 36,453 impressions / 0.33% CTR / 21.1 position**. Re-measure the same pages and query clusters (Clearwater, Temple Terrace, Tarpon Springs, Largo, home repair, commercial handyman, fixtures/plumbing). Do not judge Home Watch or Lutz from that baseline.

Check:

1. Live `https://www.knightgroup.com/sitemap.xml` URL count vs GSC discovered pages.
2. Review count in `data/google-reviews.json` vs the Google profile (`npm run reviews:sync-google` in the website repo). That command also aligns GBP hours to Monday–Friday 8 AM–5 PM.
3. No new city×service pages added unless GSC shows a real query gap. No `/lutz-handyman`.
4. Homepage carousel still capped at 8 featured jobs.
5. Fixture/fan/faucet/switch/outlet language stays; do not claim a licensed electrician or plumber. Mold/roof/window claims still match `handyman-scope-florida`.
6. About page still says Vince is **Co-Owner & Field Operations Lead**, not sole owner, and does not claim he personally performs every job.
7. No Lutz GBP, no named unproven contractor, no dedicated `/lutz-handyman` until several completed jobs. Lutz / North Tampa may appear as an expanding route on `/service-areas`. “North Tampa” is prose only — not a Schema.org City.
8. No mass 301s or city-page consolidation. Preserve pricing satellites, FAQs, city URLs with impressions, niche service URLs, and the Home Watch cluster. Home Watch stays Pinellas-first.
9. Callers mentioning ChatGPT: note the landing URL they used (homepage vs `/pricing` vs `/home-watch-pinellas`) in the monthly log.

AI / search visibility while the site evolves:

- Keep explicit `$150 first hour / $75 after` and Home Watch plan prices.
- Do not dump `seoTarget` keywords into sentences.
- Hillsborough/Pasco pages must not claim Pinellas daily-route density.
- Keep Temple Terrace in the geographic graph if we accept jobs there.
- Re-auth GSC (`npm run auth` in `E:\Website Audit\GSC`) before relying on a 3–6 month query→URL map.

Do not add Windows Task Scheduler jobs for this monitor. Run it from this machine on the first business day.
