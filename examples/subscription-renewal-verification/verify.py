#!/usr/bin/env python3
"""Offline assertions for renewal.sql. Python standard library only."""

import csv
from pathlib import Path
import sqlite3


HERE = Path(__file__).resolve().parent
SQL = (HERE / "renewal.sql").read_text(encoding="utf-8")
BEGIN = "-- BEGIN SAMPLE INPUT"
END = "-- END SAMPLE INPUT"
assert SQL.count(BEGIN) == SQL.count(END) == 1
PREFIX, rest = SQL.split(BEGIN)
_, SUFFIX = rest.split(END)

ORDER_COLUMNS = (
    "order_key", "target_account", "payment_state", "delivery_state",
    "paid_at", "period_start_at", "target_expires_at",
)
OBSERVATION_COLUMNS = (
    "order_key", "role", "account_key", "plan_name", "observed_at", "expires_at",
)
AS_OF = "2026-09-09 12:00:00"
PAID = "2026-09-09 11:20:00"
OLD = "2026-10-09 12:00:00"
TARGET = "2026-11-09 12:00:00"


def input_cte(name, columns, rows):
    """Build only fixture inputs; bind every data value as a parameter."""
    if not rows:
        body = "SELECT " + ", ".join("NULL" for _ in columns) + " WHERE 0"
        return f"{name}({', '.join(columns)}) AS ({body})", []
    placeholders = "(" + ", ".join("?" for _ in columns) + ")"
    body = "VALUES " + ", ".join(placeholders for _ in rows)
    return f"{name}({', '.join(columns)}) AS ({body})", [
        value for row in rows for value in row
    ]


def run_fixture(connection, order, observations, config=(AS_OF, 1800)):
    pieces, bindings = [], []
    for name, columns, rows in (
        ("params", ("as_of", "max_age_seconds"), [config]),
        ("orders", ORDER_COLUMNS, [[order[column] for column in ORDER_COLUMNS]]),
        ("observations", OBSERVATION_COLUMNS,
         [[item[column] for column in OBSERVATION_COLUMNS] for item in observations]),
    ):
        cte, values = input_cte(name, columns, rows)
        pieces.append(cte)
        bindings.extend(values)
    return connection.execute(PREFIX + ",\n".join(pieces) + SUFFIX, bindings).fetchall()


