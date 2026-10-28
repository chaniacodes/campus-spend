from datetime import date, timedelta

import pandas as pd
import streamlit as st
import plotly.express as px

from storage import (
    load_expenses,
    save_expenses,
    load_budget_settings,
    save_budget_settings,
)
from expense_logic import (
    get_current_month,
    calculate_budget_status,
    calculate_category_totals,
    generate_monthly_wrapped,
    generate_annual_wrapped,
    create_expense,
)

st.set_page_config(
    page_title="CampusSpend",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- CAMPUSSPEND DESIGN SYSTEM --------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {
        --ink: #f8f5f2;
        --muted: #b9b1c3;
        --plum: #17101f;
        --panel: #24182e;
        --lime: #d8ff3e;
        --violet: #a78bfa;
        --orange: #ff965c;
        --pink: #ff6fb5;
        --line: rgba(255, 255, 255, 0.12);
    }

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 85% 0%,
                rgba(119, 63, 151, 0.20), transparent 35%),
            #17101f;
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: rgba(23, 16, 31, 0.8);
    }

    [data-testid="stSidebar"] {
        background: #110c17;
        border-right: 1px solid var(--line);
    }
    /* ---------- SIDEBAR NAVIGATION TEXT ---------- */

[data-testid="stSidebar"] {
    color: #F8F5F2 !important;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: #F8F5F2;
}

[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
    color: #F8F5F2 !important;
    background-color: #24182E !important;
}

/* Radio-button navigation, if used for the menu */
[data-testid="stSidebar"] [role="radiogroup"] label {
    color: #F8F5F2 !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    color: #D8FF3E !important;
}

    h1, h2, h3 {
        color: var(--ink);
        letter-spacing: -0.045em;
    }

    h1 {
        font-size: clamp(2.4rem, 5vw, 4.6rem);
        font-weight: 700;
        line-height: 1;
    }

    [data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
    }

    [data-testid="stMetricValue"] {
        color: var(--ink);
        font-weight: 700;
    }

    /* ---------- SELECTBOX TEXT AND DROPDOWNS ---------- */

div[data-testid="stSelectbox"] label {
    color: #F8F5F2 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background-color: #24182E !important;
    border-color: rgba(216, 255, 62, 0.35) !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] span {
    color: #F8F5F2 !important;
}

div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] li {
    background-color: #24182E !important;
    color: #F8F5F2 !important;
}

div[data-baseweb="popover"] li:hover {
    background-color: #3A2848 !important;
    color: #D8FF3E !important;
}

    .stButton > button,
    .stFormSubmitButton > button {
        background: var(--lime);
        color: #17101f;
        border: 0;
        border-radius: 999px;
        font-weight: 700;
        min-height: 2.7rem;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: #e5ff79;
        color: #17101f;
    }

    hr {
        border-color: var(--line);
    }

    .eyebrow {
        color: var(--lime);
        font-family: 'DM Mono', monospace;
        font-size: 0.76rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 0.65rem;
    }

    .hero {
        padding: clamp(1.4rem, 4vw, 3rem);
        border-radius: 28px;
        background: linear-gradient(
            125deg, #392346 0%, #261a33 48%, #18241c 100%
        );
        border: 1px solid var(--line);
        margin: 0.5rem 0 1.4rem;
        overflow: hidden;
    }

    .hero-title {
        font-size: clamp(2.6rem, 7vw, 6.2rem);
        line-height: 0.95;
        font-weight: 700;
        letter-spacing: -0.075em;
        color: #fffaf4;
        margin: 0.35rem 0 1rem;
    }

    .accent {
        color: var(--lime);
    }

    .hero-subtitle {
        color: #d5c9df;
        font-size: 1.05rem;
        max-width: 620px;
    }

    .big-number {
        font-size: clamp(2.6rem, 6vw, 5.6rem);
        line-height: 1;
        letter-spacing: -0.075em;
        font-weight: 700;
        color: var(--lime);
        margin: 0.55rem 0;
        overflow-wrap: anywhere;
    }

    .story-card {
        min-height: 190px;
        padding: 1.35rem;
        border-radius: 22px;
        border: 1px solid var(--line);
        background: var(--panel);
    }

    .story-card.lime {
        background: linear-gradient(145deg, #d8ff3e, #b7e72e);
        color: #17101f;
    }

    .story-card.violet {
        background: linear-gradient(145deg, #a78bfa, #7657c8);
        color: #17101f;
    }

    .story-card.orange {
        background: linear-gradient(145deg, #ffb16f, #ff795c);
        color: #251329;
    }

    .story-card.pink {
        background: linear-gradient(145deg, #ff91c8, #e95f9e);
        color: #251329;
    }

    .story-card .eyebrow {
        color: inherit;
        opacity: 0.72;
    }

    .card-title {
        font-size: 1.2rem;
        font-weight: 700;
    }

    .card-value {
        font-size: clamp(1.8rem, 4vw, 3.2rem);
        font-weight: 700;
        line-height: 1.1;
        letter-spacing: -0.06em;
        margin: 0.7rem 0;
        overflow-wrap: anywhere;
    }

    .card-note {
        font-size: 0.9rem;
        opacity: 0.8;
    }

    .section-kicker {
        color: var(--lime);
        text-transform: uppercase;
        font-family: 'DM Mono', monospace;
        letter-spacing: 0.12em;
        font-size: 0.76rem;
        margin-bottom: 0.4rem;
    }

    .recap-banner {
        padding: 1.5rem 1.7rem;
        border-radius: 20px;
        background: linear-gradient(
            110deg,
            rgba(167, 139, 250, 0.20),
            rgba(255, 111, 181, 0.10)
        );
        border: 1px solid rgba(167, 139, 250, 0.3);
    }

    .recap-banner strong {
        color: var(--lime);
    }

    
    .small-note {
        color: var(--muted);
        font-size: 0.9rem;
    }

    /* ---------- WRAPPED PAGE SPACING ---------- */

    .section-kicker {
        margin-top: 2.2rem;
        margin-bottom: 1.1rem;
        letter-spacing: 0.13em;
        line-height: 1.5;
    }

    .story-card {
        padding: 1.8rem;
        margin-bottom: 1rem;
        min-height: 150px;
    }

    .recap-banner {
        margin-top: 3rem;
        margin-bottom: 2rem;
        padding: 2.5rem;
        border-radius: 24px;
    }

    .recap-banner .hero-title {
        margin-top: 0.8rem;
        margin-bottom: 0.8rem;
    }

    .recap-banner .hero-subtitle {
        margin-top: 0.8rem;
        line-height: 1.7;
    }
    </style>

    """,
    unsafe_allow_html=True,
)

DEFAULT_MONTHLY_BUDGET = 5000.0

CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Education",
    "Entertainment",
    "Health",
    "Bills",
    "Other",
]


# -------------------- HELPERS --------------------


def money(amount):
    return f"₹{amount:,.2f}"


def show_hero(eyebrow, title_html, subtitle):
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{eyebrow}</div>
            <div class="hero-title">{title_html}</div>
            <div class="hero-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_story_card(tone, eyebrow, title, value, note):
    st.markdown(
        f"""
        <div class="story-card {tone}">
            <div class="eyebrow">{eyebrow}</div>
            <div class="card-title">{title}</div>
            <div class="card-value">{value}</div>
            <div class="card-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_category_chart(category_totals):
    if not category_totals:
        st.info("No category data to visualise yet.")
        return

    chart_data = pd.DataFrame(
        list(category_totals.items()),
        columns=["Category", "Amount"],
    ).sort_values("Amount", ascending=True)

    # Give the highest-spending category a special accent.
    max_amount = chart_data["Amount"].max()
    chart_data["Colour"] = chart_data["Amount"].apply(
        lambda amount: ("#D8FF3E" if amount == max_amount else "#A78BFA")
    )

    fig = px.bar(
        chart_data,
        x="Amount",
        y="Category",
        orientation="h",
        text="Amount",
        color="Colour",
        color_discrete_map="identity",
        custom_data=["Category"],
    )

    fig.update_traces(
        texttemplate="₹%{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
        width=0.52,
        hovertemplate=(
            "<b>%{customdata[0]}</b>"
            "<br><span style='color:#D8FF3E'>"
            "●</span> Spent: ₹%{x:,.2f}"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Space Grotesk, sans-serif",
            color="#F8F5F2",
            size=13,
        ),
        height=max(280, len(chart_data) * 64),
        margin=dict(l=10, r=85, t=20, b=15),
        showlegend=False,
        bargap=0.48,
        xaxis=dict(
            title=None,
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            fixedrange=True,
        ),
        yaxis=dict(
            title=None,
            showgrid=False,
            ticks="",
            automargin=True,
            fixedrange=True,
            tickfont=dict(
                family="Space Grotesk, sans-serif",
                size=13,
                color="#F8F5F2",
            ),
        ),
        uniformtext=dict(
            minsize=11,
            mode="show",
        ),
    )

    # Add a little space beyond the largest bar for its price label.
    fig.update_xaxes(range=[0, max_amount * 1.30 if max_amount > 0 else 1])

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": False,
        },
    )


def show_wrapped_category_chart(category_totals):
    if not category_totals:
        st.info("No category spending to display for this period.")
        return

    chart_data = pd.DataFrame(
        list(category_totals.items()),
        columns=["Category", "Amount"],
    )

    chart_data["Amount"] = pd.to_numeric(chart_data["Amount"], errors="coerce")
    chart_data = chart_data.dropna(subset=["Amount"])
    chart_data = chart_data[chart_data["Amount"] > 0]
    chart_data = chart_data.sort_values("Amount", ascending=False)

    if chart_data.empty:
        st.info("No category spending to display for this period.")
        return

    palette = [
        "#D8FF3E",
        "#A78BFA",
        "#FF6FB5",
        "#FF965C",
        "#76E6C4",
        "#C4B5FD",
        "#F9D56E",
        "#E5DDF0",
    ]

    fig = px.bar(
        chart_data,
        x="Category",
        y="Amount",
        text="Amount",
        color="Category",
        color_discrete_sequence=palette,
        custom_data=["Category"],
    )

    fig.update_traces(
        texttemplate="₹%{y:,.0f}",
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
        hovertemplate=("<b>%{x}</b><br>" "Spent: ₹%{y:,.2f}" "<extra></extra>"),
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Space Grotesk, sans-serif",
            color="#F8F5F2",
            size=13,
        ),
        height=390,
        margin=dict(l=15, r=20, t=45, b=35),
        showlegend=False,
        bargap=0.38,
        xaxis=dict(
            title=None,
            showgrid=False,
            ticks="",
            tickfont=dict(
                family="Space Grotesk, sans-serif",
                color="#F8F5F2",
                size=12,
            ),
            fixedrange=True,
        ),
        yaxis=dict(
            title=None,
            showgrid=True,
            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False,
            showticklabels=False,
            rangemode="tozero",
            fixedrange=True,
        ),
    )

    max_amount = chart_data["Amount"].max()
    fig.update_yaxes(range=[0, max_amount * 1.22])

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False, "responsive": True},
    )


