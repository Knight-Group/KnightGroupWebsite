# Knight Group SEO change log

Logged **2026-08-31** after Nick asked whether the “real leak” (CTR at positions 6–15, especially Clearwater) was already fixed, and whether we keep rewriting before Google recrawls.

**Decision: leave copy as-is.** Do not ship another title / meta / first-300-words pack until the freeze below lifts. **Allowed now:** GSC **Request indexing** on URLs whose `lastCrawlTime` is older than live `Last-Modified` — that can speed a recrawl; it does not change the site. CTR work can add customers only after one snippet is live **and** recrawled.

Canonical GSC control: `gsc-audit/2026-08-19/CONTROL-GROUP.md` (May 21–Aug 16: 119 clicks / 36,453 impressions / 0.33% CTR / position 21.1). Latest compare: `gsc-audit/2026-08-31/VS-CONTROL-GROUP.md`.

Live HTML ships from `E:\Handyman Ticket Manager\state\deploy\KnightGroupWebsite-production` only. Public rates stay **$150 / $75**, specialty **$200 / $100**.

---

## Freeze (in effect 2026-08-31 — lifted for one title test 2026-09-12)

Do **not** rewrite titles, meta descriptions, H1s, or first-300-word intros on money pages (city URLs, `/`, `/pricing`, `/Services/handyman`, `/Services/home-repair-near-me`) until **both**:

1. Google’s last crawl of `/clearwater-handyman`, `/tampa-handyman`, `/temple-terrace-handyman`, and `/pricing` is **after** the live `Last-Modified` of **Fri, 28 Aug 2026 17:48:40 GMT**, and
2. There are **7 complete GSC days** after that recrawl.

Next scheduled **measure** (not rewrite): first business day of September, per `docs/MONTHLY-SEO-MONITOR.md`. Run the API audit. If Clearwater’s `lastCrawlTime` is still 2026-08-22, request indexing (`submit-indexing.mjs --stale-crawl`), log “still waiting,” and stop. Do not write new titles.

```powershell
node E:\Website Audit\GSC\tools\submit-indexing.mjs --site knightgroup.com --stale-crawl
```

**Still allowed during freeze:** GSC **Request indexing** / `--stale-crawl` on URLs Google has not fetched since the Aug 28 host `Last-Modified` (this can speed recrawl; it is not a content change); factual error fixes; Home Watch (do not score vs Aug 19); related-card image deploys (on-page UX, not SERP CTR); Dispatch/ops. **Not allowed:** a new CTR title pack, city URL adds/merges, Lutz GBP, `"North Tampa"` as Schema.org City.

The `$150 First Hour` snippet is **live** as of host `Last-Modified` **Sun, 13 Sep 2026 01:50:01 GMT** on `/pricing`, `/clearwater-handyman`, `/largo-handyman`, and `/tarpon-springs-handyman`. Freeze again until Google recrawls those URLs after that timestamp **and** 7 complete GSC days exist. Do not write another title pack. Do not request GSC indexing until the next day.

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

---

## 2026-09-11 — `/property-manager-handyman` vendor packet (not a money-page snippet pack)

Rebuilt the existing URL `https://www.knightgroup.com/property-manager-handyman` (it was a generated stub: one repeated sentence and homeowner FAQs). This is **not** a new URL, **not** a new GBP, and **not** a second company’s page.

**Vendor is Knight Group Handyman Services LLC only.** FEIN 33-2557284, Sunbiz L24000528363, Safety Harbor remit address, W-9 / GL COI / officer WC exemptions. Honest that the LLC does **not** yet have a company WC policy. No Copeland/vendor-network rates. No subcontractor LLCs named or listed.

**Keywords:** GSC (Jun 2–Aug 28) already has `commercial handyman near me` (645 imp / 0 clicks / pos 26.5) and `property maintenance handyman` (1 click). Google Trends explore 429’d during research; the page uses those GSC terms plus PM vendor language (work order, AppFolio/Buildium invite, certificate of insurance) instead of homeowner “near me” stuffing. Title: `Property Manager Handyman | Vendor Packet | Pinellas`. ~1,000 unique body words. Internal links to rental turnover, Home Watch, Florida scope, pricing, Pinellas, general repairs.

