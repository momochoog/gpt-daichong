-- Constructed examples only. All timestamps use UTC, at one-second precision.
-- Run this one SELECT offline; it neither obtains nor updates account data.
WITH
-- BEGIN SAMPLE INPUT
params(as_of, max_age_seconds) AS (
  VALUES ('2026-09-09 12:00:00', 1800)
),
orders(order_key, target_account, payment_state, delivery_state,
       paid_at, period_start_at, target_expires_at) AS (
  VALUES
    ('A01', 'acct-demo', 'paid', 'completed', '2026-09-09 11:20:00', '2026-10-09 12:00:00', '2026-11-09 12:00:00'),
    ('A02', 'acct-demo', 'paid', 'completed', '2026-09-09 11:20:00', '2026-10-09 12:00:00', '2026-11-09 12:00:00'),
    ('A03', 'acct-demo', 'paid', 'completed', '2026-09-09 11:20:00', '2026-10-09 12:00:00', '2026-11-09 12:00:00'),
    ('A04', 'acct-demo', 'paid', 'completed', '2026-09-09 11:20:00', '2026-09-09 11:20:00', '2026-10-09 11:20:00'),
    ('A05', 'acct-demo', 'paid', 'completed', '2026-09-09 11:20:00', '2026-09-09 11:20:00', '2026-10-09 11:20:00'),
    ('A06', 'acct-demo', 'refunded', 'completed', '2026-09-09 11:20:00', '2026-10-09 12:00:00', '2026-11-09 12:00:00'),
    ('A07', 'acct-demo', 'unpaid', 'pending', NULL, '2026-10-09 12:00:00', '2026-11-09 12:00:00'),
    ('A08', 'acct-demo', 'paid', 'processing', '2026-09-09 11:20:00', '2026-10-09 12:00:00', '2026-11-09 12:00:00'),
    ('A09', 'acct-demo', 'paid', 'completed', '2026-09-09 11:20:00', '2026-10-09 12:00:00', '2026-11-09 12:00:00'),
    ('A10', 'acct-demo', 'paid', 'completed', '2026-09-09 11:20:00', '2026-10-09 12:00:00', '2026-11-09 12:00:00'),
    ('A11', 'acct-demo', 'paid', 'completed', '2026-09-09 11:20:00', '2026-10-09 12:00:00', '2026-11-09 12:00:00'),
    ('A12', 'acct-demo', 'paid', 'completed', '2026-09-09 11:20:00', '2026-10-09 12:00:00', '2026-11-09 12:00:00')
),
observations(order_key, role, account_key, plan_name, observed_at, expires_at) AS (
  VALUES
    ('A01', 'baseline', 'acct-demo', 'plus', '2026-09-09 11:00:00', '2026-10-09 12:00:00'),
    ('A01', 'result', 'acct-demo', 'plus', '2026-09-09 11:50:00', '2026-11-09 12:00:00'),
    ('A02', 'baseline', 'acct-demo', 'plus', '2026-09-09 11:00:00', '2026-10-09 12:00:00'),
    ('A02', 'result', 'acct-demo', 'plus', '2026-09-09 11:50:00', '2026-10-09 12:00:00'),
    ('A03', 'baseline', 'acct-demo', 'plus', '2026-09-09 11:00:00', '2026-10-09 12:00:00'),
    ('A03', 'result', 'acct-demo', 'plus', '2026-09-09 11:50:00', '2026-10-19 12:00:00'),
    ('A04', 'baseline', 'acct-demo', 'free', '2026-09-09 11:00:00', '2026-09-09 10:00:00'),
    ('A04', 'result', 'acct-demo', 'plus', '2026-09-09 11:50:00', '2026-10-09 11:20:00'),
    ('A05', 'baseline', 'acct-demo', 'free', '2026-09-09 11:00:00', '2026-09-09 10:00:00'),
    ('A05', 'result', 'acct-demo', 'plus', '2026-09-09 11:50:00', '2026-10-01 11:20:00'),
    ('A06', 'baseline', 'acct-demo', 'plus', '2026-09-09 11:00:00', '2026-10-09 12:00:00'),
    ('A06', 'result', 'acct-demo', 'plus', '2026-09-09 11:50:00', '2026-11-09 12:00:00'),
    ('A07', 'baseline', 'acct-demo', 'plus', '2026-09-09 11:00:00', '2026-10-09 12:00:00'),
    ('A07', 'result', 'acct-demo', 'plus', '2026-09-09 11:50:00', '2026-11-09 12:00:00'),
    ('A08', 'baseline', 'acct-demo', 'plus', '2026-09-09 11:00:00', '2026-10-09 12:00:00'),
    ('A08', 'result', 'acct-demo', 'plus', '2026-09-09 11:50:00', '2026-11-09 12:00:00'),
    ('A09', 'baseline', 'acct-demo', 'plus', '2026-09-09 11:00:00', '2026-10-09 12:00:00'),
    ('A09', 'result', 'acct-other', 'plus', '2026-09-09 11:50:00', '2026-11-09 12:00:00'),
    ('A10', 'baseline', 'acct-demo', 'plus', '2026-09-09 11:00:00', '2026-10-09 12:00:00'),
    ('A10', 'result', 'acct-demo', 'plus', '2026-09-09 11:29:59', '2026-11-09 12:00:00'),
    ('A11', 'baseline', 'acct-demo', 'plus', '2026-09-09 11:00:00', '2026-10-09 12:00:00'),
    ('A11', 'result', 'acct-demo', 'plus', '2026-09-09 11:50:00', '2026-02-30 12:00:00'),
    ('A12', 'baseline', 'acct-demo', 'plus', '2026-09-09 11:00:00', '2026-10-09 12:00:00'),
    ('A12', 'result', 'acct-demo', 'plus', '2026-09-09 11:50:00', '2026-11-09 12:00:00'),
    ('A12', 'result', 'acct-demo', 'plus', '2026-09-09 11:50:00', '2026-10-09 12:00:00')
)
-- END SAMPLE INPUT
,
-- SQLite accepts more date forms than this example. Require canonical UTC text
-- and a round trip: non-NULL julianday() alone would accept February 30.
date_values(value) AS (
  SELECT as_of FROM params
  UNION SELECT paid_at FROM orders
  UNION SELECT period_start_at FROM orders
  UNION SELECT target_expires_at FROM orders
  UNION SELECT observed_at FROM observations
  UNION SELECT expires_at FROM observations
),
valid_dates(value) AS (
  SELECT value FROM date_values
  WHERE typeof(value) = 'text' AND length(value) = 19
    AND value GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]'
    AND substr(value, 1, 4) BETWEEN '0001' AND '9999'
    AND datetime(value, '+0 seconds') = value
),
distinct_observations AS (
  SELECT DISTINCT * FROM observations
),
observation_issues AS (
  SELECT order_key,
    MAX(CASE WHEN observed_at IS NULL OR observed_at = ''
                   OR expires_at IS NULL OR expires_at = '' THEN 1 ELSE 0 END) AS missing_date,
    MAX(CASE WHEN NOT EXISTS (SELECT 1 FROM valid_dates WHERE value = observed_at)
                   OR NOT EXISTS (SELECT 1 FROM valid_dates WHERE value = expires_at)
             THEN 1 ELSE 0 END) AS invalid_date,
    MAX(CASE WHEN COALESCE(role, '') NOT IN ('baseline', 'result')
             THEN 1 ELSE 0 END) AS unknown_role
  FROM distinct_observations GROUP BY order_key
),
-- Identical repeated records collapse. Different records at the latest second
-- remain a conflict; MIN below is never used to approve a conflicting group.
observation_groups AS (
  SELECT order_key, role, observed_at, COUNT(*) AS variants,
         MIN(account_key) AS account_key, MIN(plan_name) AS plan_name,
         MIN(expires_at) AS expires_at
  FROM distinct_observations
  GROUP BY order_key, role, observed_at
),
ranked_observations AS (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY order_key, role ORDER BY observed_at DESC
  ) AS rank_no
  FROM observation_groups
),
joined AS (
  SELECT o.*, p.as_of, p.max_age_seconds,
    b.observed_at AS baseline_at, b.expires_at AS old_expiry,
    b.account_key AS baseline_account, b.plan_name AS baseline_plan,
    b.variants AS baseline_variants,
    r.observed_at AS result_at, r.expires_at AS new_expiry,
    r.account_key AS result_account, r.plan_name AS result_plan,
    r.variants AS result_variants,
    i.missing_date, i.invalid_date, i.unknown_role
  FROM orders AS o CROSS JOIN params AS p
  LEFT JOIN ranked_observations AS b
    ON b.order_key = o.order_key AND b.role = 'baseline' AND b.rank_no = 1
  LEFT JOIN ranked_observations AS r
    ON r.order_key = o.order_key AND r.role = 'result' AND r.rank_no = 1
  LEFT JOIN observation_issues AS i ON i.order_key = o.order_key
),
evidence AS (
  SELECT *, CASE
    WHEN NOT EXISTS (SELECT 1 FROM valid_dates WHERE value = as_of)
      OR typeof(max_age_seconds) != 'integer' OR max_age_seconds NOT BETWEEN 1 AND 86400
      THEN 'invalid_configuration'
    WHEN NOT EXISTS (SELECT 1 FROM valid_dates WHERE value = paid_at)
      OR paid_at > as_of THEN 'invalid_payment_time'
    WHEN trim(COALESCE(target_account, ''),
              char(9) || char(10) || char(11) || char(12) || char(13) || char(32)) = ''
      THEN 'missing_target_account'
    WHEN missing_date = 1 THEN 'missing_observation_date'
    WHEN invalid_date = 1 THEN 'invalid_observation_date'
    WHEN unknown_role = 1 THEN 'unknown_observation_role'
    WHEN baseline_variants IS NULL THEN 'no_baseline'
    WHEN result_variants IS NULL THEN 'no_result'
    WHEN baseline_variants > 1 OR result_variants > 1
      THEN 'conflicting_latest_observations'
    WHEN COALESCE(baseline_account, '') != target_account
      OR COALESCE(result_account, '') != target_account THEN 'account_mismatch'
    WHEN COALESCE(baseline_plan, '') NOT IN ('plus', 'free')
      OR trim(COALESCE(result_plan, '')) = '' THEN 'unknown_plan'
    WHEN baseline_at >= paid_at THEN 'baseline_not_before_payment'
    WHEN baseline_at < datetime(paid_at, '-' || max_age_seconds || ' seconds')
      THEN 'stale_baseline'
    WHEN result_at <= paid_at THEN 'result_not_after_payment'
    WHEN result_at > as_of THEN 'future_result'
    WHEN result_at < datetime(as_of, '-' || max_age_seconds || ' seconds')
      THEN 'stale_result'
    WHEN old_expiry > paid_at AND baseline_plan != 'plus'
      THEN 'baseline_plan_conflict'
    ELSE 'usable'
  END AS evidence_state
  FROM joined
),
assessed AS (
  SELECT *, CASE
    WHEN evidence_state != 'usable' THEN 'unknown'
    WHEN old_expiry > paid_at THEN 'active_extension'
    ELSE 'expired_restart'
  END AS renewal_mode,
  CASE
    WHEN evidence_state = 'invalid_configuration' THEN 'check_configuration'
    WHEN payment_state = 'refunded' THEN 'refund_review'
    WHEN COALESCE(payment_state, '') != 'paid' THEN 'confirm_payment'
    WHEN evidence_state = 'invalid_payment_time' THEN 'check_payment_time'
    WHEN NOT EXISTS (SELECT 1 FROM valid_dates WHERE value = period_start_at)
      OR NOT EXISTS (SELECT 1 FROM valid_dates WHERE value = target_expires_at)
      OR target_expires_at <= period_start_at THEN 'check_target_period'
    WHEN delivery_state = 'processing' THEN 'delivery_processing'
    WHEN COALESCE(delivery_state, '') != 'completed' THEN 'verify_delivery'
    WHEN evidence_state != 'usable' THEN 'review_evidence'
    -- This example models continuous extension for an active account, and an
    -- explicitly agreed restart at/after payment for an expired account.
    WHEN old_expiry > paid_at AND period_start_at != old_expiry
      THEN 'check_target_period'
    WHEN old_expiry <= paid_at
      AND (period_start_at < paid_at OR period_start_at > result_at)
      THEN 'check_target_period'
    WHEN result_plan != 'plus' THEN 'review_current_plan'
    WHEN new_expiry <= as_of THEN 'current_plan_expired'
    WHEN new_expiry < old_expiry THEN 'expiry_regressed'
    WHEN new_expiry = old_expiry THEN 'no_extension_observed'
    WHEN new_expiry < target_expires_at THEN 'extension_short'
    ELSE 'target_period_observed'
  END AS next_step
  FROM evidence
)
SELECT order_key, payment_state, delivery_state, renewal_mode,
       evidence_state, next_step
FROM assessed
ORDER BY order_key;
