
import uuid
from datetime import date, datetime

from storage import load_expenses, save_expenses

from expense_logic import (
    MONTHLY_BUDGET,
    calculate_monthly_totals,
    calculate_category_totals,
    get_current_month,
    get_month_expenses,
    filter_expenses,
)


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
        "id": uuid.uuid4().hex,
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



def edit_expense(expenses):
    """Edit an existing expense and save the changes."""
    if not expenses:
        print("\nNo expenses available to edit.")
        return

    view_expenses(expenses)

    try:
        choice = int(input("\nEnter the transaction number to edit: "))

        if choice < 1 or choice > len(expenses):
            print("Invalid transaction number.")
            return

    except ValueError:
        print("Please enter a valid number.")
        return

    index = choice - 1

    # Keep the original safe in case saving fails.
    original_expense = expenses[index].copy()
    updated_expense = original_expense.copy()

    print("\nPress Enter to keep the existing value.")

    category = input(
        f"Category [{original_expense['category']}]: "
    ).strip()

    if category:
        updated_expense["category"] = category.title()

    amount_input = input(
        f"Amount [{original_expense['amount']}]: "
    ).strip()

    if amount_input:
        try:
            amount = float(amount_input)

            if amount <= 0:
                print("Amount must be greater than zero.")
                return

            updated_expense["amount"] = amount

        except ValueError:
            print("Please enter a valid numeric amount.")
            return

    # Avoid writing anything if the user made no changes.
    if updated_expense == original_expense:
        print("No changes made.")
        return

    expenses[index] = updated_expense

    try:
        save_expenses(expenses)
        print("Expense updated successfully!")

    except OSError as error:
        expenses[index] = original_expense
        print(f"Could not save the updated expense: {error}")


def delete_expense(expenses):
    """Delete an expense after user confirmation."""
    if not expenses:
        print("\nNo expenses available to delete.")
        return

    view_expenses(expenses)

    try:
        choice = int(input("\nEnter the transaction number to delete: "))

        if choice < 1 or choice > len(expenses):
            print("Invalid transaction number.")
            return

    except ValueError:
        print("Please enter a valid number.")
        return

    index = choice - 1
    deleted_expense = expenses[index]

    confirmation = input(
        f"Delete {deleted_expense['category']} expense of "
        f"₹{deleted_expense['amount']:.2f}? (yes/no): "
    ).strip().lower()

    if confirmation not in ("yes", "y"):
        print("Deletion cancelled.")
        return

    # Remove it temporarily, then restore it if saving fails.
    deleted_expense = expenses.pop(index)

    try:
        save_expenses(expenses)
        print("Expense deleted successfully!")

    except OSError as error:
        expenses.insert(index, deleted_expense)
        print(f"Could not save the deletion: {error}")



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
    month = get_current_month()
    totals = calculate_monthly_totals(expenses, month)

    print(f"\nMonthly Budget: ₹{totals['budget']:.2f}")
    print(f"Total Spent: ₹{totals['total']:.2f}")
    print(f"Remaining Budget: ₹{totals['remaining']:.2f}")

    if totals["over_budget"] > 0:
        print(f"You are over budget by ₹{totals['over_budget']:.2f}")
    else:
        print("You are within your budget.")


def show_category_analytics(expenses):
    month = get_current_month()
    category_totals = calculate_category_totals(expenses, month)

    if not category_totals:
        print("\nNo expenses recorded for this month.")
        return

    total_spent = sum(category_totals.values())

    print("\nCategory-wise Spending:")

    sorted_categories = sorted(
        category_totals.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    for category, amount in sorted_categories:
        percentage = (amount / total_spent) * 100
        print(f"{category}: ₹{amount:.2f} ({percentage:.1f}%)")


def filter_expenses_menu(expenses):
    """Let the user filter expenses by category and date range."""
    if not expenses:
        print("\nNo expenses available to filter.")
        return

    print("\n--- Filter Expenses ---")
    print("Leave a field blank to skip that filter.")

    category = input("Category: ").strip()
    start_date = input("Start date (YYYY-MM-DD): ").strip()
    end_date = input("End date (YYYY-MM-DD): ").strip()

    # Validate the supplied dates.
    for date_value, label in [
        (start_date, "Start date"),
        (end_date, "End date"),
    ]:
        if date_value:
            try:
                datetime.strptime(date_value, "%Y-%m-%d")
            except ValueError:
                print(f"{label} must use YYYY-MM-DD format.")
                return

    if start_date and end_date and start_date > end_date:
        print("Start date cannot be after end date.")
        return

    results = filter_expenses(
        expenses,
        category=category or None,
        start_date=start_date or None,
        end_date=end_date or None,
    )

    if not results:
        print("\nNo matching expenses found.")
        return

    print(f"\nFound {len(results)} matching expense(s):")

    for expense in results:
        expense_date = expense.get("date") or "Unknown"
        print(
            f"{expense_date} | "
            f"{expense['category']} | "
            f"₹{expense['amount']:.2f}"
        )

    total = sum(expense["amount"] for expense in results)
    print(f"\nTotal of matching expenses: ₹{total:.2f}")


def main():
    expenses = load_expenses()

    while True:
        print("\n===== CampusSpend =====")
        print("1. Add expense")
        print("2. View all transactions")
        print("3. Monthly budget summary")
        print("4. View expenses for a month")
        print("5. Category analytics")
        print("6. Edit expense")
        print("7. Delete expense")
        print("8. Filter Expenses")
        print("9. Exit")

        choice = input("Choose an option: ").strip()

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
            edit_expense(expenses)

        elif choice == "7":
            delete_expense(expenses)

        elif choice == "8":
            filter_expenses_menu(expenses)
        elif choice == "9":
            print("Thank you for using CampusSpend!")
            break

        else:
            print("Invalid choice. Please select an option from 1 to 9.")




if __name__ == "__main__":
    main()