def main():
    if sqlite3.sqlite_version_info < (3, 25, 0):
        raise RuntimeError("SQLite 3.25.0 or later is required for ROW_NUMBER().")
    with sqlite3.connect(":memory:") as connection:
        connection.execute("PRAGMA query_only = ON")
        try:
            connection.execute("CREATE TABLE forbidden_write (value TEXT)")
        except sqlite3.OperationalError:
            pass
        else:
            raise AssertionError("The verification connection must reject writes.")

        with (HERE / "expected.tsv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle, delimiter="\t"))
        cursor = connection.execute(SQL)
        assert [column[0] for column in cursor.description] == rows[0]
        actual = cursor.fetchall()
        expected = [tuple(row) for row in rows[1:]]
        assert len(expected) == 12, "The checked-in expected output must contain 12 cases."
        assert actual == expected, f"Core output mismatch:\n{actual!r}\n!=\n{expected!r}"

        count = 0

        def check(name, next_step, *, evidence="usable", mode="active_extension",
                  order_changes=None, baseline_changes=None, result_changes=None,
                  omit_baseline=False, omit_result=False, extra=(), config=(AS_OF, 1800)):
            nonlocal count
            order = dict(zip(ORDER_COLUMNS, (
                "T01", "acct-demo", "paid", "completed", PAID, OLD, TARGET,
            )))
            order.update(order_changes or {})
            baseline = dict(zip(OBSERVATION_COLUMNS, (
                "T01", "baseline", "acct-demo", "plus", "2026-09-09 11:00:00", OLD,
            )))
            result = dict(zip(OBSERVATION_COLUMNS, (
                "T01", "result", "acct-demo", "plus", "2026-09-09 11:50:00", TARGET,
            )))
            baseline.update(baseline_changes or {})
            result.update(result_changes or {})
            observations = ([] if omit_baseline else [baseline]) + ([] if omit_result else [result])
            for changes in extra:
                duplicate = dict(baseline if changes.get("role") == "baseline" else result)
                duplicate.update(changes)
                observations.append(duplicate)
            output = run_fixture(connection, order, observations, config)
            expected_row = (
                "T01", order["payment_state"], order["delivery_state"], mode, evidence, next_step,
            )
            assert output == [expected_row], f"{name}: {output!r} != {[expected_row]!r}"
            count += 1

        def review(name, evidence, **changes):
            check(name, "review_evidence", evidence=evidence, mode="unknown", **changes)

        # Boundary timestamps: equality at the freshness limit is accepted;
        # the same second as payment cannot prove before/after ordering.
        check("result exactly 30 minutes old", "target_period_observed",
              result_changes={"observed_at": "2026-09-09 11:30:00"})
        review("result one second too old", "stale_result",
               result_changes={"observed_at": "2026-09-09 11:29:59"})
        check("baseline exactly 30 minutes before payment", "target_period_observed",
              baseline_changes={"observed_at": "2026-09-09 10:50:00"})
        review("baseline one second too old", "stale_baseline",
               baseline_changes={"observed_at": "2026-09-09 10:49:59"})
        review("baseline at payment second", "baseline_not_before_payment",
               baseline_changes={"observed_at": PAID})
        review("baseline after payment", "baseline_not_before_payment",
               baseline_changes={"observed_at": "2026-09-09 11:21:00"})
        review("result at payment second", "result_not_after_payment",
               result_changes={"observed_at": PAID})
        review("result before payment", "result_not_after_payment",
               result_changes={"observed_at": "2026-09-09 11:19:59"})
        review("future result", "future_result",
               result_changes={"observed_at": "2026-09-09 12:00:01"})
        check("result exactly at audit time", "target_period_observed",
              result_changes={"observed_at": AS_OF})
        check("future payment", "check_payment_time", evidence="invalid_payment_time", mode="unknown",
              order_changes={"paid_at": "2026-09-09 12:00:01"})

        # Missing/illegal dates cannot be discarded to expose a favorable row.
        review("missing baseline", "no_baseline", omit_baseline=True)
        review("missing result", "no_result", omit_result=True)
        review("no observations", "no_baseline", omit_baseline=True, omit_result=True)
        review("NULL expiry", "missing_observation_date", result_changes={"expires_at": None})
        review("empty timestamp", "missing_observation_date", result_changes={"observed_at": ""})
        for name, value in (
            ("February 30", "2026-02-30 12:00:00"),
            ("non-leap February 29", "2026-02-29 12:00:00"),
            ("24 hour time", "2026-11-09 24:00:00"),
            ("timezone suffix", "2026-11-09 12:00:00Z"),
            ("year zero", "0000-11-09 12:00:00"),
            ("non-date", "not-a-date"),
        ):
            review(name, "invalid_observation_date", result_changes={"expires_at": value})
        review("malformed old record cannot be ignored", "invalid_observation_date",
               extra=({"observed_at": "bad-time"},))
        check("missing paid_at", "check_payment_time", evidence="invalid_payment_time", mode="unknown",
              order_changes={"paid_at": None})
        check("invalid audit time", "check_configuration", evidence="invalid_configuration", mode="unknown",
              config=("2026-02-30 12:00:00", 1800))
        check("zero freshness interval", "check_configuration", evidence="invalid_configuration", mode="unknown",
              config=(AS_OF, 0))
        check("out-of-range freshness interval", "check_configuration", evidence="invalid_configuration", mode="unknown",
              config=(AS_OF, 9223372036854775807))

        # Identical duplicates are harmless, conflicting latest evidence is not.
        check("identical duplicate", "target_period_observed", extra=({},))
        review("latest conflicting plan", "conflicting_latest_observations",
               extra=({"plan_name": "free"},))
        review("latest conflicting account", "conflicting_latest_observations",
               extra=({"account_key": "acct-other"},))
        review("latest conflicting baseline expiry", "conflicting_latest_observations",
               extra=({"role": "baseline", "expires_at": "2026-10-10 12:00:00"},))
        check("new observation supersedes older conflict", "target_period_observed", extra=(
            {"observed_at": "2026-09-09 11:40:00", "expires_at": OLD},
            {"observed_at": "2026-09-09 11:40:00", "expires_at": TARGET},
        ))
        check("latest unfavorable record beats older favorable record", "no_extension_observed",
              result_changes={"expires_at": OLD},
              extra=({"observed_at": "2026-09-09 11:40:00", "expires_at": TARGET},))
        review("wrong baseline account", "account_mismatch",
               baseline_changes={"account_key": "acct-other"})
        review("all account fields are blank spaces", "missing_target_account",
               order_changes={"target_account": "   "},
               baseline_changes={"account_key": "   "}, result_changes={"account_key": "   "})
        for name, value in (
            ("tab-only account", "\t"),
            ("newline-only account", "\n"),
            ("mixed ASCII whitespace account", "\t\n\v\f\r "),
        ):
            review(name, "missing_target_account",
                   order_changes={"target_account": value},
                   baseline_changes={"account_key": value}, result_changes={"account_key": value})
        review("blank observation account", "account_mismatch",
               result_changes={"account_key": "   "})
        review("unknown observation role", "unknown_observation_role", extra=({"role": "unclassified"},))
        review("missing result plan", "unknown_plan", result_changes={"plan_name": None})
        review("blank result plan", "unknown_plan", result_changes={"plan_name": "   "})
        review("future baseline expiry contradicts free plan", "baseline_plan_conflict",
               baseline_changes={"plan_name": "free"})

        # Target coverage uses supplied dates, not a guessed 30-day duration.
        check("one-second extension is not sufficient", "extension_short",
              result_changes={"expires_at": "2026-10-09 12:00:01"})
        check("one second short of target", "extension_short",
              result_changes={"expires_at": "2026-11-09 11:59:59"})
        check("beyond target remains only observed coverage", "target_period_observed",
              result_changes={"expires_at": "2026-11-10 12:00:00"})
        check("expiry regressed but is still in the future", "expiry_regressed",
              result_changes={"expires_at": "2026-10-01 12:00:00"})
        check("result is no longer Plus", "review_current_plan", result_changes={"plan_name": "free"})
        check("result expiry exactly at audit time", "current_plan_expired", result_changes={"expires_at": AS_OF})
        check("missing target", "check_target_period", order_changes={"target_expires_at": None})
        check("illegal target", "check_target_period", order_changes={"target_expires_at": "2026-02-30 12:00:00"})
        check("target cannot equal period start", "check_target_period", order_changes={"target_expires_at": OLD})
        check("active extension cannot silently change agreed start", "check_target_period",
              order_changes={"period_start_at": "2026-10-10 12:00:00"})
        check("expiry equals payment time is expired mode", "target_period_observed", mode="expired_restart",
              baseline_changes={"expires_at": PAID},
              order_changes={"period_start_at": PAID, "target_expires_at": "2026-10-09 11:20:00"},
              result_changes={"expires_at": "2026-10-09 11:20:00"})
        check("expired account cannot backdate restart before payment", "check_target_period", mode="expired_restart",
              baseline_changes={"expires_at": "2026-09-09 10:00:00", "plan_name": "free"},
              order_changes={"period_start_at": "2026-09-09 11:19:59"})
        check("future restart has not yet been observed", "check_target_period", mode="expired_restart",
              baseline_changes={"expires_at": "2026-09-09 10:00:00", "plan_name": "free"},
              order_changes={"period_start_at": "2026-09-09 11:50:01"})
        check("calendar month end is an explicit target", "target_period_observed",
              baseline_changes={"expires_at": "2027-01-31 12:00:00"},
              order_changes={"period_start_at": "2027-01-31 12:00:00", "target_expires_at": "2027-02-28 12:00:00"},
              result_changes={"expires_at": "2027-02-28 12:00:00"})
        check("valid leap-day target", "target_period_observed",
              baseline_changes={"expires_at": "2028-01-31 12:00:00"},
              order_changes={"period_start_at": "2028-01-31 12:00:00", "target_expires_at": "2028-02-29 12:00:00"},
              result_changes={"expires_at": "2028-02-29 12:00:00"})
        check("completed payment does not establish delivery", "verify_delivery",
              order_changes={"delivery_state": "pending"})

    print(f"PASS: 12 exact-output cases + {count} boundary cases; SQLite {sqlite3.sqlite_version}.")
    print("PASS: in-memory query_only connection rejected writes; no network or external dependencies.")


if __name__ == "__main__":
    main()
