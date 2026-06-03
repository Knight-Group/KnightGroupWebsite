# Knight Group — GBP & GSC automation setup

Reuse the same Google Cloud OAuth app as Knight Logics (`GSC-Analytics-Tracker` / `customeraccounts-a29eb`). Knight Group is a **separate** GBP location and **separate** Search Console property.

## What is already automated (Knight Logics)

| Tool | Path |
| --- | --- |
| GSC API weekly pull | `E:\KnightLogics-Growth-System\MainSite\scripts\gsc_api.py` |
| GBP review sync | `E:\KnightLogics-Growth-System\MainSite\scripts\sync-google-reviews.js` |
| Weekly bundle | `MainSite\scripts\seo_weekly_baseline.py` |

Knight Group now has its **own** review sync script in this repo. GSC pulls still run from Knight Logics MainSite with a property override (below).

---

## Step 1 — Add secrets to `accounts.env`

File: `C:\Users\nknig\.copilot-secrets\accounts.env`

Shared (same OAuth app as Knight Logics):

```
GBP_OAUTH_CLIENT_ID=...
GBP_OAUTH_CLIENT_SECRET=...
GBP_REFRESH_TOKEN=...
```

Knight Group selectors (get IDs from GBP dashboard or one-time discovery dry-run):

```
KNIGHTGROUP_GBP_ACCOUNT_NAME=accounts/XXXXXXXX
KNIGHTGROUP_GBP_LOCATION_NAME=locations/XXXXXXXX
KNIGHTGROUP_GBP_LOCATION_TITLE=Knight Group
```

Optional GSC override when running weekly Knight Group report:

```
# Used only when running knight-group-weekly-seo.ps1
KNIGHTGROUP_GSC_SITE_URL=https://www.knightgroup.com/
```

---

## Step 2 — Find GBP location IDs (one time)

From `E:\All Client Websites\KnightGroupWebsite`:

```powershell
npm run reviews:sync-google:dry-run
```

If discovery works, the error or log lists available `accounts/...` and `locations/...`. If you get **429 quota** on account discovery, set `KNIGHTGROUP_GBP_ACCOUNT_NAME` and `KNIGHTGROUP_GBP_LOCATION_NAME` manually:

1. Open [Google Business Profile](https://business.google.com/) → Knight Group location.
2. Or use the Knight Logics doc: `E:\KnightLogics-Growth-System\MainSite\docs\GOOGLE-REVIEWS-DYNAMIC-SYNC.md`

Then run:

```powershell
npm run reviews:sync-google
```

Output: `data/google-reviews.json`

---

## Step 3 — Weekly Knight Group SEO pull (GSC)

From PowerShell:

```powershell
& "E:\All Client Websites\KnightGroupWebsite\scripts\knight-group-weekly-seo.ps1"
```

Writes JSON under `E:\All Client Websites\KnightGroupWebsite\seo-audit\<date>\`.

Requires Knight Logics GSC auth once: `python E:\KnightLogics-Growth-System\MainSite\scripts\gsc_api.py auth` (same Google account that owns knightgroup.com in Search Console).

---

## Step 4 — Schedule (optional)

**Task Scheduler** — weekly Monday:

1. `knight-group-weekly-seo.ps1` (GSC queries + pages)
2. `npm run reviews:sync-google` in KnightGroupWebsite folder (GBP reviews)

---

## Weekly growth script (audit → report → next actions)

```powershell
cd E:\All Client Websites\KnightGroupWebsite
.\scripts\knight-group-weekly-growth.ps1
```

This runs:

1. GSC queries + pages export (`seo-audit/<date>/`)
2. GBP review sync → `data/google-reviews.json`
3. **Serper.dev** SERP snapshot via `seo/knight-group-serp-config.json` (same `SERPER_API_KEY` as Knight Logics OutreachEngine)
4. `WEEKLY-ACTION-REPORT.md` with top queries and a manual action checklist

Audits do **not** auto-edit GBP or page copy yet — the report tells you what to fix. Phase 2 can auto-deploy review JSON to the homepage.

## Serper.dev (competitor / SERP intelligence)

Knight Logics already uses Serper in `CRM/OutreachEngine` (`serp_intel.py`). Knight Group config:

- `seo/knight-group-serp-config.json` — handyman keywords for Pinellas / Clearwater / Safety Harbor

Requires `SERPER_API_KEY` in `E:\KnightLogics-Growth-System\CRM\OutreachEngine\.env`.

Use Serper to see **who ranks above you** for target terms (not to spam links). Compare titles and page types, then adjust Knight Group pages manually or via approved copy changes.

## Phase 2 (not built yet)

- Homepage review carousel reads `data/google-reviews.json` instead of static HTML.
- GBP **posts** API (create local update + link to `/booking`).
- Auto-deploy when review count changes; CTR regression alerts vs prior week.

Manual GBP posts and review asks still drive **calls** fastest until Phase 2 is live.

---

## MapQuest (free citation)

You may already have MapQuest links in Search Console. Verify NAP:

- [MapQuest listings](https://listings.mapquest.com/)
- Name: Knight Group Handyman Services LLC
- Address: 1225 7th St S, Safety Harbor, FL 34695
- Phone: (813) 649-3341
- Website: https://www.knightgroup.com/

Google Maps / GBP is separate and more important for calls; MapQuest is a supporting directory backlink.
