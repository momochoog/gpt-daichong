"""Boundary tests use invented records only; Python standard library."""

import contextlib
import io
import unittest
from datetime import datetime

from usage_windows import (DEFAULT_AS_OF, MAX_UNIX_SECONDS, classify_many,
                           classify_window, main, parse_as_of, synthetic_cases)


class UsageWindowsTests(unittest.TestCase):
    def setUp(self):
        self.as_of = parse_as_of(DEFAULT_AS_OF)
        self.now = int(self.as_of.timestamp())

    def record(self, used=40, reset=None):
        return dict(name="demo", usedPercent=used,
                    resetsAt=self.now + 1 if reset is None else reset)

    def check(self, record):
        return classify_window(record, self.as_of)

    def test_zero_and_fractions_are_not_missing(self):
        for used in (0, 0.0, 0.25, 50, 99.9):
            with self.subTest(used=used):
                result = self.check(self.record(used))
                self.assertEqual(result["status"], "当前未用完")
                self.assertAlmostEqual(result["remainingPercent"], 100 - used)

    def test_hundred_is_exhausted(self):
        for used in (100, 100.0):
            with self.subTest(used=used):
                result = self.check(self.record(used))
                self.assertEqual(result["status"], "已用完")
                self.assertEqual(result["remainingPercent"], 0)

    def test_invalid_percent(self):
        for used in (float("nan"), float("inf"), -float("inf"), True, False,
                     "0", "100", "", -1, -0.01, 100.01, 101, [], {}, 10**1000):
            with self.subTest(used=used):
                result = self.check(self.record(used))
                self.assertEqual(result["status"], "数据异常")
                self.assertIsNone(result["remainingPercent"])

    def test_missing_is_not_zero(self):
        for key in ("usedPercent", "resetsAt", "name"):
            for remove in (False, True):
                with self.subTest(key=key, remove=remove):
                    record = self.record()
                    if remove:
                        del record[key]
                    else:
                        record[key] = None
                    self.assertEqual(self.check(record)["status"], "信息缺失")
                    self.assertIsNone(self.check(record)["remainingPercent"])

    def test_missing_reset_is_not_epoch(self):
        self.assertIsNone(self.check(dict(name="demo", usedPercent=0))["resetsAtBeijing"])

    def test_invalid_reset_including_milliseconds(self):
        for reset in (True, False, "1799391600", self.now + 0.5, 0, -1,
                      float("nan"), float("inf"), self.now * 1000,
                      MAX_UNIX_SECONDS + 1, 10**1000, [], {}):
            with self.subTest(reset=reset):
                self.assertEqual(self.check(self.record(reset=reset))["status"], "数据异常")

    def test_reset_boundaries_never_imply_recovery(self):
        for used in (0, 40, 100):
            for offset in (-1, 0):
                with self.subTest(used=used, offset=offset):
                    result = self.check(self.record(used, self.now + offset))
                    self.assertEqual(result["status"], "到重置时间，需刷新")
                    self.assertIsNone(result["remainingPercent"])
        self.assertEqual(self.check(self.record(reset=self.now + 1))["status"], "当前未用完")

    def test_valid_timestamp_input_extremes(self):
        self.assertEqual(self.check(self.record(reset=1))["status"], "到重置时间，需刷新")
        self.assertEqual(self.check(self.record(reset=MAX_UNIX_SECONDS))["status"], "当前未用完")

    def test_invalid_data_takes_priority_over_missing(self):
        self.assertEqual(self.check(dict(name="demo", usedPercent=False))["status"], "数据异常")

    def test_timezone_conversion_and_equivalent_instants(self):
        result = self.check(self.record(reset=self.now + 3600))
        self.assertEqual(result["resetsAtBeijing"], "2026-09-11T16:00:00+08:00")
        for value in ("2026-09-11T07:00:00Z", "2026-09-11T02:00:00-05:00"):
            with self.subTest(value=value):
                self.assertEqual(parse_as_of(value), self.as_of)

    def test_naive_and_invalid_as_of_rejected(self):
        for value in ("2026-09-11", "2026-09-11T15:00:00", "not-a-time"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_as_of(value)
        with self.assertRaises(ValueError):
            classify_window(self.record(), datetime(2026, 9, 11))

    def test_multi_window_cases_remain_independent(self):
        expected = [["已用完", "当前未用完"], ["当前未用完", "已用完"],
                    ["到重置时间，需刷新", "信息缺失", "数据异常"]]
        for records, states in zip(synthetic_cases().values(), expected):
            with self.subTest(states=states):
                results = classify_many(records, self.as_of)
                self.assertEqual([result["status"] for result in results], states)
                self.assertEqual(len(results), len(records))

    def test_bad_container_and_record_shapes(self):
        for records in ([], {}, None, "[]"):
            with self.subTest(records=records), self.assertRaises(ValueError):
                classify_many(records, self.as_of)
        for record in (None, [], "bad"):
            with self.subTest(record=record):
                self.assertEqual(self.check(record)["status"], "数据异常")

    def test_cli_demo_and_manual_record(self):
        for args in ([], ["--as-of", DEFAULT_AS_OF, "--records",
                          '[{"name":"demo","usedPercent":0,"resetsAt":1799395200}]']):
            with self.subTest(args=args), contextlib.redirect_stdout(io.StringIO()) as output:
                main(args)
                self.assertIn("+08:00", output.getvalue())
                self.assertIn("当前未用完", output.getvalue())

    def test_cli_bad_json_and_timezone_exit_two(self):
        for args in (["--records", "{"], ["--records", "{}"],
                     ["--as-of", "2026-09-11T15:00:00"]):
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    main(args)
                self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
