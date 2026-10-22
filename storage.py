
import json
from pathlib import Path
from datetime import datetime


DATA_FILE = Path(__file__).parent / "expenses.json"


def load_expenses():
    """Load expenses and validate the saved transaction records."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            expenses = json.load(file)

        if not isinstance(expenses, list):
            raise ValueError("Expected a list of expenses.")

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

            elif expense["date"] is not None:
                try:
                    datetime.strptime(expense["date"], "%Y-%m-%d")
                except (ValueError, TypeError):
                    raise ValueError("Invalid transaction date.")

        return expenses

    except (json.JSONDecodeError, ValueError) as error:
        print(f"Error reading expenses: {error}")
        raise SystemExit(1)


def save_expenses(expenses):
    """Save expenses to the JSON file."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=4)
