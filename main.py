
import streamlit as st
import pandas as pd

from datetime import date

from src.money_engine import (
    CATEGORIES,
    create_transaction,
    calculate_summary
)

from src.storage import (
    initialize_database,
    save_transaction,
    load_transactions
)


st.set_page_config(
    page_title="Explain My Bills",
    page_icon="💰",
    layout="wide"
)

CURRENCIES = ["NGN", "USD", "GBP", "EUR"]

initialize_database()


def money_coach(transactions, summary):
    """Generate spending insights from recorded information."""

    insights = []

    income = summary["income"]
    expenses = summary["expenses"]

    if income <= 0:
        return ["Add your income to unlock your spending analysis."]

    spending_percentage = expenses / income * 100

    if spending_percentage > 100:
        insights.append(
            "🚨 Your spending has exceeded your income. "
            "Your wallet needs an emergency meeting."
        )
    elif spending_percentage > 80:
        insights.append(
            "😬 Over 80% of your income is already spent. "
            "Your money is working overtime."
        )
    elif spending_percentage > 50:
        insights.append(
            "👀 More than half your income has been spent. "
            "Let's make sure you're getting something worthwhile."
        )
    else:
        insights.append(
            "👏 Your recorded spending is below half your income. "
            "Good start. Keep giving your money a purpose."
        )

    optional_spending = sum(
        item["amount"]
        for item in transactions
        if item["type"] == "Expense"
        and item["necessity"] == "Optional"
    )

    if optional_spending > 0:
        insights.append(
            f"😏 You've spent {optional_spending:,.2f} "
            "on optional purchases. "
            "Not every temptation needs a bank transfer."
        )

    low_value = [
        item for item in transactions
        if item["type"] == "Expense"
        and item["value_rating"] in (1, 2)
    ]

    if low_value:
        total = sum(item["amount"] for item in low_value)

        insights.append(
            f"⚠️ You rated {len(low_value)} purchase(s) "
            f"as low value, totalling {total:,.2f}. "
            "Let's investigate whether those expenses can be reduced."
        )

    unused = [
        item for item in transactions
        if item["type"] == "Expense"
        and item["usage_frequency"] == "Never"
    ]

    if unused:
        insights.append(
            f"🫠 You recorded {len(unused)} expense(s) "
            "for things you never use. "
            "That's money paying rent in an empty apartment."
        )

    if summary["balance"] < 0:
        insights.append(
            "🚨 Your recorded outflows exceed your income. "
            "Pause optional spending and review upcoming commitments."
        )

    return insights


def spending_plan(summary):
    """Create a simple illustrative plan for remaining money."""

    remaining = max(summary["balance"], 0)

    return {
        "Essentials": round(remaining * 0.50, 2),
        "Savings": round(remaining * 0.30, 2),
        "Personal spending": round(remaining * 0.20, 2)
    }


