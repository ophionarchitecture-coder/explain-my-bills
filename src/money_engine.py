
from datetime import date
from collections import defaultdict

CATEGORIES = {
    "Food & Groceries": "Needs",
    "Transport": "Needs",
    "Housing": "Needs",
    "Utilities": "Needs",
    "Healthcare": "Needs",
    "Education": "Needs",
    "Communication": "Needs",
    "Shopping": "Wants",
    "Entertainment": "Wants",
    "Eating Out": "Wants",
    "Subscriptions": "Wants",
    "Personal Care": "Wants",
    "Gifts & Donations": "Wants",
    "Debt Repayment": "Commitments",
    "Bank Charges": "Commitments",
    "Insurance": "Commitments",
    "Savings": "Savings",
    "Investments": "Savings",
    "Other": "Other",
}


def create_transaction(
    title,
    amount,
    transaction_type,
    category,
    currency="NGN",
    transaction_date=None,
    notes=""
):
    """Create and validate a financial transaction."""

    if not title.strip():
        raise ValueError("Transaction title is required.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    if transaction_type not in [
        "Income", "Expense", "Transfer"
    ]:
        raise ValueError("Invalid transaction type.")

    if category not in CATEGORIES and category != "Other":
        raise ValueError("Invalid category.")

    if transaction_date is None:
        transaction_date = date.today().isoformat()

    return {
        "title": title.strip(),
        "amount": round(float(amount), 2),
        "type": transaction_type,
        "category": category,
        "group": CATEGORIES.get(category, "Other"),
        "currency": currency,
        "date": transaction_date,
        "notes": notes.strip()
    }


def calculate_summary(transactions, currency="NGN"):
    """Calculate income, spending, savings and balance."""

    income = 0
    expenses = 0
    transfers = 0
    savings = 0
    category_totals = defaultdict(float)

    for transaction in transactions:
        if transaction["currency"] != currency:
            continue

        amount = transaction["amount"]
        category = transaction["category"]

        if transaction["type"] == "Income":
            income += amount

        elif transaction["type"] == "Expense":
            expenses += amount
            category_totals[category] += amount

            if category == "Savings":
                savings += amount

        elif transaction["type"] == "Transfer":
            transfers += amount

    return {
        "income": round(income, 2),
        "expenses": round(expenses, 2),
        "transfers": round(transfers, 2),
        "savings": round(savings, 2),
        "balance": round(income - expenses - transfers, 2),
        "category_totals": dict(category_totals)
    }


def get_spending_insights(summary):
    """Generate simple spending observations."""

    insights = []

    income = summary["income"]
    expenses = summary["expenses"]
    savings = summary["savings"]

    if income == 0:
        insights.append(
            "No income has been recorded yet. "
            "Add your income to get a meaningful spending analysis."
        )
        return insights

    spending_ratio = (expenses / income) * 100

    if spending_ratio > 90:
        insights.append(
            "You're spending over 90% of your recorded income. "
            "Your money barely gets time to breathe."
        )
    elif spending_ratio > 70:
        insights.append(
            "More than 70% of your income is going out. "
            "Let's examine where it goes."
        )
    else:
        insights.append(
            "Your recorded spending is below 70% of your income. "
            "Keep monitoring it."
        )

    if savings == 0:
        insights.append(
            "No savings contributions recorded. "
            "Even a small, consistent amount can help."
        )

    if summary["balance"] < 0:
        insights.append(
            "Warning: recorded outflows exceed recorded income."
        )

    if summary["category_totals"]:
        highest = max(
            summary["category_totals"],
            key=summary["category_totals"].get
        )
        highest_amount = summary["category_totals"][highest]

        insights.append(
            f"Your highest recorded spending category is "
            f"{highest}: {highest_amount:,.2f} {summary['currency'] if 'currency' in summary else ''}."
        )

    return insights
