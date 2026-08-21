# Monthly Knight Group SEO monitor

Run on the first business day of each month from this machine:

```powershell
node "E:\Website Audit\GSC\tools\audit.mjs" --site knightgroup.com --api-only --skip-inspection
node "E:\Website Audit\GSC\tools\resubmit-sitemaps.mjs" --site knightgroup.com --ui
```

If the GSC API token is expired (`invalid_grant`), finish `npm run auth` in `E:\Website Audit\GSC` first.

Check:

1. Live `https://www.knightgroup.com/sitemap.xml` URL count vs GSC discovered pages.
2. Review count in `data/google-reviews.json` vs the Google profile (`npm run reviews:sync-google` in the website repo). That command also aligns GBP hours to Monday–Friday 8 AM–5 PM.
3. No new city×service pages added unless GSC shows a real query gap.
4. Homepage carousel still capped at 8 featured jobs.
5. Public electrical/plumbing/mold/roof/window claims still match `handyman-scope-florida`.