def main():

    st.title("💰 Explain My Bills")

    st.caption(
        "Know where your money goes. "
        "Know what it's worth. Spend smarter."
    )

    transactions = load_transactions()

    st.divider()

    st.header("➕ Record a transaction")

    with st.form("transaction_form"):

        title = st.text_input(
            "What did you spend or receive money for?",
            placeholder="e.g. Groceries, transport, salary"
        )

        col1, col2 = st.columns(2)

        with col1:
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=500.0
            )

            transaction_type = st.selectbox(
                "Transaction type",
                ["Expense", "Income", "Transfer"]
            )

            category = st.selectbox(
                "Category",
                list(CATEGORIES.keys())
            )

            currency = st.selectbox(
                "Currency",
                CURRENCIES
            )

        with col2:
            transaction_date = st.date_input(
                "Date",
                value=date.today()
            )

            necessity = st.selectbox(
                "Was this spending necessary?",
                ["Essential", "Optional", "Emergency", "Not specified"]
            )

            usage_frequency = st.selectbox(
                "How frequently do you use it?",
                ["Daily", "Weekly", "Monthly", "Rarely", "Never", "Not specified"]
            )

            value_rating = st.select_slider(
                "How valuable was it?",
                options=[0, 1, 2, 3, 4, 5],
                value=0,
                format_func=lambda x: (
                    "Not rated" if x == 0
                    else f"{x}/5"
                )
            )

        purpose = st.text_area(
            "What was the money actually used for?",
            placeholder="Explain what you paid for and why..."
        )

        notes = st.text_input(
            "Additional notes (optional)"
        )

        submitted = st.form_submit_button(
            "Save Transaction",
            use_container_width=True
        )

        if submitted:

            try:
                transaction = create_transaction(
                    title=title,
                    amount=amount,
                    transaction_type=transaction_type,
                    category=category,
                    currency=currency,
                    transaction_date=transaction_date.isoformat(),
                    notes=notes
                )

                transaction["purpose"] = purpose
                transaction["necessity"] = necessity
                transaction["usage_frequency"] = usage_frequency
                transaction["value_rating"] = value_rating

                save_transaction(transaction)

                st.success("Transaction saved successfully!")
                st.rerun()

            except ValueError as error:
                st.error(str(error))

    st.divider()

    st.header("📊 Your Money Dashboard")

    if not transactions:
        st.info("Start recording transactions to see your financial picture.")
        return

    selected_currency = st.selectbox(
        "Analysis currency",
        CURRENCIES
    )

    summary = calculate_summary(
        transactions,
        selected_currency
    )

    columns = st.columns(3)

    columns[0].metric(
        "Income",
        f"{selected_currency} {summary['income']:,.2f}"
    )

    columns[1].metric(
        "Expenses",
        f"{selected_currency} {summary['expenses']:,.2f}"
    )

    columns[2].metric(
        "Remaining balance",
        f"{selected_currency} {summary['balance']:,.2f}"
    )

    st.caption(
        "Transfers are excluded from expense totals but reduce "
        "the available balance."
    )

    st.divider()

    st.header("🔍 Where Your Money Goes")

    category_totals = summary["category_totals"]

    if category_totals:

        chart_data = pd.DataFrame(
            list(category_totals.items()),
            columns=["Category", "Amount"]
        ).sort_values("Amount", ascending=False)

        st.bar_chart(
            chart_data.set_index("Category")
        )

        st.dataframe(
            chart_data,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No spending recorded in this currency.")

    st.divider()

    st.header("🧠 What Your Money Actually Did")

    matching = [
        item for item in transactions
        if item["currency"] == selected_currency
        and item["type"] == "Expense"
    ]

    if matching:

        for item in matching:

            with st.expander(
                f"{item['title']} — {selected_currency} {item['amount']:,.2f}"
            ):

                st.write("**Category:**", item["category"])
                st.write("**Purpose:**", item["purpose"] or "Not provided")
                st.write("**Necessity:**", item["necessity"])
                st.write("**Usage:**", item["usage_frequency"])

                if item["value_rating"]:
                    st.write(
                        "**Your value rating:**",
                        f"{item['value_rating']}/5"
                    )
                else:
                    st.write("**Your value rating:** Not rated")

                if item["value_rating"] in (1, 2):
                    st.warning(
                        "You rated this purchase poorly. "
                        "Consider whether there is a better alternative."
                    )
                elif item["value_rating"] in (4, 5):
                    st.success(
                        "You consider this purchase valuable."
                    )

    else:
        st.info("No expense details available yet.")

    st.divider()

    st.header("😏 Your Money Coach")

    insights = money_coach(transactions, summary)

    for insight in insights:
        st.info(insight)

    st.divider()

    st.header("🗺️ Plan Your Remaining Money")

    if summary["balance"] > 0:

        plan = spending_plan(summary)

        st.write(
            "Here is an illustrative allocation of your remaining money:"
        )

        for name, value in plan.items():
            st.write(f"**{name}:** {selected_currency} {value:,.2f}")

        st.caption(
            "This is a suggested starting point, not a personalised "
            "financial plan. Upcoming bills and actual needs should "
            "be considered before allocating money."
        )

    else:
        st.warning(
            "Your available balance is zero or negative. "
            "Review your spending before making new optional purchases."
        )

    st.divider()

    st.header("📜 Transaction History")

    history = [
        item for item in transactions
        if item["currency"] == selected_currency
    ]

    if history:
        st.dataframe(
            pd.DataFrame(history),
            use_container_width=True,
            hide_index=True
        )

    st.caption(
        f"{len(transactions)} transactions permanently stored."
    )


if __name__ == "__main__":
    main()
