
import json
import os
import uuid
from pathlib import Path
from datetime import datetime


DATA_FILE = Path(__file__).parent / "expenses.json"



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

