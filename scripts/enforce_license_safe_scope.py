#!/usr/bin/env python3
"""Guard only self-licensing claims. Do not strip fixture or fan offers.

Owner policy (2026-09-12): Pinellas ceiling fans, light fixtures, switches,
like-for-like outlets, and basic no-permit plumbing are Knight Group work.
Never claim Knight Group is a licensed plumber, electrician, or GC.
Hillsborough permit rules can be tighter — confirm on the estimate.
"""

from __future__ import annotations

import runpy
from pathlib import Path


def main() -> int:
    print(
        "Fixture/fan/basic-plumbing offers stay. This guard only checks "
        "that public HTML does not say Knight Group is licensed & insured."
    )
    result = runpy.run_path(str(Path(__file__).with_name("verify-licensed-wording.py")))
    return int(result.get("main", lambda: 0)())


if __name__ == "__main__":
    raise SystemExit(main())