**Freeze unchanged.** Did not rewrite city / homepage / pricing / `/Services/handyman` titles, H1s, or intros. Sitemap lastmod bumped **only** for `/property-manager-handyman` (and rental-turnover if that page gained a vendor-page pointer).

**Public packet download (same day):** `/vendor/knight-group-vendor-packet.zip` plus individual PDFs (filled W-9 with EIN, GL COI, both officer WC exemptions, Sunbiz, services one-pager). **Not** in the zip: ACH, additional-insured endorsements, company WC policy, driver’s licenses. Nick’s personal Gmail is redacted on the public exemption copy. Refresh with `scripts/sync-vendor-packet.py`.

**Related-card images (same day):** unique Knight Group job stills per destination; About card uses a face-heavy Vince crop. Not a SERP title pack.

**Shipped live:** 2026-09-11 via `origin/main`. Did **not** ship the uncommitted `$150 First Hour` money-page title pack.

---

## 2026-09-12 — Fixture / fan / basic plumbing scope (factual, not a title pack)

Nick flagged `/handyman-scope-florida` for saying licensed trades are required for ceiling fans, fixtures, outlets, switches, and plumbing that connects to drinking water. That came from an over-strict DBPR consumer-guidance rewrite, not from how Knight Group actually works in Pinellas.

**Correct public scope:** ceiling fans, light fixtures, switches, like-for-like outlets, and basic plumbing that does **not** need a permit (faucets, toilets, sinks, shutoffs, traps — not opening walls, not sewers). Still not a licensed plumber, electrician, or GC. New circuits, panel work, in-wall plumbing, sewers, gas, roofing, structural, HVAC remain referred.

**Hillsborough:** same fixture/fan work when no permit is required; copy now says Hillsborough permit rules can be tighter than Pinellas and we confirm on the estimate.

Did **not** rewrite city / homepage / pricing / `/Services/handyman` titles or the uncommitted `$150` pack. Electrical/plumbing **service** titles went from “Assessment” back to the work they actually sell.

**Shipped live:** 2026-09-12 via `origin/main`. Fixture/fan/basic plumbing copy only. Money-page titles stay geographic on live.


---

## 2026-09-12 — Expansion gallery geography (factual, not a title pack)

Misspelled ticket city **Carolwood** did **not** block posting. `KG-20260716-DFC8` already had a composite plus `/galleries` + `/gallery/ceiling-drywall-patch-2f1127e-before-after`. The city map treated the typo as unknown → copy/schema said Pinellas. Ticket city corrected to Carrollwood. Catalog, hub JSON-LD, and detail page now say **Carrollwood / Hillsborough**. Image alts use catalog city/county instead of hardcoded Pinellas. Hub crawl list now includes the expansion job pages. **No Lutz URL, no fake Tampa/Lutz jobs.** Freeze unchanged.

**Real expansion jobs with photos (all already had composites + both gallery surfaces):**

| Place | Ticket | Surfaces |
| --- | --- | --- |
| Carrollwood | KG-20260716-DFC8 | `/gallery/ceiling-drywall-patch-2f1127e-before-after` |
| Trinity | KG-20260731-26A9 | toilets, ballast light, wall outlet |
| Port Richey | KG-20260816-809A | fence reset |

Zero completed Lutz jobs. Zero completed Tampa jobs (one cancelled Copeland WO, no photos). Future Lutz/Tampa jobs will publish the same two surfaces from Dispatch; Lutz copy will not get a `/lutz-handyman` slug.

---

## 2026-09-12 — Astra plan (distribution, tracking, one title test)

Astra’s read of the 2026-09-12 pack: organic traffic cannot fill several workers; Home Watch/PM have almost no search exposure; Clearwater/Largo/pricing have impressions without clicks; ticket app must be the lead authority. Implemented in that order. **Did not scale paid ads.**

**Phase 1 — PM outreach.** Knight Group vendor first-touch and follow-up now land on `/property-manager-handyman?utm_source=outreach&utm_medium=email&utm_campaign=pm-vendor` plus the public packet zip. Home Watch emails use `utm_campaign=home-watch`. Next OutreachEngine KG send uses those URLs. No Saturday blast; no brand mix.

