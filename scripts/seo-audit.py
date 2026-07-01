#!/usr/bin/env python3
"""Run SEO quality audits and print a summary."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run_script(name: str) -> int:
    path = SCRIPTS / name
    result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
    out = (result.stdout or "") + (result.stderr or "")
    if out.strip():
        print(out.rstrip())
    return result.returncode


def title_issues() -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    skip = {"scripts", "legacy", "Chess-Game-main", "admin", "page-template.html"}
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in skip for part in path.parts):
            continue
        html = path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"<title>([^<]+)</title>", html, re.I)
        if not match:
            continue
        title = match.group(1).strip()
        if len(title) > 60:
            rows.append((str(path.relative_to(ROOT)), len(title), title))
    return rows


def manifest_issues() -> int:
    manifest_path = ROOT / "seo" / "page-manifest.json"
    if not manifest_path.is_file():
        return 0
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    issues = 0
    for page in manifest.get("pages", []):
        path = ROOT / page["path"]
        if not path.is_file():
            issues += 1
            print(f"missing page: {page['path']}")
            continue
        html = path.read_text(encoding="utf-8", errors="ignore")
        desc = re.search(r'<meta name="description" content="([^"]+)"', html)
        desc_len = len(desc.group(1)) if desc else 0
        if "og:title" not in html or desc_len < 120:
            issues += 1
            print(f"manifest issue: {page['path']} og={('og:title' in html)} desc={desc_len}")
    return issues


def main() -> int:
    failures = 0
    checks = [
        "audit_gallery_refs.py",
        "audit_image_refs.py",
        "audit-image-alt.py",
        "audit-meta-lengths.py",
    ]
    print("=== SEO audit suite ===")
    for script in checks:
        print(f"\n--- {script} ---")
        code = run_script(script)
        if code != 0:
            failures += 1

    print("\n--- title length (>60) ---")
    long_titles = title_issues()
    print(f"{len(long_titles)} titles over 60 chars")
    for rel, length, title in long_titles[:20]:
        print(f"  {length:3d} {rel}: {title[:70]}")
    if len(long_titles) > 20:
        print(f"  ... and {len(long_titles) - 20} more")

    print("\n--- manifest page meta/og ---")
    manifest_failures = manifest_issues()
    if manifest_failures:
        failures += 1

    if failures:
        print(f"\nAudit failed ({failures} check groups).")
        return 1
    print("\nAll SEO audits passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
