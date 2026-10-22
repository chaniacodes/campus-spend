
import unittest
from datetime import date

from main import get_month_expenses, show_summary, MONTHLY_BUDGET


class TestCampusSpend(unittest.TestCase):

    def setUp(self):
        self.expenses = [
            {"category": "Food", "amount": 120.0, "date": "2026-10-02"},
            {"category": "Transport", "amount": 50.0, "date": "2026-10-05"},
            {"category": "Food", "amount": 200.0, "date": "2026-09-20"},
        ]

    def test_month_filter_returns_correct_expenses(self):
        result = get_month_expenses(self.expenses, "2026-10")

        self.assertEqual(len(result), 2)

    def test_month_filter_excludes_other_months(self):
        result = get_month_expenses(self.expenses, "2026-10")

        self.assertTrue(
            all(expense["date"].startswith("2026-10") for expense in result)
        )

    def test_month_filter_returns_empty_list_when_no_matches(self):
        result = get_month_expenses(self.expenses, "2026-08")

        self.assertEqual(result, [])

    def test_monthly_budget_constant(self):
        self.assertEqual(MONTHLY_BUDGET, 5000.0)


if __name__ == "__main__":
    unittest.main()
