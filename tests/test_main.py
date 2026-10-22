
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import storage

import main
from main import (
    add_expense,
    get_month_expenses,
    load_expenses,
    save_expenses,
    MONTHLY_BUDGET,
)


class TestCampusSpend(unittest.TestCase):

    def setUp(self):
        self.expenses = [
            {"category": "Food", "amount": 120.0, "date": "2026-10-02"},
            {"category": "Transport", "amount": 50.0, "date": "2026-10-05"},
            {"category": "Food", "amount": 200.0, "date": "2026-09-20"},
        ]

    # Monthly expense filtering tests

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

    # Budget test

    def test_monthly_budget_constant(self):
        self.assertEqual(MONTHLY_BUDGET, 5000.0)

    # Expense validation tests

    @patch("builtins.input", side_effect=["", "250"])
    def test_empty_category_is_rejected(self, mock_input):
        add_expense(self.expenses)

        self.assertEqual(len(self.expenses), 3)

    @patch("builtins.input", side_effect=["Food", "abc"])
    def test_non_numeric_amount_is_rejected(self, mock_input):
        add_expense(self.expenses)

        self.assertEqual(len(self.expenses), 3)

    @patch("builtins.input", side_effect=["Food", "-100"])
    def test_negative_amount_is_rejected(self, mock_input):
        add_expense(self.expenses)

        self.assertEqual(len(self.expenses), 3)

    # Saving and loading tests

    def test_save_and_load_expenses(self):
        sample_expenses = [
            {
                "category": "Food",
                "amount": 150.0,
                "date": "2026-10-22",
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test_expenses.json"

            with patch.object(storage, "DATA_FILE", test_file):
                save_expenses(sample_expenses)
                loaded_expenses = load_expenses()

        self.assertEqual(loaded_expenses, sample_expenses)

    def test_load_expenses_returns_empty_list_when_file_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "missing.json"

            with patch.object(storage, "DATA_FILE", test_file):
                loaded_expenses = load_expenses()

        self.assertEqual(loaded_expenses, [])

    # Legacy transaction test

    def test_legacy_expense_without_date_is_preserved(self):
        legacy_expense = {
            "category": "Food",
            "amount": 100.0,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "legacy.json"

            with patch.object(storage, "DATA_FILE", test_file):
                save_expenses([legacy_expense])
                loaded_expenses = load_expenses()

        self.assertIsNone(loaded_expenses[0]["date"])
        self.assertEqual(loaded_expenses[0]["amount"], 100.0)


if __name__ == "__main__":
    unittest.main()
