#!/usr/bin/env python3
"""Copy the public vendor packet onto the Knight Group site.

Source of truth: E:\\Handyman Ticket Manager\\Vendor Info
Public dest:     website/vendor/

Never copies ACH, bank secrets, driver's licenses, wallet cards, or the full policy PDF.
"""

from __future__ import annotations

import zipfile
from datetime import date
from pathlib import Path

VENDOR_INFO = Path(r"E:\Handyman Ticket Manager\Vendor Info")
SITE_VENDOR = Path(__file__).resolve().parents[1] / "vendor"
TODAY = date.today().isoformat()

# (source filename in Vendor Info, public filename)
PUBLIC_DOCS: list[tuple[str, str, str]] = [
    ("IRS_Form_W-9_FILLED.pdf", "knight-group-w9.pdf", "IRS W-9 (LLC / partnership; EIN 33-2557284)"),
    (
        "Coterie Standard Certificate.pdf",
        "knight-group-gl-certificate.pdf",
        "ACORD 25 general liability ($1M / $2M; certificate holder is proof of coverage)",
    ),
    (
        "ExemptionCertificate.pdf",
        "knight-group-wc-exemption-nicholas-knight.pdf",
        "Florida WC officer exemption — Nicholas J. Knight (through 1/16/2027)",
    ),
    (
        "Vince_ExemptionCertificate.pdf",
        "knight-group-wc-exemption-vincent-knight.pdf",
        "Florida WC officer exemption — Vincent E. Knight (through 6/28/2028)",
    ),
    ("Sunbiz LLC Registration.pdf", "knight-group-sunbiz-llc.pdf", "Florida Sunbiz LLC annual report (L24000528363)"),
    ("KG_SERVICES_ONE_PAGER.pdf", "knight-group-services-one-pager.pdf", "Services one-pager for property managers"),
]

ZIP_NAME = "knight-group-vendor-packet.zip"

README = f"""Knight Group Handyman Services LLC — vendor packet
Updated {TODAY}

Legal name: Knight Group Handyman Services LLC
DBA: Knight Group
FEIN: 33-2557284
Sunbiz: L24000528363
Address: 1225 7th St S, Safety Harbor, FL 34695
Contact: Nicholas Knight · (813) 649-3341 · nknight@knightgroup.com

This zip is what most Pinellas property managers need to add us as a vendor.

Included
""" + "\n".join(
    f"  - {dest}: {label}" for _src, dest, label in PUBLIC_DOCS
) + """

Not included (on purpose)
  - ACH / bank account details — email nknight@knightgroup.com after you approve the vendor
  - Additional-insured COI in your legal name — email the exact certificate-holder wording
  - Company workers' compensation policy — not bound yet; officer exemptions are enclosed
  - Full Coterie policy package — available on request

https://www.knightgroup.com/property-manager-handyman
"""


def redact_personal_gmail(pdf_bytes: bytes) -> bytes:
    """Blank nickknight488@gmail.com on the public WC exemption copy. Leaves Vendor Info source intact."""
    import fitz

    needles = (
        "nickknight488@gmail.com",
        "NICKKNIGHT488@GMAIL.COM",
        "NickKnight488@gmail.com",
        "nickknight488",
        "NICKKNIGHT488",
    )
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        for page in doc:
            for needle in needles:
                for rect in page.search_for(needle):
                    padded = fitz.Rect(rect.x0 - 1, rect.y0 - 1, rect.x1 + 1, rect.y1 + 1)
                    page.add_redact_annot(padded, fill=(1, 1, 1))
            page.apply_redactions()
        out = doc.tobytes()
    finally:
        doc.close()
    return out


def copy_public_doc(src: Path, dest: Path, dest_name: str) -> None:
    data = src.read_bytes()
    if dest_name == "knight-group-wc-exemption-nicholas-knight.pdf":
        data = redact_personal_gmail(data)
        print(f"redacted gmail on {dest_name}")
    dest.write_bytes(data)


def main() -> int:
    SITE_VENDOR.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for src_name, dest_name, _label in PUBLIC_DOCS:
        src = VENDOR_INFO / src_name
        if not src.is_file():
            raise FileNotFoundError(f"Missing packet file: {src}")
        dest = SITE_VENDOR / dest_name
        copy_public_doc(src, dest, dest_name)
        copied.append(dest)
        print(f"copied {src_name} -> vendor/{dest_name} ({dest.stat().st_size} bytes)")

    readme = SITE_VENDOR / "README.txt"
    readme.write_text(README, encoding="utf-8")

    zip_path = SITE_VENDOR / ZIP_NAME
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.txt", README)
        for dest in copied:
            zf.write(dest, dest.name)
    print(f"wrote vendor/{ZIP_NAME} ({zip_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
