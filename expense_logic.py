
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


def filter_expenses(expenses, category=None, start_date=None, end_date=None):
    """Filter expenses by category and an inclusive date range."""
    filtered = []

    for expense in expenses:
        if category and expense["category"].lower() != category.lower():
            continue

        expense_date = expense.get("date")

        if start_date and (not expense_date or expense_date < start_date):
            continue

        if end_date and (not expense_date or expense_date > end_date):
            continue

        filtered.append(expense)

    return filtered


def calculate_budget_status(expenses, month, monthly_budget, category_budgets):
    """Calculate monthly and category budget usage for a selected month."""
    monthly_expenses = get_month_expenses(expenses, month)

    total_spent = sum(
        expense["amount"] for expense in monthly_expenses
    )

    category_totals = calculate_category_totals(expenses, month)

    category_status = {}

    for category, budget in category_budgets.items():
        spent = category_totals.get(category, 0.0)

        category_status[category] = {
            "budget": budget,
            "spent": spent,
            "remaining": budget - spent,
            "over_budget": max(0.0, spent - budget),
        }

    return {
        "monthly_budget": monthly_budget,
        "total_spent": total_spent,
        "remaining": monthly_budget - total_spent,
        "over_budget": max(0.0, total_spent - monthly_budget),
        "categories": category_status,
    }
