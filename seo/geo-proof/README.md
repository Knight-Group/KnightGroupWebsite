# Town job-proof blocks

One file per city or city-service page slug (for example tampa-handyman.html or tampa-drywall-repair.html). scripts/build-seo-pages.py generate_city() and generate_combo() insert the file between the generated detail section and the FAQ section on every build, so the Dispatch gallery publisher (which re-runs build-seo-pages.py) no longer wipes hand-written job proofs.

Rules: real completed jobs only, linked to their /gallery page; tech first names only; never client names, addresses, unit numbers, or job prices. Body content only; no title/meta/H1/canonical changes here.

Added 2026-11-16 by KG Web Growth after gallery commit c4851841 (Nov 5) regenerated /tampa-handyman and /clearwater-handyman and dropped their Oct 31 and Nov 2 job-proof blocks.

Also added 2026-11-16: pinellas-park-handyman.html and tampa-drywall-repair.html so those new pages stay intact on gallery publishes.