def show_annual_monthly_charts(monthly_totals):
    if not monthly_totals:
        st.info("No monthly spending data available yet.")
        return

    monthly_data = pd.DataFrame(
        [
            {"Month": month, "Spent": amount}
            for month, amount in sorted(monthly_totals.items())
        ]
    )

    monthly_data["MonthLabel"] = monthly_data["Month"].apply(month_label)

    palette = [
        "#D8FF3E",
        "#A78BFA",
        "#FF6FB5",
        "#FF965C",
        "#76E6C4",
        "#C4B5FD",
        "#F9D56E",
        "#E5DDF0",
        "#D8FF3E",
        "#A78BFA",
        "#FF6FB5",
        "#FF965C",
    ]

    # Monthly spending trend — one bar per month.
    fig = px.bar(
        monthly_data,
        x="MonthLabel",
        y="Spent",
        text="Spent",
        color="MonthLabel",
        color_discrete_sequence=palette,
        custom_data=["Month"],
    )

    fig.update_traces(
        texttemplate="₹%{y:,.0f}",
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
        hovertemplate=("<b>%{x}</b><br>" "Spent: ₹%{y:,.2f}" "<extra></extra>"),
    )

    max_spent = monthly_data["Spent"].max()

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Space Grotesk, sans-serif",
            color="#F8F5F2",
            size=13,
        ),
        height=390,
        margin=dict(l=10, r=15, t=45, b=45),
        showlegend=False,
        bargap=0.35,
        xaxis=dict(
            title=None,
            showgrid=False,
            ticks="",
            tickfont=dict(color="#F8F5F2", size=11),
            fixedrange=True,
        ),
        yaxis=dict(
            title=None,
            showgrid=True,
            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False,
            showticklabels=False,
            range=[0, max_spent * 1.22 if max_spent > 0 else 1],
            fixedrange=True,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False, "responsive": True},
    )

    # Month-by-month breakdown — dark-theme styling.
    st.subheader("Month-by-Month Breakdown")

    for _, row in monthly_data.iterrows():
        month = str(row["MonthLabel"])
        amount = float(row["Spent"])

        left, right = st.columns([2, 1])

        with left:
            st.markdown(f"**{month}**")

        with right:
            st.markdown(
                f"<div style='text-align:right; color:#D8FF3E; "
                f"font-weight:600;'>₹{amount:,.2f}</div>",
                unsafe_allow_html=True,
            )

        st.divider()


def get_monthly_budget(settings, month):
    return float(settings.get("monthly_budgets", {}).get(month, DEFAULT_MONTHLY_BUDGET))


def get_category_budgets(settings, month):
    return settings.get("category_budgets", {}).get(month, {}).copy()


def get_available_months(expenses):
    months = sorted(
        {
            expense["date"][:7]
            for expense in expenses
            if isinstance(expense.get("date"), str)
            and len(expense["date"]) >= 7
            and expense["date"][4:5] == "-"
        }
    )
    return months


def month_label(month):
    try:
        return date.fromisoformat(month + "-01").strftime("%B %Y")
    except ValueError:
        return month


def get_expense_dataframe(expenses):
    if not expenses:
        return pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])

    rows = [
        {
            "Date": expense.get("date", ""),
            "Category": expense.get("category", ""),
            "Description": expense.get("description", ""),
            "Amount": expense.get("amount", 0.0),
        }
        for expense in expenses
    ]

    return pd.DataFrame(rows).sort_values("Date", ascending=False, na_position="last")


