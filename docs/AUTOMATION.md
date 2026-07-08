# Knight Group — automation (operations)

**Canonical website:** `E:\All Client Websites\KnightGroupWebsite`  
**Do not use:** `E:\KnightGroupWebsite_STALE_DO_NOT_USE`

This doc is the single source of truth for automated review emails, gallery composites, and social posting. For field photo workflow details see `E:\Handyman Ticket Manager\docs\GALLERY-MARKETING-PIPELINE.md`.

---

## Re-register all scheduled tasks

Run once after path changes or on a new PC:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "E:\Handyman Ticket Manager\deploy\install-kg-automation-tasks.ps1"
```

---

## Scheduled tasks (Windows)

| Task | Schedule | What it does |
|------|----------|----------------|
| `KnightGroupReviewFollowUp` | Every 60 min | Review emails from `nknight@knightgroup.com` |
| `KnightGroupMarketingWorker` | Every 20 min | Before/after composites → gallery → social queue |
| `KnightGroupScheduledSocialPublish` | Tue / Thu / Sat 10:30 AM | Publishes ready gallery posts to all platforms |
| `KnightGroupDispatchWatchdog` | Every 15 min | Restarts dispatch if port 5201 is down |

Dispatch also starts at logon via `KnightGroupDispatchAndTunnel` (`install-all.ps1`).

---

## 1. Review follow-up emails

**Code:** `E:\KnightLogics-Growth-System\CRM\KnightGroupReviewFollowUp\`

| Step | Detail |
|------|--------|
| Source | Completed jobs in `E:\Handyman Ticket Manager\state\tickets.db` |
| Sends | Initial ask + one 14-day follow-up per email (max) |
| Skips | No email, test tickets, agitation keywords in notes, `pending_review` jobs, customers who already left a GBP review (name match), inbox replies saying they reviewed |
| Log | `state\review_sends.db` |

**Manual check (dry-run):**

```powershell
cd "E:\KnightLogics-Growth-System\CRM\KnightGroupReviewFollowUp"
python send_review_batch.py --dry-run --include-followups --skip-sync
```

**Re-install task only:**

```powershell
.\install-review-task.ps1
```

Policy and templates: [REVIEW-FOLLOW-UP.md](REVIEW-FOLLOW-UP.md)

---

## 2. Gallery / before-after pipeline

**Flow:**

```text
Dispatch upload (before / process / after)
  → marketing export + job queue (on ticket complete / photo change)
  → KnightGroupMarketingWorker (2h delay after completion by default)
  → build-before-after-composite.py (this repo)
  → publish-before-after-gallery.py → GalleryImages/
  → populate_kg_gallery.py → media_library/kg + queues
```

**Env overrides** (Handyman `.env`):

```
KG_WEBSITE_ROOT=E:\All Client Websites\KnightGroupWebsite
KG_SMM_ROOT=E:\KnightLogics-Growth-System\Social\Social-Media-Manager
KG_MARKETING_DELAY_MINUTES=120
```

**Manual worker run:**

```powershell
cd "E:\Handyman Ticket Manager"
.\.venv\Scripts\python scripts\run-marketing-worker.py --fan-out --social-status ready --limit 5
```

**Job queue:** `marketing_scope_jobs` in `state\tickets.db` — statuses `pending` / `ready` / `done` / `skipped`.

---

## 3. Social publishing (gallery posts)

**Code:** `E:\KnightLogics-Growth-System\Social\Social-Media-Manager\scheduled_brand_posting\`

| Rule | Value |
|------|-------|
| Cadence | Up to 3 gallery posts per week |
| Schedule | Tue / Thu / Sat 10:30 AM |
| Min gap | 2 days between publishes |
| Platforms | GBP, X, LinkedIn, Nextdoor, Facebook (via `publish_brand_all.py`) |
| Queue | `queues/kg/media_posts.json` (status `ready`) |

**Dry-run next post:**

```powershell
cd "E:\KnightLogics-Growth-System\Social\Social-Media-Manager"
poster\.venv\Scripts\python.exe scheduled_brand_posting\run_scheduled_publish.py --brand kg
```

**Live publish one post now:**

```powershell
poster\.venv\Scripts\python.exe scheduled_brand_posting\run_scheduled_publish.py --brand kg --live
```

Log: `scheduled_brand_posting/logs/publish_execution.jsonl`

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Task fails with `2147942402` (file not found) | Re-run `install-kg-automation-tasks.ps1` — old tasks used broken paths with spaces |
| Composites use wrong layout | Ensure `KG_WEBSITE_ROOT` points here, not `_STALE_DO_NOT_USE` |
| `KG_WEBSITE_ROOT points at a stale checkout` | Fix `.env` in Handyman Ticket Manager — automation refuses `_STALE_DO_NOT_USE` |
| Marketing jobs stay `pending` | Scope needs at least one **before** and one **after** photo per scope |
| Review email to unhappy customer | Add keywords to ticket notes (`upset`, `complaint`, `skip review`) — see `review_templates.py` |
| Social post not publishing | Check `media_posts.json` for `ready` rows; verify `publish_execution.jsonl` for errors |

---

## Related docs

| Doc | Location |
|-----|----------|
| Gallery pipeline (detailed) | `E:\Handyman Ticket Manager\docs\GALLERY-MARKETING-PIPELINE.md` |
| Dispatch field app | `E:\Handyman Ticket Manager\deploy\README.md` |
| Social posting strategy | `E:\KnightLogics-Growth-System\Social\Social-Media-Manager\docs\scheduled-brand-posting-strategy.md` |
| GSC audits | [AGENTS.md](../AGENTS.md) |
| Archived manual review strategy | [archive/REVIEW-FOLLOW-UP-STRATEGY-manual-2026-03.md](archive/REVIEW-FOLLOW-UP-STRATEGY-manual-2026-03.md) |
