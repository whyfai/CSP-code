import unittest

from impact_model import calculate_impacts


class TestCalculateImpacts(unittest.TestCase):
    def test_impacts_scale_from_crude_price(self) -> None:
        impacts = calculate_impacts(100)
        self.assertEqual(impacts["Crude Oil"], 100)
        self.assertAlmostEqual(impacts["Transportation"], 32)
        self.assertAlmostEqual(impacts["Food Logistics"], 14.4)
        self.assertAlmostEqual(impacts["Flight Tickets"], 40.0)
        self.assertAlmostEqual(impacts["Household Energy"], 28)


    def test_impacts_scale_for_multiple_prices(self) -> None:
        for crude in (50, 150):
            impacts = calculate_impacts(crude)
            self.assertEqual(impacts["Crude Oil"], crude)
            self.assertAlmostEqual(impacts["Transportation"], crude * 0.32)
            self.assertAlmostEqual(impacts["Food Logistics"], crude * 0.32 * 0.45)
            self.assertAlmostEqual(impacts["Flight Tickets"], crude * 0.32 * 1.25)
            self.assertAlmostEqual(impacts["Household Energy"], crude * 0.28)

    def test_zero_crude_price_returns_zeroed_impacts(self) -> None:
        impacts = calculate_impacts(0)
        for value in impacts.values():
            self.assertEqual(value, 0)


if __name__ == "__main__":
    unittest.main()