def show_budget_progress(spent, budget):
    percentage = (spent / budget * 100) if budget > 0 else 0

    st.progress(min(percentage / 100, 1.0))
    st.caption(f"{money(spent)} spent out of {money(budget)} " f"({percentage:.1f}%)")

    if spent > budget:
        st.error(f"You are {money(spent - budget)} over budget.")
    else:
        st.success(f"{money(budget - spent)} remaining.")


def show_category_chart(category_totals):
    if not category_totals:
        st.info("No category spending to display for this period.")
        return

    chart_data = pd.DataFrame(
        {
            "Category": list(category_totals.keys()),
            "Amount": list(category_totals.values()),
        }
    ).set_index("Category")

    st.bar_chart(chart_data)


# -------------------- LOAD DATA --------------------

expenses = load_expenses()
settings = load_budget_settings()

current_month = get_current_month()
available_months = get_available_months(expenses)

monthly_budget = get_monthly_budget(settings, current_month)
category_budgets = get_category_budgets(settings, current_month)

current_status = calculate_budget_status(
    expenses,
    current_month,
    monthly_budget,
    category_budgets,
)

# -------------------- SIDEBAR --------------------


def go_to_transactions():
    st.session_state["navigation_page"] = "Transactions"


with st.sidebar:
    st.title("💸 CampusSpend")
    st.caption("Your student finance companion")
    st.divider()

    page_options = [
        "Overview",
        "Transactions",
        "Analytics",
        "Budgets",
        "Monthly Wrapped",
        "Annual Wrapped",
    ]

    if "navigation_page" not in st.session_state:
        st.session_state["navigation_page"] = "Overview"

    page = st.radio(
        "NAVIGATION",
        page_options,
        key="navigation_page",
    )

    st.divider()
    st.caption("Track your spending. Understand your habits.")
# ============================================================
# OVERVIEW
# ============================================================


