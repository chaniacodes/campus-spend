
import json
import os
import uuid
from pathlib import Path
from datetime import datetime


DATA_FILE = Path(__file__).parent / "expenses.json"
BUDGETS_FILE = Path(__file__).parent / "budgets.json"



def load_expenses():
    """Load, validate, and migrate saved expense records."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            expenses = json.load(file)

        if not isinstance(expenses, list):
            raise ValueError("Expected a list of expenses.")

        migrated = False

        for expense in expenses:
            if not isinstance(expense, dict):
                raise ValueError("Invalid transaction record.")

            if not isinstance(expense.get("category"), str):
                raise ValueError("Invalid expense category.")

            amount = expense.get("amount")

            if (
                not isinstance(amount, (int, float))
                or isinstance(amount, bool)
                or amount <= 0
            ):
                raise ValueError("Invalid expense amount.")

            if "date" not in expense:
                expense["date"] = None
                migrated = True

            elif expense["date"] is not None:
                try:
                    datetime.strptime(expense["date"], "%Y-%m-%d")
                except (ValueError, TypeError):
                    raise ValueError("Invalid transaction date.")

            if "id" not in expense:
                expense["id"] = uuid.uuid4().hex
                migrated = True

            elif not isinstance(expense["id"], str) or not expense["id"].strip():
                raise ValueError("Invalid transaction ID.")

        # Persist generated IDs so they remain stable after restarting.
        if migrated:
            save_expenses(expenses)

        return expenses

    except (json.JSONDecodeError, ValueError) as error:
        print(f"Error reading expenses: {error}")
        raise SystemExit(1)
    except OSError as error:
        print(f"Error accessing expense storage: {error}")
        raise SystemExit(1)




def save_expenses(expenses):
    """Save expenses safely using a temporary file."""
    temp_file = DATA_FILE.with_name(DATA_FILE.name + ".tmp")

    try:
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(expenses, file, indent=4)
            file.flush()
            os.fsync(file.fileno())

        temp_file.replace(DATA_FILE)

    except OSError:
        try:
            temp_file.unlink(missing_ok=True)
        except OSError:
            pass

        raise


def load_budget_settings():
    """Load saved monthly and category budget settings."""
    if not BUDGETS_FILE.exists():
        return {
            "monthly_budgets": {},
            "category_budgets": {},
        }

    try:
        with BUDGETS_FILE.open("r", encoding="utf-8") as file:
            settings = json.load(file)

        if not isinstance(settings, dict):
            raise ValueError("Budget settings must be a dictionary.")

        monthly = settings.get("monthly_budgets", {})
        categories = settings.get("category_budgets", {})

        if not isinstance(monthly, dict) or not isinstance(categories, dict):
            raise ValueError("Invalid budget settings structure.")

        for month, amount in monthly.items():
            try:
                datetime.strptime(month, "%Y-%m")
            except (ValueError, TypeError):
                raise ValueError("Invalid month in budget settings.")

            if (
                not isinstance(amount, (int, float))
                or isinstance(amount, bool)
                or amount <= 0
            ):
                raise ValueError("Monthly budgets must be positive numbers.")

        for month, category_limits in categories.items():
            try:
                datetime.strptime(month, "%Y-%m")
            except (ValueError, TypeError):
                raise ValueError("Invalid month in category budgets.")

            if not isinstance(category_limits, dict):
                raise ValueError("Invalid category budget structure.")

            for category, amount in category_limits.items():
                if not isinstance(category, str) or not category.strip():
                    raise ValueError("Invalid budget category.")

                if (
                    not isinstance(amount, (int, float))
                    or isinstance(amount, bool)
                    or amount <= 0
                ):
                    raise ValueError(
                        "Category budgets must be positive numbers."
                    )

        return {
            "monthly_budgets": monthly,
            "category_budgets": categories,
        }

    except (json.JSONDecodeError, ValueError) as error:
        print(f"Error reading budget settings: {error}")
        raise SystemExit(1)

    except OSError as error:
        print(f"Error accessing budget settings: {error}")
        raise SystemExit(1)


def save_budget_settings(settings):
    """Save budget settings safely using a temporary file."""
    temp_file = BUDGETS_FILE.with_name(BUDGETS_FILE.name + ".tmp")

    try:
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4)
            file.flush()
            os.fsync(file.fileno())

        temp_file.replace(BUDGETS_FILE)

    except OSError:
        try:
            temp_file.unlink(missing_ok=True)
        except OSError:
            pass

        raise


