import streamlit as st
from datetime import date, timedelta
import uuid

from storage import load_expenses, save_expenses, load_budget_settings
from expense_logic import (
    get_current_month,
    calculate_budget_status,
    create_expense,
)

st.set_page_config(
    page_title="CampusSpend",
    page_icon="💸",
    layout="wide",
)

st.title("💸 CampusSpend")
st.caption("Your personal student expense tracker")

# Load saved data
# Load saved data

# Load saved data
expenses = load_expenses()
budget_settings = load_budget_settings()

# Get this month's budget and spending
current_month = get_current_month()
monthly_budget = budget_settings["monthly_budgets"].get(current_month, 5000.0)
category_budgets = budget_settings["category_budgets"].get(current_month, {})


status = calculate_budget_status(
    expenses,
    current_month,
    monthly_budget,
    category_budgets,
)

st.subheader("Your Spending Dashboard")
st.caption(f"Overview for {current_month}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Monthly Budget", f"₹{status['monthly_budget']:,.2f}")

with col2:
    st.metric("Total Spent", f"₹{status['total_spent']:,.2f}")

with col3:
    st.metric("Remaining Budget", f"₹{status['remaining']:,.2f}")

# Budget progress
if status["monthly_budget"] > 0:
    progress = min(
        status["total_spent"] / status["monthly_budget"],
        1.0,
    )
    st.subheader("Monthly Budget Progress")
    st.progress(progress)
    st.caption(
        f"{status['total_spent'] / status['monthly_budget'] * 100:.1f}% "
        "of your budget used"
    )

if status["over_budget"] > 0:
    st.warning(f"You are ₹{status['over_budget']:,.2f} over your monthly budget.")

st.divider()


# Recent Transactions
st.subheader("Recent Transactions")

if expenses:
    sorted_expenses = sorted(
        expenses,
        key=lambda expense: expense.get("date") or "",
        reverse=True,
    )

    available_months = sorted(
        {expense["date"][:7] for expense in sorted_expenses if expense.get("date")},
        reverse=True,
    )

    selected_month = st.selectbox(
        "Filter transactions by month",
        options=["All months"] + available_months,
    )

    if selected_month == "All months":
        filtered_expenses = sorted_expenses
    else:
        filtered_expenses = [
            expense
            for expense in sorted_expenses
            if expense.get("date", "").startswith(selected_month)
        ]

    if filtered_expenses:
        if selected_month == "All months":
            displayed_expenses = filtered_expenses[:5]
        else:
            displayed_expenses = filtered_expenses

        st.dataframe(
            [
                {
                    "Date": expense.get("date") or "Unknown",
                    "Category": expense["category"],
                    "Amount (₹)": expense["amount"],
                }
                for expense in displayed_expenses
            ],
            use_container_width=True,
            hide_index=True,
        )

        if selected_month == "All months":
            st.caption(
                f"Showing {len(displayed_expenses)} of "
                f"{len(filtered_expenses)} matching transactions."
            )
        else:
            st.caption(
                f"Showing all {len(filtered_expenses)} transactions "
                f"for {selected_month}."
            )
    else:
        st.info("No transactions found for this month.")

else:
    st.info("No expenses yet. Add expenses through your existing CLI app.")


# Category spending charts
st.subheader("📊 Where Your Money Goes")

if expenses:
    category_totals = {}

    # Calculate total spending for each category
    for expense in expenses:
        category = expense["category"]
        amount = expense["amount"]

        if category not in category_totals:
            category_totals[category] = 0

        category_totals[category] += amount

    # Prepare data for the charts
    chart_data = {
        "Category": list(category_totals.keys()),
        "Amount (₹)": list(category_totals.values()),
    }

    # Spending insight: highest-spending category
    highest_category = max(category_totals, key=category_totals.get)
    highest_amount = category_totals[highest_category]
    total_spending = sum(category_totals.values())
    spending_percentage = (highest_amount / total_spending) * 100

    st.write("### 💡 Spending Insight")
    st.info(
        f"Your highest-spending category is **{highest_category}**, "
        f"with ₹{highest_amount:,.2f} spent. "
        f"That's {spending_percentage:.1f}% of your total spending."
    )

    # Bar chart
    st.write("### Spending by Category")

    st.bar_chart(
        chart_data,
        x="Category",
        y="Amount (₹)",
        width="stretch",
    )

