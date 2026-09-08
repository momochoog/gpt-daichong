# Subscription reconciliation with SQLite

Keep payment status, delivery status, and account-plan observations separate when investigating a subscription order. This example uses constructed orders and manually recorded plan observations to choose a next step for each order.

中文说明：本示例使用构造订单和人工套餐观察记录，演示付款、交付与套餐状态的 SQL 对账，可离线运行。

## Run the query

From this directory, with SQLite supporting window functions:

```sh
sqlite3 -header -column :memory: < reconciliation.sql
```

The query contains its own sample rows in CTEs and requires no existing tables. All times use the same Beijing wall-clock format, with a fixed evaluation time of `2026-09-08 12:00:00`. No timezone conversion is performed. The freshness window is the inclusive interval from `11:30:00` to `12:00:00`, and an observation must also be at or after payment confirmation.

`expected.tsv` contains the complete nine-row output. The cases cover unconfirmed payment, delivery in progress, missing evidence, a recent Plus observation, stale evidence, a different account, a refund, a recent Free observation, and a future observation.

`plus_observed` means the supplied evidence shows Plus on the intended account at the observation time. A renewal needs additional validity-period evidence to establish added subscription time.

## Verify the example

Python 3 and its standard-library `sqlite3` module are sufficient:

```sh
python3 verify.py
```

The verifier runs the SQL in memory with `PRAGMA query_only=ON`, checks all nine output rows against `expected.tsv`, and checks eleven boundary cases. It prints one result for each boundary case and exits with an error if any expectation differs.

Boundary cases include missing or empty account keys, missing payment time, evidence before payment, both freshness boundaries, an observation one second too old, a future observation, a newer Free observation, an unknown plan, and an unknown payment state.

The query and verifier use constructed data only and make no network or account API calls. Account observations are supplied separately. In an application, normalize and validate incoming timestamps before ranking observations; define separate handling for partial refunds, duplicate payment events, and conflicting observations at the same time.

## SQL references

- [SQLite WITH clause](https://www.sqlite.org/lang_with.html)
- [SQLite window functions](https://www.sqlite.org/windowfunctions.html)
- [SQLite date and time functions](https://www.sqlite.org/lang_datefunc.html)