**Phase 2 — Lead tracking.** `generate_lead` still fires only on `/thank-you` (`form_success`), not on `form_submit`. Events include `form_type` (`homeowner` / `property_manager` / `home_watch`). `sms_click` is tracked. Localhost / Electron / `utm_source=internal|test` do not send GTM/gtag. Formspree → tickets now store `landing_page`, `form_type`, and UTM columns. **Nick:** in GA4 Admin → Events, mark `generate_lead`, `phone_click`, and `sms_click` as key events. Do not mark `form_submit`. Do not run `kg-live-gbp-ga4.py`.

**Phase 3 — Money pages (freeze wait for the Aug 28 HTML is over).** URL Inspection 2026-09-12: Clearwater last crawl **2026-08-31T13:53:02Z**, pricing **2026-08-31T13:53:01Z** — after live Last-Modified **2026-08-28 17:48 GMT**, and more than 7 complete GSC days have passed. Applied the **existing** `$150 First Hour` snippet only on `/pricing`, `/clearwater-handyman`, `/largo-handyman`, `/tarpon-springs-handyman` — not a fourth invented pack. Homepage, Tampa, Temple Terrace, and other city URLs were restored to HEAD geographic titles after a leftover mass `$150` pack was found in the working tree. Also added documented Dispatch jobs (below the intro), rate-card call/photo-estimate actions, and Clearwater drywall patch/texture/finish copy (Carrollwood ceiling patch is not claimed as Clearwater). **Not live until Nick deploys.** Live host `Last-Modified` is still **Sat, 12 Sep 2026 18:50:38 GMT**; live Clearwater/Largo/Tarpon titles remain geographic. Restart the snippet freeze from the next deploy’s `Last-Modified`.

**Phase 4 — Indexing (checked).** Requested indexing on 10 URLs, 0 errors: pricing, Clearwater, Largo, Tarpon Springs, Clearwater drywall, PM, three Home Watch pages, `/Services/handyman`. Output: `GSC/runs/2026-09-12/knightgroup.com/submit-indexing`. Sitemap API resubmit reported already-processed. Daily quota is used; do not submit another 10 today. After the `$150` source pack deploys, request indexing again the **next** day.

GSC Pages URL lists (Sep 3 snapshot) are now mapped in `GSC/runs/2026-09-12/knightgroup.com/indexing-map/`:

- **74 discovered-not-indexed:** 58 gallery, 13 service, 2 city satellites (`/largo-toilet-repair`, `/dunedin-trim-repair`), 1 `/services` hub.
- **8 crawled-not-indexed:** mostly gallery/`http://` junk/noindex policy. Keep PolicyPages excluded.
- High-importance money/PM/Home Watch URLs already appear in GSC performance. Do **not** demand 100% indexing of galleries.
- Next indexing day: the 13 service URLs plus the documented job galleries now linked from pricing/Clearwater/Largo/drywall.

**Phase 5 — Home Watch first route.** Did **not** redesign Home Watch or change `$329/$189/$125`. CSV of existing KG customers: `E:\Handyman Ticket Manager\state\marketing-exports\home-watch-first-route-2026-09-12.csv` (Keith/Tina Slater and Jeanette first). Saturday: Nick reviews and emails; no Google Voice.

**Phase 6 — Paid ads.** Not launched. Gate before any spend: (1) Nick marks `generate_lead`, `phone_click`, and `sms_click` as GA4 key events; (2) a few real tickets show `form_type` + UTM; (3) the ticket app, not `form_submit`, is the lead count. Organic search cannot carry a five-worker schedule.

**External mentions:** relationship list at `E:\Handyman Ticket Manager\state\marketing-exports\kg-partner-mentions-2026-09-12.csv`. Keith Slater / JK Slater first. No directory spam. No extra social-platform engineering.

**Astra alignment pass (same day, before commit).** PM vendor and realtor emails now ask about vacant-house / snowbird inquiries they don’t service, with tracked Home Watch URLs. Clearwater cites Kevin Poe’s Google review and the GBP. Largo/Tarpon “related” copy now has real internal links. `/Services/handyman` links the 13 discovered-not-indexed service URLs that belong on that hub. Ticket page shows website attribution; `scripts/export-lead-outcomes.py` maps those tickets to booked / completed / lost / collected. Temple Terrace was left on the geographic title (examine for profitable coverage; not this sprint’s title test).

