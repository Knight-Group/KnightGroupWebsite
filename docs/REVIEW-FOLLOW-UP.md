# Google review follow-up — Knight Group

**Status:** Automated (2026-07-08). See [AUTOMATION.md](AUTOMATION.md) for tasks and commands.

---

## What runs automatically

- **Initial email** after a completed, approved job (one per customer email)
- **One follow-up** 14 days later if no review detected
- **GBP sync** before each batch — skips customers who already reviewed (name match) or replied saying they reviewed
- **Safety gates** — skips tickets with agitation/complaint keywords in notes, jobs awaiting admin review, test tickets, missing email

Emails send from `nknight@knightgroup.com` via Microsoft Graph (`KnightGroupReviewFollowUp` scheduled task, hourly).

---

## Principles (unchanged)

1. Ask only after a clearly successful job.
2. One polite ask, one reminder max.
3. Direct Google review link in every email.
4. Never offer payment or discounts for reviews.
5. If something went wrong, fix it privately — do not send unhappy customers to Google.

---

## Manual override

| Action | How |
|--------|-----|
| Block a customer | Add `skip review` or `do not contact` to ticket completion/access notes |
| Preview queue | `python send_review_batch.py --dry-run --include-followups --skip-sync` |
| Send now (limit 1) | `python send_review_batch.py --limit 1 --include-followups` |

---

## Archived

The pre-automation manual spreadsheet/SMS strategy is preserved in [archive/REVIEW-FOLLOW-UP-STRATEGY-manual-2026-03.md](archive/REVIEW-FOLLOW-UP-STRATEGY-manual-2026-03.md) for reference only.
