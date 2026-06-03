# Knight Group Growth Playbook — June 3, 2026

Data sources: GSC export (last 28 days), keyword CSV, backlink comparison, live site audit.

## GSC reality check (last 28 days)

| Metric | Value |
| --- | --- |
| Total clicks | **5** (all homepage) |
| Top impressions | Homepage 338, About 68, Handyman 31, Plumbing 26, Contact 22 |
| Service pages with impressions | **0 clicks** on every service URL |
| Brand query `knight group` | 24 impressions, position ~8.4, **0 clicks** |
| Local intent | `handyman company pinellas`, `handyman pinellas county`, `sink repair clearwater` — all **0 clicks** |

**Diagnosis:** Google is starting to show you for local terms, but titles/snippets and authority are not converting. Growth = fix CTR on pages that already impress + build local links + GBP calls — not 50 new thin pages.

---

## What Cursor can vs cannot do for GSC

| Capability | Status |
| --- | --- |
| Read GSC **exports** you drop in the repo | Yes (done) |
| Live Google Search Console API in this chat | **No** — not connected here |
| KnightLogics Growth System (`E:\KnightLogics-Growth-System`) | Automation for citations/GBP; **no GSC API found** in a quick scan |
| On-site SEO (titles, pages, schema, sitemap) | Yes — implemented June 3, 2026 |