**Clearwater query inspection (Astra §2, GSC query.csv through Sep 9).** Page `/clearwater-handyman` is the local-handyman destination: `handyman clearwater` 858 imp / 2 clicks / pos 20.7; `clearwater handyman` 48 / 0 / 14.9; `clearwater handyman services` 209 / 1 / 22.4. `clearwater drywall repair` 57 / 0 / 17.1 belongs on `/clearwater-drywall-repair` (724 page impressions), not the city page. Sitewide `handyman near me` is still 4,006 / 3 / pos 14.4 — visibility plus wording, not a new city-page batch. Temple Terrace query `handyman temple terrace fl` averaged pos 6.2 with five clicks; coverage stays geographic unless Nick confirms profitable Hillsborough routing. Paid ads remain off. GBP Maps/call metrics are still a data gap and not a blocker.

---

## 2026-09-12 evening — Astra live-site correction (shipping via origin/main)

Astra verified the **live** host: main features were present, but Home Watch intake, PM proof, and copy cleanup were still incomplete. Pricing was left alone. **Did not request indexing** (quota already used). **Did not change** money-page titles/metas/H1s except Tampa’s on-page hero lead (factual routing). **Did not change** Home Watch `$329/$189/$125`. **Did not launch ads.**

**1. Home Watch intake + sample report (first).** Pinellas form is now **6 customer-facing fields, 5 required** (name, phone, email, city, plan + optional notes). Dropped property type, sqft, away frequency, interior/pool/gate, start date. Rates sit in the hero and in a table under the first paragraph. New page `/home-watch-sample-report` is a labeled **SAMPLE** (fictional Safety Harbor vacant house, not a real owner file, not a licensed inspection). Generator: `scripts/build-home-watch-pages.py` — edit that or a rebuild overwrites the HTML.

**2. Property-manager proof + trial work order.** `/property-manager-handyman` now has `#sample-closeout` (real Largo gate photos, SAMPLE-WO-1847 label), two documented jobs (Largo gate, Clearwater rodent-hole), and `#first-paid-work-order` — one **paid** ticket at published `$150/$75`, not a free trial. No invented PM company names. No Copeland rates.

**3. Sitewide copy/title cleanup.** Homepage tags no longer say “Local trust layer,” “Geo and route coverage,” or “Google reviews and map proof.” Clearwater opening no longer says “already showing up for Clearwater searches.” Tampa hero/body/FAQ now lead with northwest Tampa / Westchase / Town 'n' Country / Carrollwood; Hyde Park is confirm-first; duplicate kitchen/bath bullet removed. Related-card `Doors &amp;amp;amp; windows` collapsed to `Doors &amp; windows` (52 files); `service_related.py` unescapes before escaping once so a future related-card pass does not re-stack ampersands. Gallery ticket names **Bedroom** and **Attic Drywall - Return Visit** are now customer problem/result titles on those two job pages, related-card labels, catalog, and gallery-manifest. **Did not mass-regenerate galleries** (no lastmod storm).

**4. Text Photos.** Header Call is `tel:`. A separate **Text Photos** control uses `sms:+18136493341` (customer texts *to* 813-649-3341). Mobile menu has the same. Home Watch and PM sidebars match. `sms_click` tracking was already in `includes.js`. Never send Voice SMS from here.

**Review count.** Left **12**. `data/google-reviews.json` last fetched **2026-08-21**. Did not invent a new GBP total. Did not run `kg-live-gbp-ga4.py`.

**Still not confirmed by this pass:** form delivery, GA4 key events, ticket-app UTMs, or Google recrawl. Low Home Watch / PM traffic still cannot be blamed on page design alone. **Shipped live** 2026-09-12 evening via `origin/main` `471e7a1`. Host `Last-Modified` is **Sun, 13 Sep 2026 01:50:01 GMT**. Sitemap lastmod was bumped only on Home Watch, the sample report, PM, homepage, Clearwater, Largo, Tarpon, Tampa, pricing, and the two renamed gallery pages — not a city/gallery lastmod storm. Restart the snippet freeze from that `Last-Modified`. Request indexing the **next** day on the four `$150` title-test URLs first; do not resubmit tonight.

---

## 2026-09-13 — Astra 48-hour intake/reporting (no title pack)

Astra re-inspected after the Sep 12/13 ship. Website improvements are real; these were remaining conversion/reporting defects. **Did not rewrite titles/metas/H1s.** **Did not mass-regenerate galleries.** **Did not launch ads.** **Did not request GSC indexing in this pass.**

