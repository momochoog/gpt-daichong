#!/usr/bin/env python3
"""Verify the constructed reconciliation example offline using only the stdlib."""

import csv
from pathlib import Path
import sqlite3


HERE = Path(__file__).resolve().parent
COLUMNS = (
    "order_key",
    "payment_state",
    "delivery_state",
    "evidence_state",
    "next_step",
)


def check_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}\nexpected: {expected!r}\nactual:   {actual!r}")


def run_query(sql):
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("PRAGMA query_only=ON")
        check_equal(
            connection.execute("PRAGMA query_only").fetchone()[0],
            1,
            "query_only must be enabled",
        )
        cursor = connection.execute(sql)
        check_equal(
            tuple(column[0] for column in cursor.description),
            COLUMNS,
            "output columns",
        )
        return cursor.fetchall()
    finally:
        connection.close()


def replace_fixture(sql, old, new):
    # Fail clearly if a later edit changes the sample fixture being tested.
    check_equal(sql.count(old), 1, "boundary fixture must match exactly once")
    return sql.replace(old, new, 1)


def main():
    sql = (HERE / "reconciliation.sql").read_text(encoding="utf-8")
    with (HERE / "expected.tsv").open(encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream, delimiter="\t")
        check_equal(tuple(next(reader)), COLUMNS, "expected.tsv columns")
        expected = [tuple(row) for row in reader]
    check_equal(len(expected), 9, "number of core scenarios")
    check_equal(len({row[0] for row in expected}), 9, "unique core order keys")
    baseline = run_query(sql)
    check_equal(baseline, expected, "complete nine-row baseline output")
    print("PASS: 9 core scenarios (complete output matches expected.tsv)")

    order = "('O04', 'A04', 'paid',     'completed',  '2026-09-08 11:20:00')"
    observation = "(1, 'O04', 'A04', 'plus', '2026-09-08 11:50:00')"
    older_observation = "(2, 'O04', 'A04', 'free', '2026-09-08 11:10:00')"
    # Each case supplies one changed input and an explicit complete O04 output.
    cases = [
        (
            "missing_target_account",
            order,
            "('O04', NULL, 'paid',     'completed',  '2026-09-08 11:20:00')",
            ("O04", "paid", "completed", "account_mismatch", "review_evidence"),
        ),
        (
            "empty_target_account",
            order,
            "('O04', '', 'paid',     'completed',  '2026-09-08 11:20:00')",
            ("O04", "paid", "completed", "account_mismatch", "review_evidence"),
        ),
        (
            "missing_payment_time",
            order,
            "('O04', 'A04', 'paid',     'completed',  NULL)",
            ("O04", "paid", "completed", "payment_time_unknown", "check_payment_time"),
        ),
        (
            "evidence_before_payment",
            order,
            "('O04', 'A04', 'paid',     'completed',  '2026-09-08 11:55:00')",
            ("O04", "paid", "completed", "stale", "review_evidence"),
        ),
        (
            "freshness_lower_boundary",
            observation,
            "(1, 'O04', 'A04', 'plus', '2026-09-08 11:30:00')",
            ("O04", "paid", "completed", "recent_plus", "plus_observed"),
        ),
        (
            "one_second_too_old",
            observation,
            "(1, 'O04', 'A04', 'plus', '2026-09-08 11:29:59')",
            ("O04", "paid", "completed", "stale", "review_evidence"),
        ),
        (
            "observation_at_query_time",
            observation,
            "(1, 'O04', 'A04', 'plus', '2026-09-08 12:00:00')",
            ("O04", "paid", "completed", "recent_plus", "plus_observed"),
        ),
        (
            "future_observation",
            observation,
            "(1, 'O04', 'A04', 'plus', '2026-09-08 12:00:01')",
            ("O04", "paid", "completed", "invalid_time", "review_evidence"),
        ),
        (
            "newer_free_replaces_older_plus",
            older_observation,
            "(2, 'O04', 'A04', 'free', '2026-09-08 11:55:00')",
            ("O04", "paid", "completed", "recent_other_plan", "review_evidence"),
        ),
        (
            "unknown_plan",
            observation,
            "(1, 'O04', 'A04', NULL, '2026-09-08 11:50:00')",
            ("O04", "paid", "completed", "unknown_plan", "review_evidence"),
        ),
        (
            "unknown_payment_state",
            order,
            "('O04', 'A04', 'unknown',  'completed',  '2026-09-08 11:20:00')",
            ("O04", "unknown", "completed", "recent_plus", "confirm_payment"),
        ),
    ]
    check_equal(len(cases), 11, "number of boundary scenarios")
    for name, old, new, expected_order in cases:
        actual_rows = run_query(replace_fixture(sql, old, new))
        expected_rows = [expected_order if row[0] == "O04" else row for row in expected]
        check_equal(actual_rows, expected_rows, name)
        print(f"PASS: {name}")

    print(f"OK: 9 core + 11 boundary scenarios; SQLite {sqlite3.sqlite_version}")


if __name__ == "__main__":
    main()