else:
    st.info("Add your first expense to see your spending charts.")


# Monthly spending trend and comparison
st.subheader("📈 Monthly Spending Trend")

if expenses:
    monthly_totals = {}

    for expense in expenses:
        expense_month = expense["date"][:7]
        amount = expense["amount"]

        if expense_month not in monthly_totals:
            monthly_totals[expense_month] = 0

        monthly_totals[expense_month] += amount

    sorted_months = sorted(monthly_totals.keys())

    # Month-over-month spending comparison
    st.write("### 📊 Month-over-Month Comparison")

    current_month = date.today().strftime("%Y-%m")

    # Find the previous calendar month
    today = date.today()
    first_day_of_current_month = today.replace(day=1)
    previous_month_date = first_day_of_current_month - timedelta(days=1)
    previous_month = previous_month_date.strftime("%Y-%m")

    current_spending = monthly_totals.get(current_month, 0)
    previous_spending = monthly_totals.get(previous_month, 0)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "This Month",
            f"₹{current_spending:,.2f}",
        )

    with col2:
        st.metric(
            "Previous Month",
            f"₹{previous_spending:,.2f}",
        )

    if previous_spending > 0:
        change = current_spending - previous_spending
        percentage_change = (change / previous_spending) * 100

        if change > 0:
            st.warning(
                f"Spending increased by ₹{change:,.2f} "
                f"({percentage_change:.1f}%) compared with last month."
            )
        elif change < 0:
            st.success(
                f"Spending decreased by ₹{abs(change):,.2f} "
                f"({abs(percentage_change):.1f}%) compared with last month."
            )
        else:
            st.info("Your spending is unchanged from last month.")

    elif current_spending > 0:
        st.info(
            "You have spending this month, but no recorded spending "
            "for the previous month to compare against."
        )
    else:
        st.info("No spending recorded for this month or the previous month yet.")

    # Prepare data for the trend chart
    trend_data = {
        "Month": sorted_months,
        "Total Spent (₹)": [monthly_totals[month] for month in sorted_months],
    }

    st.write("### Monthly Spending History")

    st.line_chart(
        trend_data,
        x="Month",
        y="Total Spent (₹)",
        width="stretch",
    )

else:
    st.info("Add expenses to see your monthly spending trend.")


# Add a new expense
st.subheader("➕ Add an Expense")

with st.form("add_expense_form"):
    expense_amount = st.number_input(
        "Amount (₹)",
        min_value=0.01,
        step=10.0,
        format="%.2f",
    )

    expense_category = st.selectbox(
        "Category",
        [
            "Food",
            "Transport",
            "Shopping",
            "Education",
            "Entertainment",
            "Health",
            "Other",
        ],
    )

    expense_date = st.date_input(
        "Date",
        value=date.today(),
    )

    expense_description = st.text_input(
        "Description (optional)",
        placeholder="e.g. Lunch at the college canteen",
    )

    submitted = st.form_submit_button("Save Expense")

    if submitted:
        try:
            new_expense = create_expense(
                amount=expense_amount,
                category=expense_category,
                expense_date=expense_date.isoformat(),
                description=expense_description,
            )

            expenses.append(new_expense)

            try:
                save_expenses(expenses)
            except OSError:
                expenses.pop()
                raise

            st.success("Expense saved successfully!")
            st.rerun()

        except ValueError as error:
            st.error(str(error))
        except OSError:
            st.error("Could not save the expense. Please try again.")


st.divider()

# Category budgets
st.subheader("Category Budgets")

if status["categories"]:
    for category, details in status["categories"].items():
        st.write(f"**{category}**")
        st.caption(f"Spent ₹{details['spent']:,.2f} " f"of ₹{details['budget']:,.2f}")

        if details["budget"] > 0:
            category_progress = min(
                details["spent"] / details["budget"],
                1.0,
            )
            st.progress(category_progress)

        if details["over_budget"] > 0:
            st.warning(f"{category}: ₹{details['over_budget']:,.2f} over budget")
else:
    st.info("No category budgets configured yet.")
