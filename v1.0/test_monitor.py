#!/usr/bin/env python3
"""Unit tests for the weekly pullback monitor core logic."""

import datetime as dt
import unittest

import monitor


def weekly_from_closes(closes):
    start = dt.date(2024, 1, 1)
    weekly = []
    for index, close in enumerate(closes):
        weekly.append(
            {
                "date": start + dt.timedelta(days=index * 7),
                "week_start": start + dt.timedelta(days=index * 7),
                "open": close,
                "high": close * 1.03,
                "low": close * 0.97,
                "close": close,
                "volume": 1000,
            }
        )
    monitor.add_indicators(weekly)
    return weekly


class MonitorLogicTest(unittest.TestCase):
    def test_add_indicators_calculates_weekly_moving_average(self):
        weekly = weekly_from_closes(range(1, 31))
        self.assertAlmostEqual(weekly[-1]["ma5"], 28.0)
        self.assertAlmostEqual(weekly[-1]["ma10"], 25.5)
        self.assertAlmostEqual(weekly[-1]["ma20"], 20.5)

    def test_recent_cross_age_detects_bullish_cross(self):
        closes = [30 - i * 0.4 for i in range(30)] + [18 + i * 1.4 for i in range(12)]
        weekly = weekly_from_closes(closes)
        age = monitor.recent_cross_age(weekly, 5, 10, max_weeks=8)
        self.assertIsNotNone(age)
        self.assertLessEqual(age, 8)

    def test_context_only_excludes_index_and_leveraged_products(self):
        self.assertTrue(monitor.is_non_stock_context({"assetclass": "index"}))
        self.assertTrue(monitor.is_non_stock_context({"role": "leveraged"}))
        self.assertFalse(monitor.is_non_stock_context({"assetclass": "stocks", "role": "core"}))

    def test_auto_provider_uses_futu_then_nasdaq_for_us_symbols(self):
        item = {"symbol": "GOOG", "assetclass": "stocks"}
        self.assertEqual(monitor.provider_order("auto", item), ["futu", "nasdaq"])

    def test_auto_provider_does_not_use_nasdaq_for_non_us_symbols(self):
        item = {"symbol": "09888", "futu_code": "HK.09888", "assetclass": "stocks"}
        self.assertEqual(monitor.provider_order("auto", item), ["futu"])

    def test_dedupe_suppresses_same_signal_within_five_business_days(self):
        state = {"alerts": {}}
        result = {
            "symbol": "GOOG",
            "latest_date": "2026-05-08",
            "grade": "B",
            "close": 100.0,
            "signals": [{"kind": "pure_pullback", "ma": 20, "distance": 0.02, "support": 98.0}],
        }
        monitor.apply_dedupe([result], state)
        repeated = {
            "symbol": "GOOG",
            "latest_date": "2026-05-11",
            "grade": "B",
            "close": 101.0,
            "signals": [{"kind": "pure_pullback", "ma": 20, "distance": 0.019, "support": 99.0}],
        }
        monitor.apply_dedupe([repeated], state)
        self.assertTrue(repeated["suppressed"])

    def test_dedupe_allows_grade_improvement(self):
        state = {"alerts": {}}
        first = {
            "symbol": "AGRO",
            "latest_date": "2026-05-08",
            "grade": "C",
            "close": 10.0,
            "signals": [{"kind": "pure_pullback", "ma": 10, "distance": 0.03, "support": 9.8}],
        }
        improved = {
            "symbol": "AGRO",
            "latest_date": "2026-05-11",
            "grade": "B",
            "close": 10.1,
            "signals": [{"kind": "pure_pullback", "ma": 10, "distance": 0.03, "support": 9.9}],
        }
        monitor.apply_dedupe([first], state)
        monitor.apply_dedupe([improved], state)
        self.assertFalse(improved["suppressed"])


if __name__ == "__main__":
    unittest.main()
