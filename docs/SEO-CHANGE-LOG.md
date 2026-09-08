# Knight Group SEO change log

Logged **2026-08-31** after Nick asked whether the “real leak” (CTR at positions 6–15, especially Clearwater) was already fixed, and whether we keep rewriting before Google recrawls.

**Decision: leave copy as-is.** Do not ship another title / meta / first-300-words pack until the freeze below lifts. **Allowed now:** GSC **Request indexing** on URLs whose `lastCrawlTime` is older than live `Last-Modified` — that can speed a recrawl; it does not change the site. CTR work can add customers only after one snippet is live **and** recrawled.

Canonical GSC control: `gsc-audit/2026-08-19/CONTROL-GROUP.md` (May 21–Aug 16: 119 clicks / 36,453 impressions / 0.33% CTR / position 21.1). Latest compare: `gsc-audit/2026-08-31/VS-CONTROL-GROUP.md`.

Live HTML ships from `E:\Handyman Ticket Manager\state\deploy\KnightGroupWebsite-production` only. Public rates stay **$150 / $75**, specialty **$200 / $100**.

---

## Freeze (in effect 2026-08-31)

Do **not** rewrite titles, meta descriptions, H1s, or first-300-word intros on money pages (city URLs, `/`, `/pricing`, `/Services/handyman`, `/Services/home-repair-near-me`) until **both**:

1. Google’s last crawl of `/clearwater-handyman`, `/tampa-handyman`, `/temple-terrace-handyman`, and `/pricing` is **after** the live `Last-Modified` of **Fri, 28 Aug 2026 17:48:40 GMT**, and
2. There are **7 complete GSC days** after that recrawl.

Next scheduled **measure** (not rewrite): first business day of September, per `docs/MONTHLY-SEO-MONITOR.md`. Run the API audit. If Clearwater’s `lastCrawlTime` is still 2026-08-22, request indexing (`submit-indexing.mjs --stale-crawl`), log “still waiting,” and stop. Do not write new titles.

```powershell
node E:\Website Audit\GSC\tools\submit-indexing.mjs --site knightgroup.com --stale-crawl
```

**Still allowed during freeze:** GSC **Request indexing** / `--stale-crawl` on URLs Google has not fetched since the Aug 28 host `Last-Modified` (this can speed recrawl; it is not a content change); factual error fixes; Home Watch (do not score vs Aug 19); related-card image deploys (on-page UX, not SERP CTR); Dispatch/ops. **Not allowed:** a new CTR title pack, city URL adds/merges, Lutz GBP, `"North Tampa"` as Schema.org City.

Uncommitted working-tree titles (`Clearwater Handyman | $150 First Hour`, etc.) are the **already-written** next snippet. Do not invent a fourth version. Deploy that pack only if Nick says so, then restart this freeze from that deploy’s `Last-Modified`.

---

## What Google is actually seeing (2026-08-31)

Live public titles match **git HEAD** (`origin/main`), last hosted **2026-08-28 17:48 GMT**. They do **not** match the dirty working tree.

| URL | Live title (what the host serves) | Google last crawl (URL Inspection 2026-08-31) |
| --- | --- | --- |
| `/clearwater-handyman` | Clearwater Handyman \| Pinellas County \| Knight Group | **2026-08-22T19:12:16Z** — before Aug 23/25/28 ships |
| `/tampa-handyman` | Tampa Handyman \| Hillsborough County \| Knight Group | **2026-08-22T19:12:16Z** |
| `/temple-terrace-handyman` | Temple Terrace Handyman \| Hillsborough County \| Knight Group | **2026-08-22T19:16:31Z** |
| `/pricing` | Handyman Pricing \| $150 First Hour · $75 After \| Pinellas FL | **2026-08-22T19:13:17Z** |
| `/` | Pinellas Handyman \| No 2-Hour Minimum \| Knight Group | 2026-08-29T18:12:27Z (after Aug 28 host) |
| `/Services/handyman` | Handyman Pinellas County FL \| Knight Group | 2026-08-30T02:47:47Z (after Aug 28 host) |

Clearwater GSC (Jun 2–Aug 28 vs control): still **1 click / 3,962 impressions / ~0.03% CTR / position ~17**. That window mostly predates a recrawl of the current live HTML. Do not treat that as a failed experiment.

---

## Changes already made (do not redo)

