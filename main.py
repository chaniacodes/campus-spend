
import json
from pathlib import Path
from datetime import date, datetime

DATA_FILE = Path(__file__).parent / "expenses.json"
MONTHLY_BUDGET = 5000.0



def load_expenses():
    """Load saved expenses without inventing dates for older records."""
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

            if (
                not isinstance(expense.get("amount"), (int, float))
                or isinstance(expense.get("amount"), bool)
                or expense["amount"] <= 0
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


def add_expense(expenses):
    """Add a new expense with today's date."""
    category = input("Enter expense category: ").strip().title()

    if not category:
        print("Category cannot be empty.")
        return

    try:
        amount = float(input("Enter expense amount (₹): "))

        if amount <= 0:
            print("Amount must be greater than zero.")
            return

    except ValueError:
        print("Please enter a valid number.")
        return

    transaction = {
        "category": category,
        "amount": amount,
        "date": date.today().isoformat()
    }

    expenses.append(transaction)

    try:
        save_expenses(expenses)
        print("Expense saved successfully!")

    except OSError as error:
        expenses.pop()
        print(f"Could not save expense: {error}")


def view_expenses(expenses):
    """Display all transactions."""
    print("\n===== Transaction History =====")

    if not expenses:
        print("No expenses recorded yet.")
        return

    for index, expense in enumerate(expenses, start=1):
        print(
            f"{index}. {expense.get('date') or 'Unknown date'} | "          
            f"{expense['category']} | "
            f"₹{expense['amount']:.2f}"
        )


def get_month_expenses(expenses, month):
    """Return dated transactions for a month in YYYY-MM format."""
    return [
        expense for expense in expenses
        if isinstance(expense.get("date"), str)
        and expense["date"].startswith(month)
    ]


def view_monthly_expenses(expenses):
    """Display transactions for a selected month."""
    month = input("Enter month (YYYY-MM, e.g. 2026-10): ").strip()

    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid month. Use YYYY-MM, for example 2026-10.")
        return

    monthly_expenses = get_month_expenses(expenses, month)

    print(f"\n===== Expenses for {month} =====")

    if not monthly_expenses:
        print("No expenses recorded for this month.")
        return

    for index, expense in enumerate(monthly_expenses, start=1):
        print(
            f"{index}. {expense.get('date') or 'Unknown date'} | "
            f"{expense['category']} | "
            f"₹{expense['amount']:.2f}"
        )


def show_summary(expenses):
    """Display the budget summary for the current month."""
    current_month = date.today().strftime("%Y-%m")
    monthly_expenses = get_month_expenses(expenses, current_month)

    total = sum(expense["amount"] for expense in monthly_expenses)
    remaining = MONTHLY_BUDGET - total

    print(f"\n===== Budget Summary: {current_month} =====")
    print(f"Monthly budget:   ₹{MONTHLY_BUDGET:.2f}")
    print(f"Total expenses:   ₹{total:.2f}")
    print(f"Remaining budget: ₹{remaining:.2f}")

    if remaining < 0:
        print(f"Over budget by ₹{-remaining:.2f}")
    else:
        print("You are within your budget!")


def show_category_analytics(expenses):
    """Show spending totals and percentages by category."""
    current_month = date.today().strftime("%Y-%m")
    monthly_expenses = get_month_expenses(expenses, current_month)

    if not monthly_expenses:
        print("\nNo expenses recorded for this month.")
        return

    category_totals = {}

    for expense in monthly_expenses:
        category = expense["category"]
        amount = expense["amount"]

        category_totals[category] = (
            category_totals.get(category, 0) + amount
        )

    total = sum(category_totals.values())

    print(f"\n===== Category Analytics: {current_month} =====")

    for category, amount in sorted(
        category_totals.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        percentage = (amount / total) * 100
        print(f"{category}: ₹{amount:.2f} ({percentage:.1f}%)")

    print(f"\nTotal spending: ₹{total:.2f}")


def main():
    expenses = load_expenses()

    

    while True:
        print("\n===== CampusSpend =====")
        print("1. Add expense")
        print("2. View all transactions")
        print("3. View current month's budget summary")
        print("4. View transactions for a month")
        print("5. View category analytics")
        print("6. Exit")

        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_expenses(expenses)
        elif choice == "3":
            show_summary(expenses)
        elif choice == "4":
            view_monthly_expenses(expenses)
        elif choice == "5":
            show_category_analytics(expenses)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Enter 1, 2, 3, 4, 5, or 6.")


if __name__ == "__main__":
    main()
