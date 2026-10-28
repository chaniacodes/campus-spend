import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from expense_logic import (
    calculate_monthly_totals,
    calculate_category_totals,
    filter_expenses,
    calculate_budget_status,
    calculate_budget_percentage,
    get_top_spending_category,
    generate_monthly_wrapped,
    generate_annual_wrapped,
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
                "id": "test-expense-001",
                "category": "Food",
                "amount": 150.0,
                "date": "2026-10-22",
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "expenses.json"

            with patch.object(storage, "DATA_FILE", test_file):
                storage.save_expenses(sample_expenses)
                loaded_expenses = storage.load_expenses()

        self.assertEqual(loaded_expenses, sample_expenses)

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
            {
                "id": "test-expense-002",
                "category": "Food",
                "amount": 100.0,
                "date": "2026-10-22",
            }
        ]

        updated_expenses = [
            {
                "id": "test-expense-002",
                "category": "Food",
                "amount": 200.0,
                "date": "2026-10-22",
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "expenses.json"
            test_file.write_text(
                __import__("json").dumps(original_expenses),
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
        expenses = [{"category": "Food", "amount": 100.0, "date": "2026-10-22"}]

        with patch("builtins.input", side_effect=["1", "", "200"]):
            with patch.object(main, "save_expenses"):
                edit_expense(expenses)

        self.assertEqual(expenses[0]["amount"], 200.0)
        self.assertEqual(expenses[0]["category"], "Food")

    def test_edit_expense_rejects_invalid_amount(self):
        expenses = [{"category": "Food", "amount": 100.0, "date": "2026-10-22"}]

        with patch("builtins.input", side_effect=["1", "", "abc"]):
            with patch.object(main, "save_expenses") as mock_save:
                edit_expense(expenses)

        self.assertEqual(expenses[0]["amount"], 100.0)
        mock_save.assert_not_called()

    def test_delete_expense_can_be_cancelled(self):
        expenses = [{"category": "Food", "amount": 100.0, "date": "2026-10-22"}]

        with patch("builtins.input", side_effect=["1", "no"]):
            with patch.object(main, "save_expenses") as mock_save:
                delete_expense(expenses)

        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0]["amount"], 100.0)
        mock_save.assert_not_called()

    def test_delete_expense_removes_transaction(self):
        expenses = [{"category": "Food", "amount": 100.0, "date": "2026-10-22"}]

        with patch("builtins.input", side_effect=["1", "yes"]):
            with patch.object(main, "save_expenses"):
                delete_expense(expenses)

        self.assertEqual(expenses, [])

    def test_edit_expense_restores_original_if_save_fails(self):
        expenses = [{"category": "Food", "amount": 100.0, "date": "2026-10-22"}]
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
        expenses = [{"category": "Food", "amount": 100.0, "date": "2026-10-22"}]
        original = expenses[0].copy()

        with patch("builtins.input", side_effect=["1", "yes"]):
            with patch.object(
                main,
                "save_expenses",
                side_effect=OSError("Simulated save failure"),
            ):
                delete_expense(expenses)

        self.assertEqual(expenses, [original])

    def test_legacy_expense_receives_persistent_id(self):
        legacy_expenses = [
            {
                "category": "Food",
                "amount": 100.0,
                "date": "2026-10-22",
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "expenses.json"
            test_file.write_text(
                __import__("json").dumps(legacy_expenses),
                encoding="utf-8",
            )

            with patch.object(storage, "DATA_FILE", test_file):
                loaded_expenses = storage.load_expenses()
                first_id = loaded_expenses[0]["id"]

                self.assertTrue(first_id)

                # Loading again should preserve the generated ID.
                reloaded_expenses = storage.load_expenses()

        self.assertEqual(reloaded_expenses[0]["id"], first_id)
        self.assertEqual(reloaded_expenses[0]["category"], "Food")

    # Expense filtering tests

    def test_filter_by_category(self):
        result = filter_expenses(self.expenses, category="food")

        self.assertEqual(len(result), 2)
        self.assertTrue(all(expense["category"] == "Food" for expense in result))

    def test_filter_by_date_range(self):
        result = filter_expenses(
            self.expenses,
            start_date="2026-10-01",
            end_date="2026-10-31",
        )

        self.assertEqual(len(result), 2)

    def test_filter_by_category_and_date_range(self):
        result = filter_expenses(
            self.expenses,
            category="Food",
            start_date="2026-10-01",
            end_date="2026-10-31",
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["amount"], 120.0)

    def test_filter_returns_empty_list_when_no_matches(self):
        result = filter_expenses(self.expenses, category="Shopping")

        self.assertEqual(result, [])

    # Budget settings storage tests

    def test_budget_settings_default_when_file_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "budgets.json"

            with patch.object(storage, "BUDGETS_FILE", test_file):
                settings = storage.load_budget_settings()

        self.assertEqual(
            settings,
            {
                "monthly_budgets": {},
                "category_budgets": {},
            },
        )

    def test_budget_settings_save_and_load(self):
        sample_settings = {
            "monthly_budgets": {"2026-10": 8000.0},
            "category_budgets": {"2026-10": {"Food": 2500.0, "Transport": 1000.0}},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "budgets.json"

            with patch.object(storage, "BUDGETS_FILE", test_file):
                storage.save_budget_settings(sample_settings)
                loaded_settings = storage.load_budget_settings()

        self.assertEqual(loaded_settings, sample_settings)

    def test_invalid_monthly_budget_is_rejected(self):
        invalid_settings = {
            "monthly_budgets": {"2026-10": -500.0},
            "category_budgets": {},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "budgets.json"
            test_file.write_text(
                __import__("json").dumps(invalid_settings),
                encoding="utf-8",
            )

            with patch.object(storage, "BUDGETS_FILE", test_file):
                with self.assertRaises(SystemExit):
                    storage.load_budget_settings()

    # Budget calculation tests

    def test_budget_status_calculates_remaining_amounts(self):
        expenses = [
            {"category": "Food", "amount": 1800.0, "date": "2026-10-02"},
            {"category": "Transport", "amount": 500.0, "date": "2026-10-05"},
        ]

        result = calculate_budget_status(
            expenses,
            "2026-10",
            8000.0,
            {"Food": 2500.0, "Transport": 1000.0},
        )

        self.assertEqual(result["total_spent"], 2300.0)
        self.assertEqual(result["remaining"], 5700.0)
        self.assertEqual(result["over_budget"], 0.0)
        self.assertEqual(result["categories"]["Food"]["remaining"], 700.0)
        self.assertEqual(result["categories"]["Transport"]["remaining"], 500.0)

    def test_budget_status_detects_overspending(self):
        expenses = [
            {"category": "Food", "amount": 3000.0, "date": "2026-10-02"},
        ]

        result = calculate_budget_status(
            expenses,
            "2026-10",
            2500.0,
            {"Food": 2000.0},
        )

        self.assertEqual(result["over_budget"], 500.0)
        self.assertEqual(result["categories"]["Food"]["over_budget"], 1000.0)
        self.assertEqual(result["categories"]["Food"]["remaining"], -1000.0)

    def test_budget_status_ignores_other_months(self):
        expenses = [
            {"category": "Food", "amount": 500.0, "date": "2026-09-20"},
            {"category": "Food", "amount": 200.0, "date": "2026-10-02"},
        ]

        result = calculate_budget_status(
            expenses,
            "2026-10",
            1000.0,
            {"Food": 500.0},
        )

        self.assertEqual(result["total_spent"], 200.0)
        self.assertEqual(result["categories"]["Food"]["remaining"], 300.0)

    def test_manage_budgets_saves_monthly_and_category_budgets(self):
        initial_settings = {
            "monthly_budgets": {},
            "category_budgets": {},
        }

        user_inputs = [
            "2026-10",
            "8000",
            "Food",
            "2500",
            "",
        ]

        with patch.object(
            main, "load_budget_settings", return_value=initial_settings
        ), patch.object(main, "save_budget_settings") as mock_save, patch(
            "builtins.input", side_effect=user_inputs
        ):
            main.manage_budgets([])

        saved_settings = mock_save.call_args[0][0]

        self.assertEqual(saved_settings["monthly_budgets"]["2026-10"], 8000.0)
        self.assertEqual(saved_settings["category_budgets"]["2026-10"]["Food"], 2500.0)

    def test_manage_budgets_rejects_invalid_month(self):
        with patch.object(
            main,
            "load_budget_settings",
            return_value={
                "monthly_budgets": {},
                "category_budgets": {},
            },
        ), patch.object(main, "save_budget_settings") as mock_save, patch(
            "builtins.input", return_value="2026-13"
        ):
            main.manage_budgets([])

        mock_save.assert_not_called()

    def test_manage_budgets_rejects_invalid_monthly_budget(self):
        user_inputs = ["2026-10", "abc"]

        with patch.object(
            main,
            "load_budget_settings",
            return_value={
                "monthly_budgets": {},
                "category_budgets": {},
            },
        ), patch.object(main, "save_budget_settings") as mock_save, patch(
            "builtins.input", side_effect=user_inputs
        ):
            main.manage_budgets([])

        mock_save.assert_not_called()

    def test_budget_percentage(self):
        self.assertEqual(
            calculate_budget_percentage(2000, 5000),
            40.0,
        )

    def test_budget_percentage_when_overspent(self):
        self.assertEqual(
            calculate_budget_percentage(6000, 5000),
            120.0,
        )

    def test_budget_percentage_when_budget_is_zero(self):
        self.assertEqual(
            calculate_budget_percentage(2000, 0),
            0.0,
        )

    def test_get_top_spending_category(self):
        expenses = [
            {"category": "Food", "amount": 1800.0, "date": "2026-10-02"},
            {"category": "Transport", "amount": 500.0, "date": "2026-10-05"},
            {"category": "Shopping", "amount": 900.0, "date": "2026-10-10"},
        ]

        result = get_top_spending_category(expenses, "2026-10")

        self.assertEqual(result, ("Food", 1800.0))

    def test_get_top_spending_category_ignores_other_months(self):
        expenses = [
            {"category": "Food", "amount": 500.0, "date": "2026-09-20"},
            {"category": "Transport", "amount": 300.0, "date": "2026-10-05"},
        ]

        result = get_top_spending_category(expenses, "2026-10")

        self.assertEqual(result, ("Transport", 300.0))

    def test_get_top_spending_category_when_no_expenses(self):
        result = get_top_spending_category([], "2026-10")

        self.assertEqual(result, (None, 0.0))

    def test_monthly_wrapped_returns_correct_summary(self):
        expenses = [
            {"category": "Food", "amount": 120.0, "date": "2026-10-02"},
            {"category": "Transport", "amount": 50.0, "date": "2026-10-05"},
            {"category": "Food", "amount": 200.0, "date": "2026-09-20"},
        ]

        result = generate_monthly_wrapped(expenses, "2026-10", 5000.0)

        self.assertEqual(result["month"], "2026-10")
        self.assertEqual(result["total_spent"], 170.0)
        self.assertEqual(result["top_category"], "Food")
        self.assertEqual(result["top_amount"], 120.0)
        self.assertAlmostEqual(result["budget_percentage"], 3.4)
        self.assertEqual(
            result["category_totals"],
            {"Food": 120.0, "Transport": 50.0},
        )

    def test_monthly_wrapped_handles_empty_month(self):
        expenses = [
            {"category": "Food", "amount": 120.0, "date": "2026-09-20"},
        ]

        result = generate_monthly_wrapped(expenses, "2026-10", 5000.0)

        self.assertEqual(result["total_spent"], 0)
        self.assertIsNone(result["top_category"])
        self.assertEqual(result["top_amount"], 0.0)
        self.assertEqual(result["budget_percentage"], 0.0)
        self.assertEqual(result["category_totals"], {})

    def test_monthly_wrapped_handles_zero_budget(self):
        result = generate_monthly_wrapped(
            [{"category": "Food", "amount": 100.0, "date": "2026-10-02"}],
            "2026-10",
            0,
        )

        self.assertEqual(result["budget_percentage"], 0.0)

    def test_annual_wrapped_calculates_totals(self):
        expenses = [
            {"category": "Food", "amount": 120.0, "date": "2026-10-02"},
            {"category": "Transport", "amount": 50.0, "date": "2026-10-05"},
            {"category": "Food", "amount": 200.0, "date": "2026-09-20"},
            {"category": "Books", "amount": 300.0, "date": "2025-12-10"},
        ]

        result = generate_annual_wrapped(expenses, "2026")

        self.assertEqual(result["total_spent"], 370.0)
        self.assertEqual(result["top_category"], "Food")
        self.assertEqual(result["top_amount"], 320.0)
        self.assertEqual(result["highest_month"], "2026-09")
        self.assertEqual(result["highest_month_amount"], 200.0)
        self.assertEqual(
            result["monthly_totals"],
            {
                "2026-10": 170.0,
                "2026-09": 200.0,
            },
        )
        self.assertEqual(result["average_monthly_spending"], 185.0)

    def test_annual_wrapped_handles_empty_year(self):
        expenses = [
            {"category": "Food", "amount": 120.0, "date": "2025-10-02"},
        ]

        result = generate_annual_wrapped(expenses, "2026")

        self.assertEqual(result["total_spent"], 0)
        self.assertIsNone(result["top_category"])
        self.assertIsNone(result["highest_month"])
        self.assertEqual(result["category_totals"], {})
        self.assertEqual(result["monthly_totals"], {})
        self.assertEqual(result["average_monthly_spending"], 0.0)

    def test_annual_wrapped_excludes_unknown_dates(self):
        expenses = [
            {"category": "Food", "amount": 100.0, "date": None},
            {"category": "Food", "amount": 150.0, "date": "2026-01-10"},
        ]

        result = generate_annual_wrapped(expenses, "2026")

        self.assertEqual(result["total_spent"], 150.0)

    def test_create_expense(self):
        from expense_logic import create_expense

        expense = create_expense(50, "Food", "2026-10-23", "Lunch")

        self.assertEqual(expense["amount"], 50.0)
        self.assertEqual(expense["category"], "Food")
        self.assertEqual(expense["date"], "2026-10-23")
        self.assertEqual(expense["description"], "Lunch")
        self.assertTrue(expense["id"])

    def test_create_expense_rejects_zero_amount(self):
        from expense_logic import create_expense

        with self.assertRaises(ValueError):
            create_expense(0, "Food", "2026-10-23")

    def test_create_expense_rejects_empty_category(self):
        from expense_logic import create_expense

        with self.assertRaises(ValueError):
            create_expense(50, "  ", "2026-10-23")

    def test_create_expense_rejects_negative_amount(self):
        from expense_logic import create_expense

        with self.assertRaises(ValueError):
            create_expense(-50, "Food", "2026-10-23")

    def test_create_expense_rejects_boolean_amount(self):
        from expense_logic import create_expense

        with self.assertRaises(ValueError):
            create_expense(True, "Food", "2026-10-23")

    def test_create_expense_rejects_invalid_date(self):
        from expense_logic import create_expense

        with self.assertRaises(ValueError):
            create_expense(50, "Food", "2026-02-30")


if __name__ == "__main__":
    unittest.main()