| When | What | Shipped live? | Notes |
| --- | --- | --- | --- |
| 2026-07-08 | `0d477ed` GSC growth plan, metadata, crawl fixes | Yes (historical) | First systematic SEO pass |
| 2026-07-29 | `33d8089` “Fix CTR-killing metas…” (`scripts/fix-ctr-metas-20260729.py`) | Yes | Clearwater title then: `Clearwater Handyman Near You \| Free Estimate \| Knight Group` |
| 2026-08-19 | GSC **control group** (May 21–Aug 16) | Measure only | 119 / 36,453 / 0.33% / 21.1. Do not score Home Watch vs this. |
| 2026-08-21 | `d0770e4` gallery before/after | Yes | Not a SERP title change |
| 2026-08-22 | `ed64f81` Clearwater snippet + Temple Terrace graph; `ece3740` About/geography. Deploy + sitemap resubmit + indexing requests (`E:\Website Audit\GSC\runs\2026-08-22`) | Yes | Control file says titles/metas/OG/Home Watch/North Tampa signals ship on/after this date. **This is the crawl Google still has for Clearwater.** |
| 2026-08-23 | `fe0de43` “tighter money-page titles” | Briefly in git | Clearwater became `Clearwater Handyman \| $150 First Hour · $75 After`. Remediation doc said re-run GSC 7–14 days later. **Google never recrawled Clearwater after this.** |
| 2026-08-25 | `8f4bead` homepage photos, sticky booking, curated service photos | Yes (overwrote Aug 23 titles) | Clearwater title changed **away** from `$150` to `Pinellas County \| Knight Group`. CTR regression bundled into a photo ship. |
| 2026-08-26 | `[ctr-pack-20260826]` in `seo/meta-descriptions.json`; `scripts/apply-gsc-ctr-titles.py` | **No** | Script is untracked (`??`). Source-only. |
| 2026-08-28 | `2ca1047` gallery longform | Yes | Host `Last-Modified` Fri Aug 28 17:48 GMT. Titles still the Aug 25 geographic set. |
| 2026-08-29 | This chat: titles/metas/intros/links/schema CTR pack + related-card after-stills | **No** | Working tree dirty. Source Clearwater: `Clearwater Handyman \| $150 First Hour` + Island Estates / Countryside / Coachman meta. Related stills are on-page UX, not SERP CTR. |
| 2026-08-31 | Full GSC audit vs control | Measure only | Clicks +36, impressions +8,938, CTR +0.01 pp. Leak unchanged on Clearwater / `handyman near me`. Homepage recrawled Aug 29; handyman hub Aug 30. |
| 2026-08-31 | Recrawl-before-rewrite baked into Website Audit + GSC `--stale-crawl`. **Request indexing** on 10 URLs whose crawl was older than live Last-Modified (pricing, Clearwater, Tampa, Temple Terrace, service-areas, electrical, plumbing, three Home Watch pages). 10/10 requested, 0 errors. Snowbird + About were stale too but over the 10/day cap. | GSC only — **no site copy change** | `GSC/runs/2026-08-31/knightgroup.com/submit-indexing`. This can speed Google fetching the Aug 28 HTML. It does not guarantee a crawl date. |
| 2026-09-01 | Microsoft Clarity (`wgzcqjrxjd`) wired into `JS/kg-analytics.js` on production host only; city pages boot it from `canonical-redirect.js`. Ahrefs 99 left alone (IndexNow / title-changed notices are not a rewrite trigger). | JS in production deploy; **no title/meta/H1 pack** | Do not treat Ahrefs “148 IndexNow” or “title changed” as errors. |

Clearwater title history in git (same URL, four snippets in ~5 weeks):

1. Jul 29: `…Near You | Free Estimate | Knight Group`
2. Aug 22: snippet matched to impressions (geographic / Pinellas era leading into Aug 23)
3. Aug 23: `$150 First Hour · $75 After`
4. Aug 25–live: `Pinellas County | Knight Group`
5. Uncommitted Aug 29: `$150 First Hour` (not live)

---

## Will more CTR work increase customers?

**Yes, for this leak and similar ones** — city and “near me” queries already at positions **6–15** with almost no clicks (Clearwater 3,962 impressions / 1 click; `handyman near me` 3,735 / 3 clicks). Those people already see a Knight Group result. A better snippet (price, no 2-hour minimum, local proof) is how they become callers. That is the same play for Largo, home-repair-near-me, and other 6–15 clusters. It is **not** a reason to add city URLs or merge pages.

**No, not from another rewrite this week.** Google’s Clearwater snippet is still the **Aug 22** crawl. Rewriting source again does not change what searchers see. The Aug 23 `$150` title never got a recrawl test because Aug 25 replaced it before Google came back.

Do **not** expect CTR work to move queries at position 20+ into customers the same way. Those need rank, not only snippet.

---

## Lift the freeze when

- URL Inspection: Clearwater / Tampa / Temple Terrace / pricing `lastCrawlTime` > 2026-08-28T17:48:40Z, **and**
- 7 complete GSC days after that, then compare those URLs and the query clusters in `CONTROL-GROUP.md` (not Home Watch).

If CTR is still ~0.03% on Clearwater **after** that window, then it is fair to ship the **existing** uncommitted `$150` pack (or confirm live already has it) — not to invent new copy.

---

## 2026-09-08 — `/join` 1099 application (ops, not a snippet pack)

Shipped a quiet **independent contractor application** at `/join`. Collects contact, W-9, GL COI, and workers’ comp or Florida exemption. Linked from **footer + About only** — not homepage, not city/money pages, not the main nav. Title/meta say 1099/apply, not “handyman near me.” Sitemap priority **0.40**. Public retail stays **$150/$75**, specialty **$200/$100**. No Vince 75/25 or 1099 2/3 splits published. `/join` body (not title/meta) states typical **contractor pay** on general jobs: **$75 first hour / $50 each hour after per job**, variable on other scopes — labeled as contractor pay, not homeowner pricing.

GSC last-3-months looking weaker on average position is consistent with **niche expansion** (Home Watch, North Tampa signals, more query mix) plus crawls that still predate live HTML on several money URLs. **Do not** treat that chart as a reason to rewrite titles. Freeze above still holds.

**Gallery pipeline (same day, not a content pack):** auto job pages already get 750+ word unique copy, canonical, OG, JSON-LD (WebPage / ImageObject / HowTo / FAQ), and sitemap inclusion. “Scope & Routing” is the existing service hub (e.g. `/Services/plumbing-services`), not a second URL per image. “View Job Details” is `/gallery/{id}`. `clip_title` no longer chops the brand to `Knight G...`. `publish-before-after-gallery.py` now runs `build-seo-pages.py --gallery-only` so adding a composite does **not** rewrite city/money HTML. Existing gallery HTML was **not** mass-regenerated (avoids a lastmod storm during the freeze).

