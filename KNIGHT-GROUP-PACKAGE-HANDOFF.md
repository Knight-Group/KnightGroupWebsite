# Knight Group Package Handoff

Generated from the Social Media Manager workspace on 2026-04-28 so the website-side work can be completed directly inside the AllProjects-Window2 workspace.

## Current GBP Product Set

- Standard Handyman Visit — $150 first hour
- Minor Plumbing Repair Visit — $150 first hour
- Specialty Install & Repair Visit — $200 first hour

These were intentionally kept aligned with the public pricing structure already on the Knight Group site.

## Recommended Website Placement

Primary file:

- pricing.html

Exact insertion target:

- Insert the visit-card section after the existing Payment Options card and before the closing div that appears immediately ahead of the Pricing Sidebar comment.
- In the current file, the best insertion point is just before the comment for Pricing Sidebar, after the Payment Options block that ends around lines 754 to 759.

Why this spot:

- It keeps the new visit cards close to the pricing explanation.
- It gives the user concrete entry options before the estimate form.
- It avoids fighting the page hero and keeps the section aligned with the rate logic already on the page.

## CTA Direction

- Primary CTA target: /contact
- Secondary CTA: tel:+18136493341
- Keep wording estimate-focused, homeowner-friendly, and plain.

## Package Copy Summary

### Standard Handyman Visit — $150 first hour

Best fit for general repair, punch-list, and everyday handyman work around the home.

Include:

- minor repairs and punch-list work
- drywall patching, caulking, and fixture swaps
- transparent pricing with no hidden service-call fees

### Minor Plumbing Repair Visit — $150 first hour

Plumbing-focused handyman visit for common household issues that need a fast, practical fix.

Include:

- faucets, showerheads, and fixture swaps
- running toilets, minor leaks, and shutoff-related fixes
- free written estimate and clear pricing

### Specialty Install & Repair Visit — $200 first hour

Higher-liability or heavier install work that needs more care, setup, or complexity handling.

Include:

- TV mounting and heavier installs
- ceiling fans, light fixtures, and appliance hookups
- large drywall or more complex repair work

## Ready-To-Paste Self-Contained HTML

This is the exact self-contained section generated for the site handoff. It can be pasted into pricing.html at the insertion point above.

