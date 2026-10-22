
from datetime import date


MONTHLY_BUDGET = 5000.0


def get_month_expenses(expenses, month):
    """Return dated transactions for a month in YYYY-MM format."""
    return [
        expense for expense in expenses
        if isinstance(expense.get("date"), str)
        and expense["date"].startswith(month)
    ]


def calculate_monthly_totals(expenses, month):
    """Calculate spending and remaining budget for a selected month."""
    monthly_expenses = get_month_expenses(expenses, month)

    total = sum(expense["amount"] for expense in monthly_expenses)
    remaining = MONTHLY_BUDGET - total

    return {
        "budget": MONTHLY_BUDGET,
        "total": total,
        "remaining": remaining,
        "over_budget": max(0, total - MONTHLY_BUDGET),
    }


def calculate_category_totals(expenses, month):
    """Return spending totals grouped by category for a selected month."""
    monthly_expenses = get_month_expenses(expenses, month)
    category_totals = {}

    for expense in monthly_expenses:
        category = expense["category"]
        amount = expense["amount"]

        category_totals[category] = (
            category_totals.get(category, 0) + amount
        )

    return category_totals


def get_current_month():
    """Return the current month in YYYY-MM format."""
    return date.today().strftime("%Y-%m")
