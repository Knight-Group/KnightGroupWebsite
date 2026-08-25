#!/usr/bin/env python3
"""Read-only unmatched books report for Handyman Ticket Manager / Dispatch.

Lists, for a tax year:
  * payout_transfers with a blank ticket_number, classified split vs kept
  * unmatched stripe_deposit_lines
  * paid job_books whose payment_channel is unrecorded

Opens tickets.db as SQLite read-only. Never writes to the database, never
applies payouts, and never invents ticket matches (including Vince's Zelle
payouts, which already count in paid_to_worker).

When tickets.db is present, JSON is written under state/books/.
When it is missing, the script still exists and exits with the paths it tried.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
WINDOWS_DB = Path(r"E:\Handyman Ticket Manager\state\tickets.db")

REQUIRED_TABLES = ("payout_transfers", "stripe_deposit_lines", "job_books")

TICKET_NUMBER_CANDIDATES = (
    "ticket_number",
    "ticket_no",
    "ticket",
    "job_ticket",
)
DATE_CANDIDATES = (
    "tax_year",
    "paid_at",
    "transferred_at",
    "transfer_date",
    "payout_date",
    "deposit_date",
    "arrived_at",
    "line_date",
    "booked_at",
    "job_date",
    "completed_at",
    "paid_on",
    "created_at",
    "updated_at",
)
KIND_CANDIDATES = (
    "split_kept",
    "split_or_kept",
    "kind",
    "transfer_kind",
    "payout_kind",
    "bucket",
    "category",
    "type",
    "transfer_type",
    "role",
    "destination",
    "disposition",
)
SPLIT_AMOUNT_CANDIDATES = (
    "pay_them",
    "pay_them_amount",
    "worker_amount",
    "split_amount",
    "paid_to_worker",
    "worker_payout",
    "1099_amount",
)
KEEP_AMOUNT_CANDIDATES = (
    "you_keep",
    "keep_amount",
    "company_amount",
    "house_amount",
    "retained_amount",
    "kept",
)
MATCH_STATUS_CANDIDATES = (
    "match_status",
    "reconcile_status",
    "reconciliation_status",
    "link_status",
)
MATCHED_FLAG_CANDIDATES = ("matched", "is_matched", "reconciled", "linked")
UNMATCHED_FLAG_CANDIDATES = ("unmatched", "is_unmatched")
JOB_LINK_CANDIDATES = (
    "ticket_number",
    "ticket_id",
    "job_book_id",
    "job_id",
    "books_id",
    "matched_ticket",
    "matched_ticket_number",
    "linked_ticket",
    "assigned_ticket",
)
PAID_STATUS_CANDIDATES = ("status", "payment_status", "book_status", "job_status")
PAID_FLAG_CANDIDATES = ("paid", "is_paid")
PAID_AT_CANDIDATES = ("paid_at", "collected_at", "closed_at")
PAYMENT_CHANNEL_CANDIDATES = ("payment_channel",)
PAID_STATUS_VALUES = {
    "paid",
    "collected",
    "closed_paid",
    "closed-paid",
    "payment_received",
    "received",
}
MATCHED_STATUS_VALUES = {
    "matched",
    "reconciled",
    "linked",
    "applied",
    "booked",
    "assigned",
    "ticketed",
}
UNRECORDED_CHANNEL_VALUES = {"", "unrecorded", "unknown", "none", "n/a", "na", "-"}
SPLIT_KIND_VALUES = {
    "split",
    "worker",
    "pay_them",
    "pay-them",
    "paythem",
    "1099",
    "contractor",
}
KEPT_KIND_VALUES = {
    "kept",
    "keep",
    "you_keep",
    "you-keep",
    "company",
    "house",
    "retained",
    "owner",
}

VINCE_ZELLE_NOTE = (
    "Vince's 9 Zelle payouts already count in paid_to_worker. "
    "This report does not invent ticket matches for them."
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _truthy(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "t"}


def _blank(value: Any) -> bool:
    if value is None:
        return True
    return str(value).strip() == ""


def _lower(value: Any) -> str:
    return "" if value is None else str(value).strip().lower()


def _pick(columns: Iterable[str], candidates: Iterable[str]) -> str | None:
    available = {name.lower(): name for name in columns}
    for candidate in candidates:
        if candidate.lower() in available:
            return available[candidate.lower()]
    return None


def _ident(name: str) -> str:
    if not name or not all(ch.isalnum() or ch == "_" for ch in name):
        raise ValueError(f"Refusing unsafe SQL identifier: {name!r}")
    return f'"{name}"'


def candidate_db_paths(explicit: Path | None) -> list[Path]:
    paths: list[Path] = []

    def add(path: Path | None) -> None:
        if path is None:
            return
        resolved = path.expanduser()
        if resolved not in paths:
            paths.append(resolved)

    add(explicit)
    env_db = os.environ.get("TICKETS_DB")
    if env_db:
        add(Path(env_db))
    for env_name in ("HANDYMAN_ROOT", "HTM_ROOT", "DISPATCH_ROOT"):
        root = os.environ.get(env_name)
        if root:
            add(Path(root) / "state" / "tickets.db")
    add(ROOT / "state" / "tickets.db")
    add(Path.cwd() / "state" / "tickets.db")
    add(WINDOWS_DB)
    add(Path("/mnt/e/Handyman Ticket Manager/state/tickets.db"))
    return paths


def resolve_db_path(explicit: Path | None) -> tuple[Path | None, list[Path]]:
    tried = candidate_db_paths(explicit)
    for path in tried:
        if path.is_file():
            return path, tried
    return None, tried


def missing_db_message(tried: list[Path]) -> str:
    lines = [
        "tickets.db not found — unmatched books report is read-only and cannot run without the Dispatch database.",
        "Looked at:",
    ]
    for path in tried:
        lines.append(f"  {path}")
    lines.extend(
        [
            "Set TICKETS_DB to the sqlite file, or HANDYMAN_ROOT to the Handyman Ticket Manager folder",
            r"(Windows default: E:\Handyman Ticket Manager\state\tickets.db).",
            "No payouts were applied and no money was mutated.",
        ]
    )
    return "\n".join(lines)


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    uri = db_path.resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


def list_tables(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return {str(row[0]) for row in rows}


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({_ident(table)})").fetchall()
    return [str(row[1]) for row in rows]


def require_tables(tables: set[str]) -> None:
    missing = [name for name in REQUIRED_TABLES if name not in tables]
    if missing:
        present = ", ".join(sorted(tables)) or "(none)"
        raise SystemExit(
            "tickets.db is missing required books tables: "
            + ", ".join(missing)
            + f". Present tables: {present}."
        )


def year_clause(column: str | None, year: int) -> tuple[str, dict[str, Any]]:
    if column is None:
        return "", {}
    ident = _ident(column)
    key = f"year_{column}"
    if column.lower() == "tax_year":
        return f" AND CAST({ident} AS INTEGER) = :{key}", {key: year}
    iso = (
        f"(CAST(strftime('%Y', {ident}) AS INTEGER) = :{key} "
        f"OR CAST(strftime('%Y', {ident}, 'unixepoch') AS INTEGER) = :{key} "
        f"OR CAST({ident} AS TEXT) LIKE :{key}_prefix)"
    )
    return f" AND {iso}", {key: year, f"{key}_prefix": f"{year}%"}


def blank_ticket_clause(column: str) -> str:
    ident = _ident(column)
    return f"({ident} IS NULL OR TRIM(CAST({ident} AS TEXT)) = '')"


def classify_split_kept(row: dict[str, Any], columns: list[str]) -> str:
    kind_col = _pick(columns, KIND_CANDIDATES)
    if kind_col and not _blank(row.get(kind_col)):
        value = _lower(row.get(kind_col))
        if value in SPLIT_KIND_VALUES or "split" in value:
            return "split"
        if value in KEPT_KIND_VALUES or "keep" in value:
            return "kept"

    split_col = _pick(columns, SPLIT_AMOUNT_CANDIDATES)
    keep_col = _pick(columns, KEEP_AMOUNT_CANDIDATES)

    def amount(name: str | None) -> float | None:
        if not name:
            return None
        raw = row.get(name)
        if raw in (None, ""):
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    split_amt = amount(split_col)
    keep_amt = amount(keep_col)
    if split_amt is not None and keep_amt is not None:
        if split_amt and not keep_amt:
            return "split"
        if keep_amt and not split_amt:
            return "kept"
        if split_amt and keep_amt:
            return "split"
    if split_amt:
        return "split"
    if keep_amt:
        return "kept"
    return "unclassified"


def looks_like_vince_zelle(row: dict[str, Any]) -> bool:
    blob = " ".join(str(value) for value in row.values() if value is not None).lower()
    has_vince = "vince" in blob or "vincent knight" in blob
    has_zelle = "zelle" in blob
    return has_vince and has_zelle


def annotate_row(row: sqlite3.Row, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    data = {key: row[key] for key in row.keys()}
    if extra:
        data.update(extra)
    if looks_like_vince_zelle(data):
        data["vince_zelle"] = True
        data["counts_in_paid_to_worker"] = True
        data["invented_ticket_match"] = None
        data["note"] = VINCE_ZELLE_NOTE
    return data


def fetch_dicts(conn: sqlite3.Connection, sql: str, params: dict[str, Any]) -> list[sqlite3.Row]:
    return list(conn.execute(sql, params))


def report_blank_payout_transfers(
    conn: sqlite3.Connection, year: int
) -> dict[str, Any]:
    columns = table_columns(conn, "payout_transfers")
    ticket_col = _pick(columns, TICKET_NUMBER_CANDIDATES)
    if ticket_col is None:
        raise SystemExit(
            "payout_transfers has no ticket_number column. Columns: " + ", ".join(columns)
        )
    date_col = _pick(columns, DATE_CANDIDATES)
    year_sql, params = year_clause(date_col, year)
    sql = (
        f'SELECT * FROM "payout_transfers" '
        f"WHERE {blank_ticket_clause(ticket_col)}{year_sql}"
    )
    rows = fetch_dicts(conn, sql, params)
    grouped = {"split": [], "kept": [], "unclassified": []}
    for row in rows:
        as_dict = {key: row[key] for key in row.keys()}
        kind = classify_split_kept(as_dict, columns)
        grouped.setdefault(kind, [])
        grouped[kind].append(
            annotate_row(row, {"split_or_kept": kind, "ticket_number_column": ticket_col})
        )
    return {
        "table": "payout_transfers",
        "ticket_number_column": ticket_col,
        "tax_year_column": date_col,
        "tax_year_filter": year if date_col else "none — no date/tax_year column; listed all blank ticket_number rows",
        "count": sum(len(items) for items in grouped.values()),
        "counts_by_kind": {key: len(value) for key, value in grouped.items()},
        "rows": grouped,
    }


def unmatched_clause(columns: list[str]) -> str:
    """Use the strongest available unmatched signal. Do not invent ticket matches."""
    status_col = _pick(columns, MATCH_STATUS_CANDIDATES)
    if status_col:
        ident = _ident(status_col)
        matched_list = ", ".join(f"'{value}'" for value in sorted(MATCHED_STATUS_VALUES))
        return (
            f"(LOWER(TRIM(CAST({ident} AS TEXT))) NOT IN ({matched_list}) "
            f"OR {ident} IS NULL OR TRIM(CAST({ident} AS TEXT)) = '')"
        )
    unmatched_col = _pick(columns, UNMATCHED_FLAG_CANDIDATES)
    if unmatched_col:
        ident = _ident(unmatched_col)
        return f"(CAST({ident} AS TEXT) IN ('1', 'true', 'True', 'yes') OR {ident} = 1)"
    matched_col = _pick(columns, MATCHED_FLAG_CANDIDATES)
    if matched_col:
        ident = _ident(matched_col)
        return f"({ident} IS NULL OR CAST({ident} AS TEXT) IN ('0', 'false', 'False', ''))"
    link_col = _pick(columns, JOB_LINK_CANDIDATES)
    if link_col:
        return blank_ticket_clause(link_col)
    raise SystemExit(
        "stripe_deposit_lines has no match/ticket columns to detect unmatched rows. Columns: "
        + ", ".join(columns)
    )


def report_unmatched_deposits(conn: sqlite3.Connection, year: int) -> dict[str, Any]:
    columns = table_columns(conn, "stripe_deposit_lines")
    date_col = _pick(columns, DATE_CANDIDATES)
    year_sql, params = year_clause(date_col, year)
    where = unmatched_clause(columns)
    sql = f'SELECT * FROM "stripe_deposit_lines" WHERE {where}{year_sql}'
    rows = fetch_dicts(conn, sql, params)
    return {
        "table": "stripe_deposit_lines",
        "tax_year_column": date_col,
        "tax_year_filter": year if date_col else "none — no date/tax_year column; listed all unmatched rows",
        "match_detection": {
            "match_status_column": _pick(columns, MATCH_STATUS_CANDIDATES),
            "matched_flag_column": _pick(columns, MATCHED_FLAG_CANDIDATES),
            "unmatched_flag_column": _pick(columns, UNMATCHED_FLAG_CANDIDATES),
            "ticket_or_job_link_column": _pick(columns, JOB_LINK_CANDIDATES),
        },
        "invented_ticket_matches": False,
        "count": len(rows),
        "rows": [annotate_row(row) for row in rows],
    }


def paid_clause(columns: list[str]) -> str:
    clauses: list[str] = []
    status_col = _pick(columns, PAID_STATUS_CANDIDATES)
    if status_col:
        ident = _ident(status_col)
        values = ", ".join(f"'{value}'" for value in sorted(PAID_STATUS_VALUES))
        clauses.append(f"LOWER(TRIM(CAST({ident} AS TEXT))) IN ({values})")
    flag_col = _pick(columns, PAID_FLAG_CANDIDATES)
    if flag_col:
        ident = _ident(flag_col)
        clauses.append(f"(CAST({ident} AS TEXT) IN ('1', 'true', 'True', 'yes') OR {ident} = 1)")
    paid_at_col = _pick(columns, PAID_AT_CANDIDATES)
    if paid_at_col:
        ident = _ident(paid_at_col)
        clauses.append(f"({ident} IS NOT NULL AND TRIM(CAST({ident} AS TEXT)) != '')")
    if not clauses:
        raise SystemExit(
            "job_books has no paid status/flag/date columns. Columns: " + ", ".join(columns)
        )
    return "(" + " OR ".join(clauses) + ")"


def unrecorded_channel_clause(column: str) -> str:
    ident = _ident(column)
    values = ", ".join(f"'{value}'" for value in sorted(UNRECORDED_CHANNEL_VALUES) if value)
    return (
        f"({ident} IS NULL OR TRIM(CAST({ident} AS TEXT)) = '' "
        f"OR LOWER(TRIM(CAST({ident} AS TEXT))) IN ({values}))"
    )


def report_unrecorded_paid_jobs(conn: sqlite3.Connection, year: int) -> dict[str, Any]:
    columns = table_columns(conn, "job_books")
    channel_col = _pick(columns, PAYMENT_CHANNEL_CANDIDATES)
    if channel_col is None:
        raise SystemExit(
            "job_books has no payment_channel column. Columns: " + ", ".join(columns)
        )
    date_col = _pick(columns, DATE_CANDIDATES)
    year_sql, params = year_clause(date_col, year)
    sql = (
        f'SELECT * FROM "job_books" '
        f"WHERE {paid_clause(columns)} AND {unrecorded_channel_clause(channel_col)}{year_sql}"
    )
    rows = fetch_dicts(conn, sql, params)
    return {
        "table": "job_books",
        "payment_channel_column": channel_col,
        "tax_year_column": date_col,
        "tax_year_filter": year if date_col else "none — no date/tax_year column; listed all paid unrecorded-channel rows",
        "count": len(rows),
        "rows": [annotate_row(row) for row in rows],
    }


def default_out_path(db_path: Path, year: int) -> Path:
    parent = db_path.parent
    books_dir = parent / "books" if parent.name.lower() == "state" else ROOT / "state" / "books"
    return books_dir / f"unmatched-financial-records-{year}.json"


def build_report(conn: sqlite3.Connection, db_path: Path, year: int) -> dict[str, Any]:
    tables = list_tables(conn)
    require_tables(tables)
    payouts = report_blank_payout_transfers(conn, year)
    deposits = report_unmatched_deposits(conn, year)
    jobs = report_unrecorded_paid_jobs(conn, year)
    return {
        "generated_at": _utc_now(),
        "tax_year": year,
        "db_path": str(db_path),
        "read_only": True,
        "auto_apply_payouts": False,
        "mutate_live_money": False,
        "invent_ticket_matches": False,
        "policy": {
            "vince_zelle": VINCE_ZELLE_NOTE,
            "website_retail_prices": "unchanged",
        },
        "payout_transfers_blank_ticket_number": payouts,
        "unmatched_stripe_deposit_lines": deposits,
        "paid_job_books_payment_channel_unrecorded": jobs,
    }


def print_summary(report: dict[str, Any], out_path: Path) -> None:
    payouts = report["payout_transfers_blank_ticket_number"]
    deposits = report["unmatched_stripe_deposit_lines"]
    jobs = report["paid_job_books_payment_channel_unrecorded"]
    counts = payouts["counts_by_kind"]
    print("Read-only unmatched books report")
    print(f"DB: {report['db_path']}")
    print(f"Tax year: {report['tax_year']}")
    print(f"Wrote: {out_path}")
    print(
        "payout_transfers blank ticket_number: "
        f"{payouts['count']} (split={counts.get('split', 0)} "
        f"kept={counts.get('kept', 0)} unclassified={counts.get('unclassified', 0)})"
    )
    print(f"unmatched stripe_deposit_lines: {deposits['count']}")
    print(f"paid job_books payment_channel unrecorded: {jobs['count']}")
    print(VINCE_ZELLE_NOTE)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only report of unmatched Dispatch books records. "
            "Does not apply payouts or change website prices."
        ),
        epilog=(
            "Run from the website or Handyman Ticket Manager root:\n"
            "  python scripts/report-unmatched-books.py --year 2026\n"
            "  python scripts/report-unmatched-books.py --year 2026 "
            "--db state/tickets.db"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--year",
        type=int,
        default=datetime.now().year,
        help="Tax year to report (default: current calendar year)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="Path to tickets.db (default: TICKETS_DB, HANDYMAN_ROOT/state/tickets.db, or ./state/tickets.db)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="JSON output path (default: state/books/unmatched-financial-records-YEAR.json)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    db_path, tried = resolve_db_path(args.db)
    if db_path is None:
        print(missing_db_message(tried), file=sys.stderr)
        return 2

    try:
        conn = connect_readonly(db_path)
    except sqlite3.Error as exc:
        print(f"Could not open tickets.db read-only at {db_path}: {exc}", file=sys.stderr)
        return 1

    try:
        report = build_report(conn, db_path, args.year)
    except sqlite3.Error as exc:
        print(f"Read-only query failed against {db_path}: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    out_path = args.out or default_out_path(db_path, args.year)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    print_summary(report, out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