```html
<section class="kg-package-section" id="popular-service-visits">
  <style>
    .kg-package-section {
      --kg-bg: #161213;
      --kg-card: rgba(255, 248, 244, 0.94);
      --kg-ink: #211819;
      --kg-muted: #5d4f50;
      --kg-accent: #8a3136;
      --kg-gold: #d6b57a;
      --kg-line: rgba(255, 255, 255, 0.12);
      padding: 76px 24px;
      background:
        radial-gradient(circle at 10% 12%, rgba(214, 181, 122, 0.16), transparent 16%),
        linear-gradient(135deg, #171214 0%, #29171a 100%);
      color: #fff7f1;
    }

    .kg-package-shell {
      max-width: 1180px;
      margin: 0 auto;
    }

    .kg-package-intro {
      max-width: 760px;
      margin-bottom: 30px;
    }

    .kg-package-eyebrow {
      margin: 0 0 12px;
      color: var(--kg-gold);
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.18em;
      text-transform: uppercase;
    }

    .kg-package-intro h2 {
      margin: 0 0 12px;
      font-size: clamp(2rem, 4vw, 3rem);
      line-height: 1.04;
    }

    .kg-package-intro p {
      margin: 0;
      color: rgba(255, 247, 241, 0.8);
      line-height: 1.7;
      font-size: 1.05rem;
    }

    .kg-package-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 22px;
    }

    .kg-package-card {
      display: grid;
      gap: 16px;
      padding: 28px;
      border: 1px solid var(--kg-line);
      border-radius: 28px;
      background: var(--kg-card);
      color: var(--kg-ink);
      box-shadow: 0 24px 44px rgba(0, 0, 0, 0.2);
    }

    .kg-package-card--featured {
      background: linear-gradient(180deg, rgba(255, 248, 244, 0.98), rgba(255, 244, 236, 0.92));
      border-color: rgba(214, 181, 122, 0.45);
    }

    .kg-package-tag {
      width: fit-content;
      padding: 7px 11px;
      border-radius: 999px;
      background: rgba(138, 49, 54, 0.12);
      color: var(--kg-accent);
      font-size: 0.76rem;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }

    .kg-package-head h3 {
      margin: 0 0 8px;
      font-size: 1.35rem;
      line-height: 1.2;
    }

    .kg-package-price {
      margin: 0;
      font-size: 2rem;
      font-weight: 800;
      line-height: 1;
    }

    .kg-package-subprice {
      margin: 6px 0 0;
      color: var(--kg-muted);
      font-size: 0.98rem;
      font-weight: 700;
    }

    .kg-package-desc {
      margin: 0;
      color: var(--kg-muted);
      line-height: 1.65;
    }

    .kg-package-points {
      margin: 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 10px;
    }

    .kg-package-points li {
      position: relative;
      padding-left: 18px;
      line-height: 1.5;
    }

    .kg-package-points li::before {
      content: "";
      position: absolute;
      left: 0;
      top: 0.6em;
      width: 7px;
      height: 7px;
      border-radius: 999px;
      background: var(--kg-accent);
    }

    .kg-package-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }

    .kg-package-cta,
    .kg-package-call {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 170px;
      padding: 12px 18px;
      border-radius: 999px;
      font-weight: 700;
      text-decoration: none;
    }

    .kg-package-cta {
      background: var(--kg-accent);
      color: #fff;
    }

    .kg-package-call {
      border: 1px solid rgba(33, 24, 25, 0.16);
      color: var(--kg-ink);
      background: rgba(255, 255, 255, 0.7);
    }

    .kg-package-note {
      margin-top: 18px;
      color: rgba(255, 247, 241, 0.82);
      font-size: 0.96rem;
    }

    @media (max-width: 700px) {
      .kg-package-section {
        padding: 68px 18px;
      }

      .kg-package-card {
        padding: 24px;
      }
    }
  </style>

  <div class="kg-package-shell">
    <div class="kg-package-intro">
      <p class="kg-package-eyebrow">Popular Service Visits</p>
      <h2>Simple starting points for the jobs homeowners usually need handled first.</h2>
      <p>These visit cards make the pricing page easier to act on. If the job is larger or needs a custom scope, the same estimate form still handles it.</p>
    </div>

    <div class="kg-package-grid">
      <article class="kg-package-card kg-package-card--featured">
        <div class="kg-package-tag">Most Common</div>
        <div class="kg-package-head">
          <h3>Standard Handyman Visit</h3>
          <p class="kg-package-price">$150 first hour</p>
          <p class="kg-package-subprice">$75 each additional hour</p>
        </div>
        <p class="kg-package-desc">Best fit for general repair, punch-list, and everyday handyman work around the home.</p>
        <ul class="kg-package-points">
          <li>Minor repairs and punch-list work</li>
          <li>Drywall patching, caulking, and fixture swaps</li>
          <li>Transparent pricing with no hidden service-call fees</li>
        </ul>
        <div class="kg-package-actions">
          <a class="kg-package-cta" href="/contact">Request Estimate</a>
          <a class="kg-package-call" href="tel:+18136493341">Call (813) 649-3341</a>
        </div>
      </article>

      <article class="kg-package-card">
        <div class="kg-package-tag">Plumbing-Led</div>
        <div class="kg-package-head">
          <h3>Minor Plumbing Repair Visit</h3>
          <p class="kg-package-price">$150 first hour</p>
          <p class="kg-package-subprice">$75 each additional hour</p>
        </div>
        <p class="kg-package-desc">Plumbing-focused handyman visit for common household issues that need a fast, practical fix.</p>
        <ul class="kg-package-points">
          <li>Faucets, showerheads, and fixture swaps</li>
          <li>Running toilets, minor leaks, and shutoff-related fixes</li>
          <li>Free written estimate and clear pricing</li>
        </ul>
        <div class="kg-package-actions">
          <a class="kg-package-cta" href="/contact">Book Plumbing Visit</a>
          <a class="kg-package-call" href="tel:+18136493341">Call (813) 649-3341</a>
        </div>
      </article>

      <article class="kg-package-card">
        <div class="kg-package-tag">Higher Complexity</div>
        <div class="kg-package-head">
          <h3>Specialty Install &amp; Repair Visit</h3>
          <p class="kg-package-price">$200 first hour</p>
          <p class="kg-package-subprice">$100 each additional hour</p>
        </div>
        <p class="kg-package-desc">Higher-liability or heavier install work that needs more care, setup, or complexity handling.</p>
        <ul class="kg-package-points">
          <li>TV mounting and heavier installs</li>
          <li>Ceiling fans, light fixtures, and appliance hookups</li>
          <li>Large drywall or more complex repair work</li>
        </ul>
        <div class="kg-package-actions">
          <a class="kg-package-cta" href="/contact">Request Specialty Visit</a>
          <a class="kg-package-call" href="tel:+18136493341">Call (813) 649-3341</a>
        </div>
      </article>
    </div>

    <p class="kg-package-note">Free written estimates. Materials and parts are separate from labor when needed. No hidden travel or service-call fees.</p>
  </div>
</section>
```

## Suggested Implementation Order

1. Paste the section into pricing.html at the insertion point above.
2. Verify spacing against the current pricing cards and sidebar.
3. Keep the pricing numbers aligned with this file and the existing pricing page language.
4. If needed later, adapt the same visit-card section into the homepage or services pages after the pricing page version is live.