-- Constructed data; all timestamps use the same Beijing wall-clock format.
WITH
params(as_of) AS (VALUES ('2026-09-08 12:00:00')),
orders(order_key, target_account, payment_state, delivery_state, paid_at) AS (
  VALUES
  ('O01', 'A01', 'pending',  'none',       NULL),
  ('O02', 'A02', 'paid',     'processing', '2026-09-08 11:20:00'),
  ('O03', 'A03', 'paid',     'completed',  '2026-09-08 11:20:00'),
  ('O04', 'A04', 'paid',     'completed',  '2026-09-08 11:20:00'),
  ('O05', 'A05', 'paid',     'completed',  '2026-09-08 11:20:00'),
  ('O06', 'A06', 'paid',     'completed',  '2026-09-08 11:20:00'),
  ('O07', 'A07', 'refunded', 'completed',  '2026-09-08 11:20:00'),
  ('O08', 'A08', 'paid',     'completed',  '2026-09-08 11:20:00'),
  ('O09', 'A09', 'paid',     'completed',  '2026-09-08 11:20:00')
),
evidence(evidence_id, order_key, account_key, plan_name, observed_at) AS (
  VALUES
  (1, 'O04', 'A04', 'plus', '2026-09-08 11:50:00'),
  (2, 'O04', 'A04', 'free', '2026-09-08 11:10:00'),
  (3, 'O05', 'A05', 'plus', '2026-09-08 11:25:00'),
  (4, 'O06', 'B06', 'plus', '2026-09-08 11:55:00'),
  (5, 'O07', 'A07', 'plus', '2026-09-08 11:55:00'),
  (6, 'O08', 'A08', 'free', '2026-09-08 11:55:00'),
  (7, 'O09', 'A09', 'plus', '2026-09-08 12:05:00')
),
ranked AS (
  SELECT e.*, ROW_NUMBER() OVER (
    PARTITION BY order_key
    ORDER BY julianday(observed_at) DESC, evidence_id DESC
  ) AS rn
  FROM evidence AS e
),
checked AS (
  SELECT o.*, p.as_of,
    CASE
      WHEN e.evidence_id IS NULL THEN 'no_record'
      WHEN o.target_account IS NULL OR trim(o.target_account) = ''
        OR e.account_key IS NULL OR trim(e.account_key) = ''
        OR e.account_key <> o.target_account
        THEN 'account_mismatch'
      WHEN julianday(e.observed_at) IS NULL
        OR julianday(e.observed_at) > julianday(p.as_of)
        THEN 'invalid_time'
      WHEN julianday(o.paid_at) IS NULL THEN 'payment_time_unknown'
      WHEN julianday(e.observed_at) < julianday(o.paid_at)
        OR julianday(e.observed_at) < julianday(p.as_of, '-30 minutes')
        THEN 'stale'
      WHEN e.plan_name = 'plus' THEN 'recent_plus'
      WHEN e.plan_name IS NULL OR trim(e.plan_name) = '' THEN 'unknown_plan'
      ELSE 'recent_other_plan'
    END AS evidence_state
  FROM orders AS o CROSS JOIN params AS p
  LEFT JOIN ranked AS e ON e.order_key = o.order_key AND e.rn = 1
)
SELECT order_key, payment_state, delivery_state, evidence_state,
  CASE
    WHEN payment_state = 'refunded' THEN 'refund_review'
    WHEN payment_state IS NULL OR payment_state <> 'paid' THEN 'confirm_payment'
    WHEN julianday(paid_at) IS NULL OR julianday(paid_at) > julianday(as_of)
      THEN 'check_payment_time'
    WHEN evidence_state = 'recent_plus' THEN 'plus_observed'
    WHEN evidence_state <> 'no_record' THEN 'review_evidence'
    WHEN delivery_state = 'processing' THEN 'processing'
    ELSE 'verify_plan'
  END AS next_step
FROM checked
ORDER BY order_key;