**Live site (this commit):** `toRootSitePath()` now preserves `sms:` / `smsto:` (header Text Photos was resolving to `https://www.knightgroup.com/sms:...`). Injected `/sms:` hrefs are restored. PM vendor form photos are optional; “Send a first paid work order” jumps to `#vendor-intake`. Sitemap lastmod bumped only on `/property-manager-handyman`. JS cache-buster on HTML pages was **not** mass-updated (avoids a lastmod storm); `includes.min.js` content change is the SMS fix.

**Dispatch (localhost):** Formspree parser accepts Home Watch / PM inquiries from request type + valid phone with blank notes; parses `property_city`, `plan_interest`, and `company` instead of appending them onto email. `invoiced` is no longer reported as `collected`. Review-contingent invoice credit is **off** unless `KG_REVIEW_INCENTIVE=1`. Review asks skip genuine opt-outs, not sentiment-only “unhappy” notes.

**Outreach scorecard:** does not divide business-wide receipts by first-touch sends. `closed_won` still counts as a genuine reply. `revenue_attributed` stays 0 until lead → ticket → collected payment is wired.

**Gallery generator:** removed the 750-word pad and the “what homeowners search” section. Do not rebuild existing gallery HTML until a later packet.

**DataForSEO / Serper:** audit engine already prefers DataForSEO when credentials exist, else Serper, with a **$5/month** estimated cap (`SEO_ENGINE_MONTHLY_BUDGET_USD`). Buying credits does not raise that cap. Do not spend on a 100-firm PM batch until Nick raises the cap and confirms DataForSEO login is present.

---

## 2026-09-17 — GSC re-auth + measure + stale-crawl (no title pack)

`invalid_grant` auto-refreshed via `auth-via-profile.mjs` (saved Chrome profile). Audits now do that on token failure instead of stopping. GSC OAuth CDP uses port **9335** so it does not attach to Google Voice on **9333**.

Fresh API **Jun 19–Sep 14:** **180 clicks / 53,746 impressions / 0.33% CTR / position 20.3**. Last 7 complete days **8 clicks / 2,727 impressions**. Last 28 vs prior 28: **57 vs 78 clicks**. Homepage recrawled **2026-09-14T03:02:35Z** (after Sep 13 live HTML). 17 other inspected URLs still stale vs `Last-Modified` Sun, 13 Sep 2026 05:00:46 GMT.

Requested indexing on 10/10 stale money URLs, 0 errors: pricing, `/Services/handyman`, Clearwater, Largo, Tarpon Springs, Tampa, Temple Terrace, Land O' Lakes, service-areas, electrical. Daily quota used. **Did not rewrite titles.** Freeze holds until those recrawls plus 7 complete GSC days.

---

## 2026-09-21 — GBP review count 12 → 14 (no title pack)

Homepage `#kg-review-summary` was still showing **5.0 · 12 reviews** because `data/google-reviews.json` last fetched **2026-08-21** and no Task Scheduler job refreshed it. Live GBP pull today: **5.0 / 14 reviews** (`locations/15551195498878135337`). Shipped the JSON feed plus homepage/about fallbacks. Registered **KnightGroupGbpReviewSync** daily 8:15 AM (`scripts/sync-google-reviews.js --feed-only --skip-hours`, then git-push only `data/google-reviews.json`). **Did not rewrite titles.** **Did not PATCH GBP hours.** **Did not mass-replace `reviewCount` in HTML schema.**

---

## 2026-09-21 — Tampa coverage is a dispatched technician, not a local office (no title pack)

Homepage hero said Lutz / North Tampa was “an expanding handyman route with no local office,” which reads like Knight Group has offices elsewhere. It does not. Visible copy on `/`, `/service-areas`, `/tampa-handyman`, `/hillsborough-handyman`, and About now says jobs are dispatched to the technician covering that area and that there are no storefronts. **Did not name Sergey** (or any 1099) on the public site. **Did not rewrite titles or metas.** **Did not add `/lutz-handyman` or a Lutz GBP.** **Did not mass-regenerate galleries.** Generator strings in `gallery_longform.py` / `geo_city_data.py` / `geo_seo_copy.py` updated so a later rebuild does not put “no Lutz office” back.






