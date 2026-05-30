# Knight Group Audit Status

Last updated: 2026-05-30

## Completed in this round

- Removed the direct Messenger social link from the shared partials and all inlined page copies because it was the live external 302 target flagged by Ahrefs.
- Replaced remote email-provider favicon images with local inline provider badges across the public forms to stop redirected-image warnings.
- Simplified the homepage JSON-LD into a smaller valid graph to reduce schema noise in [index.html](E:/KnightGroupWebsite/index.html).
- Reworked structured data on [pricing.html](E:/KnightGroupWebsite/pricing.html) so the page no longer exposes the invalid standalone `Offer` pattern that triggered Google rich-results warnings.
- Removed the invalid `availability: "24/7"` field from the service schema on [Services/emergency-services.html](E:/KnightGroupWebsite/Services/emergency-services.html).
- Bumped the shared include cache version to `20260530-social-cleanup` after header/footer changes so live validation is not masked by cached partials.
- Verified the touched HTML and JS files show no editor errors after the changes.

## Verified issue mapping

- `External 3XX redirect`: repo-fixable. Root cause was `https://www.messenger.com/t/KnightGroupServices`.
- `Page has links to redirect`: repo-fixable. Same Messenger URL was present across 18 indexable pages.
- `Page in multiple sitemaps`: hosting-level. Ahrefs shows the same URLs referenced by both `http://www.knightgroup.com/sitemap.xml` and `https://www.knightgroup.com/sitemap.xml`.
- `Canonical from HTTP to HTTPS`: hosting-level. The live host currently returns `200` for both `http://www.knightgroup.com/` and `https://www.knightgroup.com/`.
- `Page has only one dofollow incoming internal link`: mostly a hosting artifact in current Ahrefs results because HTTP and HTTPS variants are being crawled separately.
- `Pages to submit to IndexNow`: operational follow-up after deployment of the current source changes.

## Homepage assessment

- `index.html` is large, but the size is mostly homepage-specific CSS/content plus some still-inlined shared UI.
- The file is not too large in a way that forces an immediate split, especially because the current high Lighthouse state depends on the existing critical font and hero CSS loading sequence.
- The best next structural cleanup is reducing duplicated shared markup and keeping non-critical shared UI in the include path, not breaking apart the critical hero/font path.

## Remaining follow-up

1. Enforce HTTPS at the host/domain level so `http://www.knightgroup.com/` and `http://www.knightgroup.com/sitemap.xml` no longer return `200`.
2. After deployment, rerun Ahrefs and submit the updated sitemap URLs to IndexNow.
3. If more cleanup is needed, continue consolidating repeated header/social/modal markup into the shared include flow without changing the known-good hero/font loading architecture.