To enable recurring GSC pulls: use [Google Search Console API](https://developers.google.com/webmaster-tools) with a service account in KnightLogics, or export CSV monthly into this folder.

---

## On-site changes completed (June 3, 2026)

1. **Homepage** — Brand-first title: `Knight Group | Handyman Pinellas County & Safety Harbor FL`
2. **Handyman** — Pinellas-focused title, H1, FAQ schema for “handyman company Pinellas”
3. **Plumbing** — Clearwater / sink repair in title and meta
4. **Service areas** — Pinellas hub copy + links to new geo pages
5. **About** — Brand + “handyman company” title alignment
6. **New pages:** `/clearwater-handyman`, `/pinellas-handyman` (substantive, FAQ schema, sitemap)
7. **Legacy URL** — `canonical-redirect.js` now sends `/Services/programming&databases` to Knight Logics (was only on 404)
8. **Sitemap** — 20 URLs (added 2 geo pages)
9. **Priority map:** `gsc-priority-queries-2026-06-03.csv`

**You must deploy** (git push to production) for Google to see these changes, then request indexing in GSC.

---

## Your 90-day agency-style execution plan

### Phase 1 — Deploy & index (Week 1)

- [ ] Push site changes to `origin/main` / live host
- [ ] GSC → URL inspection → Request indexing for:
  - `/`
  - `/Services/handyman`
  - `/Services/plumbing-services`
  - `/clearwater-handyman`
  - `/pinellas-handyman`
  - `/service-areas`
- [ ] Resubmit `sitemap.xml` in GSC and Bing Webmaster
- [ ] IndexNow ping (if host supports) for the 6 URLs above
- [ ] Fix hosting: **force HTTPS** and single sitemap (see `KNIGHT-GROUP-AUDIT-STATUS.md`)

### Phase 2 — Google Business Profile (Weeks 1–2) — highest ROI for **calls**

- [ ] Primary category: **Handyman** (not General Contractor)
- [ ] Services list matches site: repairs, plumbing fixtures, drywall, paint, carpentry
- [ ] Website URL: `https://www.knightgroup.com/`
- [ ] Appointment link: `https://www.knightgroup.com/booking`
- [ ] 2× weekly posts → rotate links: `booking`, `handyman`, `clearwater-handyman`, gallery photo
- [ ] Ask every happy customer for a Google review (text link from phone)
- [ ] Add 10+ project photos with geo tags (Safety Harbor / Clearwater)

**KPI:** GBP calls + direction requests (track in GBP insights weekly)

### Phase 3 — Citations & dofollow links (Weeks 2–6)

Prioritize **quality + NAP match** over volume.

| Tier | Target | Link to |
| --- | --- | --- |
| 1 | Google Business Profile | Homepage + booking |
| 1 | Bing Places, Apple Business Connect | Homepage |
| 1 | MapQuest (already links — verify NAP) | Homepage |
| 1 | Safety Harbor Chamber of Commerce | Homepage + booking |
| 2 | Central Pinellas Chamber, Tarpon Springs Chamber | `/pinellas-handyman` or `/service-areas` |
| 2 | Yelp, BBB, Houzz, Porch, Angi | `/Services/handyman` or booking |
| 3 | Realtor / PM partners (3–5 relationships) | `/Services/painting-finishing`, `/Services/general-repairs` |

**Anchor text:** vary naturally — “Knight Group”, “handyman in Clearwater”, “request an estimate”, not 20× exact “handyman pinellas county”.

**Do not:** Fiverr bulk directories, irrelevant national lists, or buying links.

### Phase 4 — Partner outreach (Weeks 3–8)

Copy starters are in `KNIGHT-GROUP-AUTHORITY-PLAN.md`.

- [ ] 5 Realtors (pre-listing punch list → painting + general repairs)
- [ ] 3 property managers (handyman + emergency pages)
- [ ] 2 restoration/water-damage companies (post-mitigation drywall/plumbing)
- [ ] 1 local hardware or showroom (doors/windows page)

**Goal:** 5–10 **real** referring domains in 90 days (competitor benchmark ~58; Ace is franchise outlier).

### Phase 5 — Keyword research (ongoing)

**Ignore** national noise in `KeywordStats_6_3_2026.csv` (Ace Hardware, TaskRabbit, UK cities, DIY).

**Use instead:**

1. GSC Queries export monthly (Pinellas-only filter in mind)
2. Google Keyword Planner — location **Tampa–St. Petersburg**, terms:
   - handyman clearwater fl
   - handyman safety harbor
   - drywall repair pinellas county
   - sink repair clearwater
3. GBP “Search queries” (when volume appears)
4. Competitor page titles (The Handyman Company, local independents) — not Ace franchise

### Phase 6 — Content (only after indexing improves)

- [ ] Wait until core service URLs get **clicks** or stable impressions with position &lt; 15
- [ ] Then add **one** more city page if GSC shows demand (e.g. Dunedin) — same quality bar as Clearwater page
- [ ] Optional intent page: “pre-listing repairs” or “punch list handyman” if queries appear

---

## Weekly scorecard (you fill in)

| Week | GSC clicks | GSC impressions | Avg position (top 5 queries) | GBP calls | New reviews | New referring domains |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | |
| 2 | | | | | | |

---

## Keyword file → page map (national CSV, Pinellas-relevant only)

| Keyword theme | Knight page |
| --- | --- |
| handyman near me / services near me | `/Services/handyman`, GBP |
| local handyman / in my area | `/pinellas-handyman` |
| home repair / home repair services | `/Services/general-repairs` |
| deck repair handyman near me | `/Services/general-repairs` + gallery |
| licensed / reliable / best handyman near me | `/about`, reviews on homepage |
| bathroom remodel handyman | `/Services/home-renovations` |
| electrical handyman near me | `/Services/electrical-work` (scope carefully) |

---

## What NOT to do

- Chase `general contractors pinellas county` (wrong business type; position 61)
- Publish 10 duplicate city pages before service pages earn clicks
- Point every backlink to homepage only
- Mix Knight Logics (tech) positioning into Knight Group listings
- Pay for spam directories to match Ace Handyman’s 3K domains

---

## Next export to add

Drop in this folder for the next optimization pass:

- GSC → Performance → **Queries** + **Pages** (last 3 months)
- GSC → Links → External links (top linking sites)
- GBP insights screenshot or CSV (calls, views)

When those are present, re-run prioritization against live positions and CTR.
