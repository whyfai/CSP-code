import unittest

from impact_model import calculate_impacts


class TestCalculateImpacts(unittest.TestCase):
    def test_impacts_return_expected_categories(self) -> None:
        impacts = calculate_impacts(100)

        self.assertEqual(
            set(impacts),
            {
                "Crude Oil",
                "Transportation",
                "Food Cost",
                "Annual Expenditure",
                "Healthcare",
            },
        )
        self.assertEqual(impacts["Crude Oil"], 100)
        for key, value in impacts.items():
            self.assertIsInstance(value, float)

    def test_impacts_increase_with_crude_price(self) -> None:
        lower = calculate_impacts(50)
        higher = calculate_impacts(150)

        self.assertEqual(lower["Crude Oil"], 50)
        self.assertEqual(higher["Crude Oil"], 150)

        for key in ("Transportation", "Food Cost", "Annual Expenditure", "Healthcare"):
            self.assertGreater(higher[key], lower[key])


if __name__ == "__main__":
    unittest.main()
