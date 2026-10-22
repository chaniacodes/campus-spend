
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from expense_logic import (
    calculate_monthly_totals,
    calculate_category_totals,
)
import storage

import main
from main import (
    add_expense,
    get_month_expenses,
    load_expenses,
    save_expenses,
    edit_expense,
    delete_expense,
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

    def test_calculate_monthly_totals(self):
        expenses = [
            {"category": "Food", "amount": 120.0, "date": "2026-10-02"},
            {"category": "Transport", "amount": 80.0, "date": "2026-10-03"},
            {"category": "Food", "amount": 50.0, "date": "2026-09-20"},
        ]

        totals = calculate_monthly_totals(expenses, "2026-10")

        self.assertEqual(totals["budget"], 5000.0)
        self.assertEqual(totals["total"], 200.0)
        self.assertEqual(totals["remaining"], 4800.0)
        self.assertEqual(totals["over_budget"], 0)

    def test_calculate_category_totals(self):
        expenses = [
            {"category": "Food", "amount": 120.0, "date": "2026-10-02"},
            {"category": "Transport", "amount": 80.0, "date": "2026-10-03"},
            {"category": "Food", "amount": 50.0, "date": "2026-10-04"},
            {"category": "Food", "amount": 40.0, "date": "2026-09-20"},
        ]

        totals = calculate_category_totals(expenses, "2026-10")

        self.assertEqual(totals["Food"], 170.0)
        self.assertEqual(totals["Transport"], 80.0)
        self.assertEqual(sum(totals.values()), 250.0)

    
    def test_failed_replacement_preserves_original_file(self):
        original_expenses = [
            {"category": "Food", "amount": 100.0, "date": "2026-10-22"}
        ]
        updated_expenses = [
            {"category": "Food", "amount": 200.0, "date": "2026-10-22"}
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "expenses.json"
            test_file.write_text(
                '[{"category": "Food", "amount": 100.0, "date": "2026-10-22"}]',
                encoding="utf-8",
            )

            with patch.object(storage, "DATA_FILE", test_file):
                with patch.object(
                    Path,
                    "replace",
                    side_effect=OSError("Simulated replacement failure"),
                ):
                    with self.assertRaises(OSError):
                        storage.save_expenses(updated_expenses)

                saved_data = storage.load_expenses()

                self.assertEqual(saved_data, original_expenses)

    
    def test_edit_expense_updates_amount(self):
        expenses = [
            {"category": "Food", "amount": 100.0, "date": "2026-10-22"}
        ]

        with patch("builtins.input", side_effect=["1", "", "200"]):
            with patch.object(main, "save_expenses"):
                edit_expense(expenses)

        self.assertEqual(expenses[0]["amount"], 200.0)
        self.assertEqual(expenses[0]["category"], "Food")

    def test_edit_expense_rejects_invalid_amount(self):
        expenses = [
            {"category": "Food", "amount": 100.0, "date": "2026-10-22"}
        ]

        with patch("builtins.input", side_effect=["1", "", "abc"]):
            with patch.object(main, "save_expenses") as mock_save:
                edit_expense(expenses)

        self.assertEqual(expenses[0]["amount"], 100.0)
        mock_save.assert_not_called()

    def test_delete_expense_can_be_cancelled(self):
        expenses = [
            {"category": "Food", "amount": 100.0, "date": "2026-10-22"}
        ]

        with patch("builtins.input", side_effect=["1", "no"]):
            with patch.object(main, "save_expenses") as mock_save:
                delete_expense(expenses)

        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0]["amount"], 100.0)
        mock_save.assert_not_called()

    def test_delete_expense_removes_transaction(self):
        expenses = [
            {"category": "Food", "amount": 100.0, "date": "2026-10-22"}
        ]

        with patch("builtins.input", side_effect=["1", "yes"]):
            with patch.object(main, "save_expenses"):
                delete_expense(expenses)

        self.assertEqual(expenses, [])

    
    def test_edit_expense_restores_original_if_save_fails(self):
        expenses = [
            {"category": "Food", "amount": 100.0, "date": "2026-10-22"}
        ]
        original = expenses[0].copy()

        with patch("builtins.input", side_effect=["1", "", "200"]):
            with patch.object(
                main,
                "save_expenses",
                side_effect=OSError("Simulated save failure"),
            ):
                edit_expense(expenses)

        self.assertEqual(expenses[0], original)

    def test_delete_expense_restores_transaction_if_save_fails(self):
        expenses = [
            {"category": "Food", "amount": 100.0, "date": "2026-10-22"}
        ]
        original = expenses[0].copy()

        with patch("builtins.input", side_effect=["1", "yes"]):
            with patch.object(
                main,
                "save_expenses",
                side_effect=OSError("Simulated save failure"),
            ):
                delete_expense(expenses)

        self.assertEqual(expenses, [original])




if __name__ == "__main__":
    unittest.main()