if page == "Overview":
    st.title("Your Overview")
    st.caption(f"Your financial snapshot for {month_label(current_month)}")

    # Main financial metrics
    col1, col2, col3 = st.columns(3)

    col1.metric("Monthly Budget", money(monthly_budget))
    col2.metric("Total Spent", money(current_status["total_spent"]))
    col3.metric(
        "Remaining",
        money(current_status["remaining"]),
        delta=("Over budget" if current_status["remaining"] < 0 else "Available"),
        delta_color="inverse",
    )

    st.subheader("Monthly Budget Progress")
    show_budget_progress(
        current_status["total_spent"],
        monthly_budget,
    )

    st.divider()

    left, right = st.columns(2, gap="large")

    # Spending by Category

    with left:
        st.subheader("Spending by Category")
        current_category_totals = calculate_category_totals(expenses, current_month)

        if current_category_totals:
            category_data = pd.DataFrame(
                {
                    "Category": list(current_category_totals.keys()),
                    "Amount": list(current_category_totals.values()),
                }
            )

            category_colors = [
                "#D8FF3E",  # Lime
                "#A78BFA",  # Violet
                "#FF6FB5",  # Pink
                "#FF965C",  # Orange
                "#76E6C4",  # Mint
                "#C4B5FD",  # Light violet
                "#F9D56E",  # Yellow
            ]

            fig = px.pie(
                category_data,
                names="Category",
                values="Amount",
                hole=0.62,
                color_discrete_sequence=category_colors,
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent",
                textfont=dict(
                    family="Space Grotesk",
                    size=12,
                    color="#17101F",
                ),
                marker=dict(line=dict(color="#24182E", width=3)),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Spent: ₹%{value:,.2f}<br>"
                    "%{percent}<extra></extra>"
                ),
            )

            fig.update_layout(
                height=300,
                margin=dict(l=5, r=5, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    family="Space Grotesk",
                    color="#F8F5F2",
                ),
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.08,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11, color="#B9B1C3"),
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            )

            top_category = max(
                current_category_totals,
                key=current_category_totals.get,
            )

            st.info(
                f"Your highest spending category this month is "
                f"**{top_category}** at "
                f"**{money(current_category_totals[top_category])}**."
            )
        else:
            st.info("No expenses recorded for this month yet.")

    # Recent Transactions — dark-themed native layout
    with right:
        st.subheader("Recent Transactions")

        recent = sorted(
            expenses,
            key=lambda item: item.get("date") or "",
            reverse=True,
        )[:5]

        if recent:
            for index, expense in enumerate(recent):
                transaction_cols = st.columns([2, 3, 2])

                with transaction_cols[0]:
                    st.markdown(
                        f"<span style='color:#B9B1C3;font-size:12px;'>"
                        f"{expense.get('date', '—')}</span>",
                        unsafe_allow_html=True,
                    )

                with transaction_cols[1]:
                    st.markdown(f"**{expense.get('category', 'Other')}**")
                    description = expense.get(
                        "description",
                        expense.get("note", ""),
                    )
                    if description:
                        st.caption(str(description))

                with transaction_cols[2]:
                    st.markdown(
                        f"<div style='text-align:right; "
                        f"color:#D8FF3E; font-weight:600;'>"
                        f"{money(expense.get('amount', 0))}</div>",
                        unsafe_allow_html=True,
                    )

                if index < len(recent) - 1:
                    st.markdown(
                        "<hr style='margin:8px 0;"
                        "border:0;"
                        "border-top:1px solid rgba(255,255,255,0.10);'>",
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown("### Your money story starts here")
            st.caption(
                "Log your first expense to see your spending, "
                "track your budget, and build your monthly recap."
            )

            st.button(
                "＋ Add your first expense",
                key="overview_first_expense",
                type="primary",
                use_container_width=True,
                on_click=go_to_transactions,
            )

    st.divider()

    st.subheader("Quick Actions")
    st.write(
        "Use **Transactions** to add or review expenses, "
        "**Budgets** to manage your limits, or open a Wrapped "
        "page for a spending recap."
    )

# ============================================================
# TRANSACTIONS
# ============================================================

elif page == "Transactions":
    st.title("Transactions")
    st.caption("Add, review and filter your expenses.")

    with st.expander("➕ Add a New Expense", expanded=not bool(expenses)):
        with st.form("add_expense_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            amount = col1.number_input(
                "Amount (₹)",
                min_value=0.01,
                step=10.0,
                format="%.2f",
            )

            category = col2.selectbox("Category", CATEGORIES)

            expense_date = st.date_input(
                "Date",
                value=date.today(),
            )

            description = st.text_input(
                "Description",
                placeholder="e.g. Lunch at the campus cafe",
            )

            submitted = st.form_submit_button(
                "Save Expense",
                use_container_width=True,
            )

            if submitted:
                try:
                    new_expense = create_expense(
                        amount,
                        category,
                        expense_date.isoformat(),
                        description,
                    )

                    expenses.append(new_expense)

                    try:
                        save_expenses(expenses)
                    except OSError as error:
                        expenses.pop()
                        st.error(f"Could not save the expense: {error}")
                    else:
                        st.success("Expense saved successfully!")
                        st.rerun()

                except ValueError as error:
                    st.error(str(error))

    st.divider()

    month_options = ["All months"] + list(reversed(available_months))
    selected_month = st.selectbox(
        "Filter by month",
        month_options,
        format_func=lambda item: (item if item == "All months" else month_label(item)),
    )

    filtered_expenses = expenses

    if selected_month != "All months":
        filtered_expenses = [
            expense
            for expense in expenses
            if isinstance(expense.get("date"), str)
            and expense["date"].startswith(selected_month)
        ]

    if filtered_expenses:
        total_shown = sum(float(item.get("amount", 0)) for item in filtered_expenses)

        metric_col1, metric_col2 = st.columns(2, gap="large")

        metric_col1.metric(
            "Transactions shown",
            len(filtered_expenses),
        )
        metric_col2.metric(
            "Total shown",
            money(total_shown),
        )

        st.divider()

        sorted_expenses = sorted(
            filtered_expenses,
            key=lambda item: item.get("date") or "",
            reverse=True,
        )

        date_col, details_col, amount_col = st.columns(
            [1.4, 3, 1.5],
            gap="medium",
        )

        with date_col:
            st.caption("DATE")

        with details_col:
            st.caption("CATEGORY / DESCRIPTION")

        with amount_col:
            st.markdown(
                "<div style='text-align:right; color:#B9B1C3; "
                "font-size:0.8rem;'>AMOUNT</div>",
                unsafe_allow_html=True,
            )

        st.divider()

        for index, expense in enumerate(sorted_expenses):
            date_col, details_col, amount_col = st.columns(
                [1.3, 3.2, 1.5],
                gap="small",
            )

            with date_col:
                raw_date = expense.get("date", "—")
                try:
                    display_date = date.fromisoformat(raw_date).strftime("%d %b")
                except (ValueError, TypeError):
                    display_date = raw_date

                st.markdown(
                    f"<span style='color:#B9B1C3; font-size:0.85rem;'>"
                    f"{display_date}</span>",
                    unsafe_allow_html=True,
                )

            with details_col:
                category = expense.get("category", "Other")
                description = expense.get("description") or expense.get("note") or ""

                st.markdown(
                    f"<span style='font-size:0.95rem; font-weight:600;'>"
                    f"{category}</span>"
                    + (
                        f"<span style='color:#B9B1C3; font-size:0.8rem;'>"
                        f" · {description}</span>"
                        if description
                        else ""
                    ),
                    unsafe_allow_html=True,
                )

            with amount_col:
                st.markdown(
                    f"<div style='text-align:right; color:#D8FF3E; "
                    f"font-weight:600; font-size:0.9rem;'>"
                    f"{money(expense.get('amount', 0))}</div>",
                    unsafe_allow_html=True,
                )

            if index < len(sorted_expenses) - 1:
                st.markdown(
                    "<hr style='margin:0.25rem 0; "
                    "border-color:rgba(255,255,255,0.08);'>",
                    unsafe_allow_html=True,
                )

    else:
        st.info("No transactions found for this selection.")


# ============================================================
# ANALYTICS
# ============================================================

elif page == "Analytics":
    st.title("Spending Analytics")
    st.caption("Explore your spending patterns.")

    month_options = sorted(set(available_months + [current_month]))
    month_options = list(reversed(month_options))

    selected_month = st.selectbox(
        "Choose a month",
        month_options,
        format_func=month_label,
        key="analytics_month",
    )

    selected_expenses = [
        expense
        for expense in expenses
        if isinstance(expense.get("date"), str)
        and expense["date"].startswith(selected_month)
    ]

    total_spent = sum(item["amount"] for item in selected_expenses)
    category_totals = calculate_category_totals(expenses, selected_month)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spent", money(total_spent))
    col2.metric("Transactions", len(selected_expenses))
    col3.metric(
        "Average Transaction",
        money(total_spent / len(selected_expenses)) if selected_expenses else money(0),
    )

    st.divider()

    left, right = st.columns(2, gap="large")

    with left:
        st.subheader("Category Breakdown")

        if category_totals:
            category_data = pd.DataFrame(
                [
                    {"Category": category, "Amount": amount}
                    for category, amount in sorted(
                        category_totals.items(),
                        key=lambda item: item[1],
                        reverse=True,
                    )
                ]
            )

            category_colors = [
                "#D8FF3E",
                "#A78BFA",
                "#FF6FB5",
                "#FF965C",
                "#76E6C4",
                "#C4B5FD",
                "#F9D56E",
            ]

            fig = px.bar(
                category_data,
                x="Category",
                y="Amount",
                text="Amount",
                color="Category",
                color_discrete_sequence=category_colors,
            )

            fig.update_traces(
                texttemplate="₹%{y:,.0f}",
                textposition="outside",
                cliponaxis=False,
                hovertemplate=("<b>%{x}</b><br>" "Spent: ₹%{y:,.2f}<extra></extra>"),
            )

            fig.update_layout(
                height=350,
                showlegend=False,
                margin=dict(l=5, r=10, t=25, b=5),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    family="Space Grotesk",
                    color="#F8F5F2",
                ),
                xaxis=dict(
                    title=None,
                    tickfont=dict(color="#B9B1C3", size=11),
                    showgrid=False,
                    linecolor="rgba(255,255,255,0.12)",
                ),
                yaxis=dict(
                    title=None,
                    tickprefix="₹",
                    tickformat=",.0f",
                    gridcolor="rgba(255,255,255,0.08)",
                    zeroline=False,
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            )
        else:
            st.info("No spending recorded for this month.")

    with right:
        st.subheader("Category Totals")

        if category_totals:
            sorted_categories = sorted(
                category_totals.items(),
                key=lambda item: item[1],
                reverse=True,
            )

            total_category_spend = sum(category_totals.values())

            for index, (category, amount) in enumerate(sorted_categories):
                category_col, amount_col = st.columns(
                    [2, 1],
                    gap="small",
                )

                with category_col:
                    st.markdown(f"**{category}**")

                with amount_col:
                    st.markdown(
                        f"<div style='text-align:right; "
                        f"color:#D8FF3E; font-weight:600;'>"
                        f"{money(amount)}</div>",
                        unsafe_allow_html=True,
                    )

                share = (
                    amount / total_category_spend * 100 if total_category_spend else 0
                )

                st.progress(
                    share / 100,
                    text=f"{share:.1f}% of category spending",
                )

                if index < len(sorted_categories) - 1:
                    st.markdown(
                        "<div style='margin:0.6rem 0;'></div>",
                        unsafe_allow_html=True,
                    )

            top_category = max(
                category_totals,
                key=category_totals.get,
            )

            st.info(
                f"Top category: **{top_category}** "
                f"({money(category_totals[top_category])})"
            )
        else:
            st.info("No spending recorded for this month.")

    st.divider()
    st.subheader("Monthly Spending Trend")

    if available_months:
        monthly_totals = {}

        for expense in expenses:
            expense_month = expense.get("date")
            if isinstance(expense_month, str) and len(expense_month) >= 7:
                key = expense_month[:7]
                monthly_totals[key] = monthly_totals.get(key, 0.0) + expense["amount"]

        trend = pd.DataFrame(
            [
                {"Month": month, "Spent": total}
                for month, total in sorted(monthly_totals.items())
            ]
        ).set_index("Month")

        trend_data = trend.reset_index()
        trend_data["MonthLabel"] = trend_data["Month"].apply(month_label)

        trend_colors = [
            "#D8FF3E",
            "#A78BFA",
            "#FF6FB5",
            "#FF965C",
            "#76E6C4",
            "#C4B5FD",
            "#F9D56E",
            "#E5DDF0",
        ]

        trend_fig = px.bar(
            trend_data,
            x="MonthLabel",
            y="Spent",
            text="Spent",
            color="MonthLabel",
            color_discrete_sequence=trend_colors,
        )

        trend_fig.update_traces(
            texttemplate="₹%{y:,.0f}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=("<b>%{x}</b><br>" "Spent: ₹%{y:,.2f}<extra></extra>"),
        )

        trend_fig.update_layout(
            height=350,
            margin=dict(l=5, r=10, t=30, b=5),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            bargap=0.35,
            font=dict(
                family="Space Grotesk",
                color="#F8F5F2",
            ),
            xaxis=dict(
                title=None,
                tickfont=dict(color="#B9B1C3", size=11),
                showgrid=False,
                linecolor="rgba(255,255,255,0.12)",
            ),
            yaxis=dict(
                title=None,
                tickprefix="₹",
                tickformat=",.0f",
                gridcolor="rgba(255,255,255,0.08)",
                zeroline=False,
            ),
        )

        st.plotly_chart(
            trend_fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        selected_date = date.fromisoformat(selected_month + "-01")
        previous_date = selected_date.replace(day=1) - timedelta(days=1)
        previous_month = previous_date.strftime("%Y-%m")

        previous_total = sum(
            item["amount"]
            for item in expenses
            if isinstance(item.get("date"), str)
            and item["date"].startswith(previous_month)
        )

        st.subheader("Month-over-Month Comparison")

        comparison_col1, comparison_col2 = st.columns(2)
        comparison_col1.metric(
            f"{month_label(previous_month)}",
            money(previous_total),
        )

        difference = total_spent - previous_total
        comparison_col2.metric(
            month_label(selected_month),
            money(total_spent),
            delta=money(difference),
            delta_color="inverse",
        )
    else:
        st.info("Add expenses across months to see a spending trend.")


# ============================================================
# BUDGETS
# ============================================================

elif page == "Budgets":
    st.title("Budget Management")
    st.caption("Set limits for each month and spending category.")

    budget_month_options = sorted(
        set(
            available_months
            + list(settings.get("monthly_budgets", {}))
            + [current_month]
        )
    )
    budget_month_options = list(reversed(budget_month_options))

    selected_month = st.selectbox(
        "Budget month",
        budget_month_options,
        format_func=month_label,
        key="budget_month",
    )

    saved_monthly_budget = get_monthly_budget(settings, selected_month)
    saved_category_budgets = get_category_budgets(settings, selected_month)

    st.subheader("Monthly Spending Limit")

    with st.form("monthly_budget_form"):
        new_monthly_budget = st.number_input(
            "Monthly budget (₹)",
            min_value=0.01,
            value=float(saved_monthly_budget),
            step=100.0,
            format="%.2f",
        )

        save_monthly = st.form_submit_button(
            "Save Monthly Budget",
            use_container_width=True,
        )

        if save_monthly:
            updated_settings = {
                "monthly_budgets": settings.get("monthly_budgets", {}).copy(),
                "category_budgets": settings.get("category_budgets", {}).copy(),
            }

            updated_settings["monthly_budgets"][selected_month] = float(
                new_monthly_budget
            )

            try:
                save_budget_settings(updated_settings)
            except OSError as error:
                st.error(f"Could not save the budget: {error}")
            else:
                st.success("Monthly budget saved!")
                st.rerun()

    st.divider()
    st.subheader("Category Budgets")
    st.caption(
        "Enable a category to set its spending limit. "
        "Unchecked categories won't have a separate limit."
    )

    category_options = sorted(set(CATEGORIES) | set(saved_category_budgets.keys()))

    updated_category_budgets = {}

    for category_name in category_options:
        enabled = category_name in saved_category_budgets

        col1, col2 = st.columns([1, 2])

        use_limit = col1.checkbox(
            category_name,
            value=enabled,
            key=f"budget_enabled_{selected_month}_{category_name}",
        )

        current_limit = float(saved_category_budgets.get(category_name, 0.01))
        limit = col2.number_input(
            f"{category_name} limit (₹)",
            min_value=0.01,
            value=current_limit,
            step=50.0,
            format="%.2f",
            key=f"budget_limit_{selected_month}_{category_name}",
            disabled=not use_limit,
        )

        if use_limit:
            updated_category_budgets[category_name] = float(limit)

    if st.button(
        "Save Category Budgets",
        use_container_width=True,
        key="save_category_budgets",
    ):
        updated_settings = {
            "monthly_budgets": settings.get("monthly_budgets", {}).copy(),
            "category_budgets": settings.get("category_budgets", {}).copy(),
        }

        updated_settings["category_budgets"][selected_month] = updated_category_budgets

        try:
            save_budget_settings(updated_settings)
        except OSError as error:
            st.error(f"Could not save category budgets: {error}")
        else:
            st.success("Category budgets saved!")
            st.rerun()
    st.divider()
    st.subheader(f"Budget Status — {month_label(selected_month)}")

    selected_month_budget = get_monthly_budget(settings, selected_month)
    selected_category_budgets = get_category_budgets(settings, selected_month)

    status = calculate_budget_status(
        expenses,
        selected_month,
        selected_month_budget,
        selected_category_budgets,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Monthly Limit", money(status["monthly_budget"]))
    col2.metric("Spent", money(status["total_spent"]))
    col3.metric("Remaining", money(status["remaining"]))

    show_budget_progress(
        status["total_spent"],
        status["monthly_budget"],
    )

    if status["categories"]:
        st.subheader("Category Budget Usage")

        for category_name, category_status in status["categories"].items():
            st.write(f"**{category_name}**")
            show_budget_progress(
                category_status["spent"],
                category_status["budget"],
            )
    else:
        st.info("No category budgets set for this month yet.")


# ============================================================
# MONTHLY WRAPPED
# ============================================================

elif page == "Monthly Wrapped":
    wrapped_month_options = sorted(set(available_months + [current_month]))
    wrapped_month_options = list(reversed(wrapped_month_options))

    selected_month = st.selectbox(
        "Choose your month",
        wrapped_month_options,
        format_func=month_label,
        key="wrapped_month",
    )

    selected_budget = get_monthly_budget(settings, selected_month)

    wrapped = generate_monthly_wrapped(
        expenses,
        selected_month,
        selected_budget,
    )

    total_spent = wrapped["total_spent"]
    category_totals = wrapped["category_totals"]
    top_category = wrapped["top_category"]
    top_amount = wrapped["top_amount"]
    budget_percentage = wrapped["budget_percentage"]

    # ---------- HERO ----------
    st.markdown(
        f"""
        <div class="hero">
            <div class="section-kicker">CAMPUSSPEND PRESENTS</div>
            <div class="hero-title">
                YOUR MONTH.<br>
                YOUR <span class="accent">MONEY STORY.</span>
            </div>
            <div class="hero-subtitle">
                {month_label(selected_month)} · A little look at
                where your money went.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- TOTAL SPENDING STORY ----------
    st.markdown(
        """
        <div class="section-kicker">01 / THE BIG NUMBER</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="story-card story-purple">
            <div class="card-title">YOU SPENT</div>
            <div class="big-number">{money(total_spent)}</div>
            <div class="card-note">
                Your spending, summed up in one number.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- BUDGET STORY ----------
    st.markdown(
        """
        <div class="section-kicker">02 / THE BUDGET CHECK</div>
        """,
        unsafe_allow_html=True,
    )

    budget_col, reflection_col = st.columns([1, 1.2], gap="large")

    with budget_col:
        st.markdown(
            f"""
            <div class="story-card story-orange">
                <div class="card-title">MONTHLY BUDGET</div>
                <div class="card-value">{money(selected_budget)}</div>
                <div class="card-note">
                    {budget_percentage:.1f}% of your budget used
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(min(max(budget_percentage / 100, 0.0), 1.0))

    with reflection_col:
        if total_spent > selected_budget:
            difference = total_spent - selected_budget
            reflection_title = "A LITTLE OVER THE LINE"
            reflection_message = (
                f"You went over budget by {money(difference)}. "
                "Use this as a signal for next month, not a reason "
                "to beat yourself up."
            )
            reflection_class = "story-pink"
        elif total_spent > 0:
            difference = selected_budget - total_spent
            reflection_title = "YOU KEPT IT IN CHECK"
            reflection_message = (
                f"You have {money(difference)} left in your budget. "
                "That's money you didn't need to spend this month."
            )
            reflection_class = "story-lime"
        else:
            reflection_title = "A FRESH PAGE"
            reflection_message = (
                "No expenses recorded for this month yet. "
                "Your money story is waiting to be written."
            )
            reflection_class = "story-purple"

        st.markdown(
            f"""
            <div class="story-card {reflection_class}">
                <div class="card-title">YOUR BUDGET VIBE</div>
                <div class="card-value">{reflection_title}</div>
                <div class="card-note">{reflection_message}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---------- CATEGORY PERSONALITY ----------
    st.markdown(
        """
        <div class="section-kicker">03 / THE MAIN CHARACTER</div>
        <div style="color:#b9b1c3; margin-bottom:1.4rem; line-height:1.6;">
            Every month has a main character. Here's yours.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if category_totals and total_spent > 0:
        sorted_categories = sorted(
            category_totals.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        top_share = top_amount / total_spent * 100

        category_col, detail_col = st.columns(
            [0.9, 1.1],
            gap="large",
        )

        # ---------- FEATURED CATEGORY ----------
        with category_col:
            st.markdown(
                f"""
                <div style="
                    min-height:300px;
                    padding:28px;
                    border-radius:26px;
                    background:
                        radial-gradient(circle at 90% 10%,
                            rgba(255,255,255,0.18), transparent 40%),
                        linear-gradient(145deg, #ff91c8, #a78bfa);
                    color:#211329;
                    display:flex;
                    flex-direction:column;
                    justify-content:space-between;
                    border:1px solid rgba(255,255,255,0.2);
                ">
                    <div>
                        <div style="
                            font-family:'DM Mono',monospace;
                            font-size:0.75rem;
                            letter-spacing:0.14em;
                            opacity:0.8;
                        ">YOUR NUMBER ONE</div>
                        <div style="
                            font-size:clamp(2rem,4vw,3.3rem);
                            font-weight:700;
                            letter-spacing:-0.06em;
                            line-height:1.05;
                            margin-top:22px;
                            overflow-wrap:anywhere;
                        ">{top_category}</div>
                    </div>
                    <div>
                        <div style="
                            font-size:clamp(2.3rem,5vw,4rem);
                            font-weight:700;
                            letter-spacing:-0.07em;
                            line-height:1.1;
                            margin-bottom:12px;
                            overflow-wrap:anywhere;
                        ">{money(top_amount)}</div>
                        <div style="
                            display:inline-block;
                            padding:8px 12px;
                            border-radius:999px;
                            background:rgba(33,19,41,0.12);
                            font-size:0.9rem;
                            font-weight:600;
                        ">{top_share:.1f}% of your total spending</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ---------- SPENDING LINEUP ----------
        with detail_col:
            st.markdown(
                """
                <div class="section-kicker" style="margin-top:0.3rem;">
                    THE SPENDING LINEUP
                </div>
                <div style="
                    color:#b9b1c3;
                    font-size:0.9rem;
                    margin-bottom:1.3rem;
                    line-height:1.5;
                ">
                    Where your money went, ranked from highest to lowest.
                </div>
                """,
                unsafe_allow_html=True,
            )

            accent_colours = [
                "#d8ff3e",
                "#a78bfa",
                "#ff965c",
                "#ff6fb5",
            ]

            for index, (category_name, amount) in enumerate(
                sorted_categories,
                start=1,
            ):
                share = amount / total_spent * 100
                bar_width = max(0, min(share, 100))
                bar_colour = accent_colours[(index - 1) % len(accent_colours)]

                st.markdown(
                    f"""
                    <div style="
                        padding:14px 16px;
                        margin-bottom:12px;
                        border:1px solid rgba(255,255,255,0.10);
                        border-radius:16px;
                        background:rgba(255,255,255,0.035);
                    ">
                        <div style="
                            display:flex;
                            justify-content:space-between;
                            align-items:center;
                            gap:12px;
                            margin-bottom:10px;
                        ">
                            <div style="min-width:0;">
                                <span style="
                                    color:#b9b1c3;
                                    font-family:'DM Mono',monospace;
                                    font-size:0.75rem;
                                ">{index:02}</span>
                                <span style="margin-left:8px;font-weight:600;">
                                    {category_name}
                                </span>
                            </div>
                            <strong style="white-space:nowrap;">
                                {money(amount)}
                            </strong>
                        </div>
                        <div style="
                            height:6px;
                            border-radius:99px;
                            background:rgba(255,255,255,0.09);
                            overflow:hidden;
                        ">
                            <div style="
                                width:{bar_width:.2f}%;
                                height:100%;
                                border-radius:99px;
                                background:{bar_colour};
                            "></div>
                        </div>
                        <div style="
                            color:#b9b1c3;
                            font-size:0.78rem;
                            margin-top:7px;
                        ">{share:.1f}% of monthly spending</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # ---------- FULL CATEGORY CHART ----------
        st.markdown(
            """
            <div style="margin-top:2.8rem;">
                <div class="section-kicker">THE FULL PICTURE</div>
                <div style="
                    font-size:1.7rem;
                    font-weight:700;
                    letter-spacing:-0.045em;
                    margin-bottom:0.4rem;
                ">Your money, visualised.</div>
                <div style="
                    color:#b9b1c3;
                    margin-bottom:1rem;
                    line-height:1.6;
                ">
                    Compare your spending across every category.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            show_wrapped_category_chart(category_totals)

        # ---------- THINGS WORTH NOTICING ----------
        st.markdown(
            """
            <div class="section-kicker" style="margin-top:3rem;">
                04 / THINGS WORTH NOTICING
            </div>
            <div style="
                color:#b9b1c3;
                margin-bottom:1.5rem;
                line-height:1.6;
            ">
                Three little takeaways from your spending this month.
            </div>
            """,
            unsafe_allow_html=True,
        )

        transaction_count = wrapped.get(
            "transaction_count",
            sum(
                1
                for expense in expenses
                if expense.get("date", "")[:7] == selected_month
            ),
        )

        insights = [
            (
                "YOUR BIGGEST",
                top_category,
                f"You spent {money(top_amount)} here.",
                "#ff91c8",
            ),
            (
                "YOUR SHARE",
                f"{top_share:.1f}%",
                "of your total spending went to your top category.",
                "#d8ff3e",
            ),
            (
                "YOUR TRANSACTIONS",
                str(transaction_count),
                "individual expenses made up this month's story.",
                "#a78bfa",
            ),
        ]

        insight_cols = st.columns(3, gap="large")

        for col, (label, value, note, accent) in zip(
            insight_cols,
            insights,
        ):
            with col:
                st.markdown(
                    f"""
                    <div style="
                        box-sizing:border-box;
                        min-height:205px;
                        height:100%;
                        padding:26px 22px;
                        border-radius:22px;
                        border:1px solid rgba(255,255,255,0.12);
                        background:linear-gradient(
                            155deg,
                            rgba(167,139,250,0.13),
                            rgba(36,24,46,0.95) 75%
                        );
                    ">
                        <div style="
                            color:{accent};
                            font-family:'DM Mono',monospace;
                            font-size:0.72rem;
                            letter-spacing:0.1em;
                            line-height:1.5;
                            min-height:2.2rem;
                        ">{label}</div>
                        <div style="
                            font-size:clamp(1.6rem,2.5vw,2.5rem);
                            font-weight:700;
                            letter-spacing:-0.055em;
                            line-height:1.15;
                            overflow-wrap:anywhere;
                            margin:18px 0;
                        ">{value}</div>
                        <div style="
                            color:#b9b1c3;
                            font-size:0.88rem;
                            line-height:1.7;
                        ">{note}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    else:
        st.markdown(
            """
            <div class="story-card violet">
                <div class="eyebrow">YOUR STORY IS WAITING</div>
                <div class="card-value">No main character yet.</div>
                <div class="card-note">
                    Add some expenses and your category personality
                    will show up here.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# ANNUAL WRAPPED
# ============================================================


elif page == "Annual Wrapped":

    # ============================================================
    # ANNUAL WRAPPED — YOUR YEAR IN MONEY
    # ============================================================

    # Available years
    years = sorted(
        {
            expense["date"][:4]
            for expense in expenses
            if isinstance(expense.get("date"), str) and len(expense["date"]) >= 4
        }
    )

    current_year = str(date.today().year)

    if current_year not in years:
        years.append(current_year)

    years = sorted(set(years), reverse=True)

    selected_year = st.selectbox(
        "Choose your year",
        years,
        key="annual_wrapped_year",
    )

    # Generate yearly summary
    wrapped = generate_annual_wrapped(expenses, selected_year)

    year_expenses = [
        expense
        for expense in expenses
        if isinstance(expense.get("date"), str)
        and expense["date"].startswith(selected_year + "-")
    ]

    active_months = len(wrapped["monthly_totals"])
    total_spent = wrapped["total_spent"]
    transaction_count = len(year_expenses)

    # ------------------------------------------------------------
    # OPENING HERO
    # ------------------------------------------------------------

    st.html(f"""
    <div style="
        background:linear-gradient(135deg,#2B1B3A 0%,#17101F 65%);
        border:1px solid rgba(216,255,62,0.28);
        border-radius:26px;
        padding:clamp(24px,5vw,52px);
        margin:12px 0 28px 0;
    ">
        <div style="
            color:#D8FF3E;
            font-family:'DM Mono',monospace;
            font-size:0.78rem;
            letter-spacing:0.16em;
            margin-bottom:28px;
        ">
            CAMPUSSPEND PRESENTS
        </div>

        <div style="
            font-size:clamp(2.8rem,8vw,6.2rem);
            font-weight:700;
            letter-spacing:-0.075em;
            line-height:0.91;
            color:#F8F5F2;
        ">
            YOUR YEAR.
        </div>

        <div style="
            font-size:clamp(2.5rem,7vw,5.5rem);
            font-weight:700;
            letter-spacing:-0.075em;
            line-height:1.02;
            color:#D8FF3E;
            margin-top:8px;
        ">
            YOUR MONEY<br/>STORY.
        </div>

        <div style="
            color:#B9B1C3;
            font-size:1rem;
            margin-top:26px;
            line-height:1.6;
        ">
            {selected_year} · A whole year of little purchases,
            big spends, and everything in between.
        </div>

        <div style="
            color:#A78BFA;
            font-family:'DM Mono',monospace;
            font-size:0.75rem;
            letter-spacing:0.12em;
            margin-top:24px;
        ">
            YOUR YEAR, UNPACKED ↘
        </div>
    </div>
    """)

    # ------------------------------------------------------------
    # BIG ANNUAL SPENDING REVEAL
    # ------------------------------------------------------------

    st.html("""
        <div style="
            color:#B9B1C3;
            font-family:'DM Mono',monospace;
            font-size:0.75rem;
            letter-spacing:0.13em;
            margin-bottom:8px;
        ">
            FIRST UP — THE BIG NUMBER
        </div>
        """)

    st.html(f"""
        <div style="
            background:#24182E;
            border:1px solid rgba(255,255,255,0.12);
            border-radius:22px;
            padding:26px;
            margin-bottom:18px;
        ">
            <div style="
                color:#B9B1C3;
                font-size:0.95rem;
                margin-bottom:8px;
            ">
                You spent in {selected_year}
            </div>

            <div style="
                color:#D8FF3E;
                font-size:clamp(2.5rem,7vw,5rem);
                font-weight:700;
                letter-spacing:-0.065em;
                line-height:1.1;
                overflow-wrap:anywhere;
            ">
                {money(total_spent)}
            </div>

            <div style="
                color:#B9B1C3;
                font-size:0.9rem;
                margin-top:14px;
            ">
                Across {transaction_count} transactions
                and {active_months} active {
                    "month" if active_months == 1 else "months"
                }.
            </div>
        </div>
        """)

    metric_col1, metric_col2 = st.columns(2, gap="large")

    with metric_col1:
        st.html(f"""
            <div style="
                background:#24182E;
                border:1px solid rgba(167,139,250,0.35);
                border-radius:18px;
                padding:20px;
                min-height:135px;
            ">
                <div style="color:#B9B1C3;font-size:0.85rem;">
                    AVERAGE PER ACTIVE MONTH
                </div>

                <div style="
                    color:#A78BFA;
                    font-size:clamp(1.5rem,3vw,2.3rem);
                    font-weight:700;
                    letter-spacing:-0.05em;
                    margin-top:12px;
                    overflow-wrap:anywhere;
                ">
                    {money(wrapped["average_monthly_spending"])}
                </div>
            </div>
            """)

    with metric_col2:
        st.html(f"""
            <div style="
                background:#24182E;
                border:1px solid rgba(255,111,181,0.35);
                border-radius:18px;
                padding:20px;
                min-height:135px;
            ">
                <div style="color:#B9B1C3;font-size:0.85rem;">
                    TRANSACTIONS LOGGED
                </div>

                <div style="
                    color:#FF6FB5;
                    font-size:clamp(1.5rem,3vw,2.3rem);
                    font-weight:700;
                    letter-spacing:-0.05em;
                    margin-top:12px;
                ">
                    {transaction_count}
                </div>
            </div>
            """)

    st.html("<div style='height:24px;'></div>")

    # ------------------------------------------------------------
    # YOUR YEARLY SUPERLATIVES
    # ------------------------------------------------------------

    st.html("""
        <div style="
            color:#B9B1C3;
            font-family:'DM Mono',monospace;
            font-size:0.75rem;
            letter-spacing:0.13em;
            margin-bottom:12px;
        ">
            YOUR SPENDING PERSONALITY
        </div>
        """)

    highlight_left, highlight_right = st.columns(2, gap="large")

    with highlight_left:
        if wrapped["top_category"] is not None:
            st.html(f"""
                <div style="
                    background:linear-gradient(145deg,#D8FF3E,#B6DA32);
                    color:#17101F;
                    border-radius:22px;
                    padding:24px;
                    min-height:205px;
                ">
                    <div style="
                        font-family:'DM Mono',monospace;
                        font-size:0.72rem;
                        letter-spacing:0.1em;
                    ">
                        THE CATEGORY CHAMPION 🏆
                    </div>

                    <div style="
                        font-size:clamp(1.8rem,4vw,3rem);
                        font-weight:700;
                        letter-spacing:-0.06em;
                        line-height:1.05;
                        margin-top:26px;
                        overflow-wrap:anywhere;
                    ">
                        {wrapped["top_category"]}
                    </div>

                    <div style="
                        font-size:1.15rem;
                        font-weight:600;
                        margin-top:12px;
                    ">
                        {money(wrapped["top_amount"])}
                    </div>

                    <div style="font-size:0.82rem;margin-top:6px;">
                        Your biggest spending category
                    </div>
                </div>
                """)
        else:
            st.info("Your category champion will appear when you track expenses.")

    with highlight_right:
        if wrapped["highest_month"] is not None:
            st.html(f"""
                <div style="
                    background:linear-gradient(145deg,#A78BFA,#8064D6);
                    color:#17101F;
                    border-radius:22px;
                    padding:24px;
                    min-height:205px;
                ">
                    <div style="
                        font-family:'DM Mono',monospace;
                        font-size:0.72rem;
                        letter-spacing:0.1em;
                    ">
                        THE BIG SPENDING MONTH ⚡
                    </div>

                    <div style="
                        font-size:clamp(1.6rem,3.5vw,2.5rem);
                        font-weight:700;
                        letter-spacing:-0.06em;
                        line-height:1.05;
                        margin-top:26px;
                    ">
                        {month_label(wrapped["highest_month"])}
                    </div>

                    <div style="
                        font-size:1.15rem;
                        font-weight:600;
                        margin-top:12px;
                    ">
                        {money(wrapped["highest_month_amount"])}
                    </div>

                    <div style="font-size:0.82rem;margin-top:6px;">
                        Your highest-spending month
                    </div>
                </div>
                """)
        else:
            st.info("Your biggest month will appear when you track expenses.")

    # ------------------------------------------------------------
    # CATEGORY CHART
    # ------------------------------------------------------------

    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style="
            color:#B9B1C3;
            font-family:'DM Mono',monospace;
            font-size:0.75rem;
            letter-spacing:0.13em;
        ">
            CHAPTER 01
        </div>
        <div style="
            font-size:clamp(2rem,5vw,3.5rem);
            font-weight:700;
            letter-spacing:-0.065em;
            line-height:1;
            margin-top:8px;
            margin-bottom:8px;
        ">
            WHERE IT WENT.
        </div>
        <div style="color:#B9B1C3;margin-bottom:18px;">
            The categories that made up your {selected_year}.
        </div>
        """,
        unsafe_allow_html=True,
    )

    show_wrapped_category_chart(wrapped["category_totals"])

    # ------------------------------------------------------------
    # MONTHLY SPENDING TREND
    # ------------------------------------------------------------

    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="
            color:#B9B1C3;
            font-family:'DM Mono',monospace;
            font-size:0.75rem;
            letter-spacing:0.13em;
        ">
            CHAPTER 02
        </div>
        <div style="
            font-size:clamp(2rem,5vw,3.5rem);
            font-weight:700;
            letter-spacing:-0.065em;
            line-height:1;
            margin-top:8px;
            margin-bottom:8px;
        ">
            THE MONTHLY PLOT TWIST.
        </div>
        <div style="color:#B9B1C3;margin-bottom:18px;">
            Every month had its own story. Here's how they compare.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if wrapped["monthly_totals"]:
        show_annual_monthly_charts(wrapped["monthly_totals"])
    else:
        st.info("Your monthly story will appear here as you track expenses.")

        # ------------------------------------------------------------
    # CLOSING YEAR IN REVIEW
    # ------------------------------------------------------------

    st.html("<div style='height:28px;'></div>")

    if total_spent > 0:
        share = (
            wrapped["top_amount"] / total_spent * 100
            if wrapped["top_category"] is not None
            else 0
        )

        category_sentence = (
            f"{wrapped['top_category']} took the lead, making up "
            f"{share:.1f}% of your annual spending."
            if wrapped["top_category"] is not None
            else "Keep tracking to discover your biggest category."
        )

        active_month_text = "month" if active_months == 1 else "months"

        st.html(f"""
            <div style="
                background:linear-gradient(135deg,#2B1B3A,#17101F);
                border:1px solid rgba(255,111,181,0.3);
                border-radius:26px;
                padding:clamp(24px,5vw,44px);
                margin-bottom:18px;
            ">
                <div style="
                    color:#FF6FB5;
                    font-family:'DM Mono',monospace;
                    font-size:0.75rem;
                    letter-spacing:0.13em;
                ">
                    THE FINAL RECAP
                </div>

                <div style="
                    font-size:clamp(2.2rem,6vw,4.5rem);
                    font-weight:700;
                    letter-spacing:-0.07em;
                    line-height:0.98;
                    margin-top:18px;
                    color:#F8F5F2;
                ">
                    THAT WAS<br/>YOUR {selected_year}.
                </div>

                <div style="
                    color:#F8F5F2;
                    font-size:1.05rem;
                    line-height:1.8;
                    margin-top:24px;
                ">
                    You logged <b>{transaction_count} transactions</b>,
                    spent <b>{money(total_spent)}</b>, and tracked
                    your money across
                    <b>{active_months} active {active_month_text}</b>.
                </div>

                <div style="
                    color:#D8FF3E;
                    font-size:1rem;
                    font-weight:600;
                    line-height:1.6;
                    margin-top:14px;
                ">
                    {category_sentence}
                </div>

                <div style="
                    color:#B9B1C3;
                    font-size:0.9rem;
                    line-height:1.7;
                    margin-top:20px;
                ">
                    Every entry tells you a little more about your habits.
                    Here's to being more intentional with your money,
                    one month at a time.
                </div>

                <div style="
                    color:#A78BFA;
                    font-family:'DM Mono',monospace;
                    font-size:0.75rem;
                    letter-spacing:0.12em;
                    margin-top:26px;
                ">
                    CAMPUSSPEND · END OF RECAP
                </div>
            </div>
            """)

    else:
        st.html(f"""
            <div style="
                background:#24182E;
                border:1px solid rgba(255,255,255,0.12);
                border-radius:24px;
                padding:30px;
                text-align:center;
            ">
                <div style="
                    color:#D8FF3E;
                    font-family:'DM Mono',monospace;
                    font-size:0.75rem;
                    letter-spacing:0.13em;
                ">
                    YOUR STORY IS WAITING
                </div>

                <div style="
                    color:#F8F5F2;
                    font-size:clamp(2rem,5vw,3.5rem);
                    font-weight:700;
                    letter-spacing:-0.06em;
                    margin-top:16px;
                ">
                    YOUR YEAR.<br/>YOUR STORY.
                </div>

                <div style="
                    color:#B9B1C3;
                    line-height:1.7;
                    margin-top:14px;
                ">
                    Add your first expense for {selected_year}.
                    Your Annual Wrapped will grow with every entry.
                </div>
            </div>
            """)
