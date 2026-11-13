
from datetime import date


def analyze_bill(bill, today=None):
    """Analyze payment deadline and status."""

    if today is None:
        today = date.today()

    due_date = date.fromisoformat(bill["due_date"])
    days_remaining = (due_date - today).days

    if days_remaining < 0:
        status = "OVERDUE"
        explanation = (
            f"This bill is {abs(days_remaining)} days overdue."
        )
    elif days_remaining == 0:
        status = "DUE TODAY"
        explanation = "This bill is due today."
    elif days_remaining <= 7:
        status = "DUE SOON"
        explanation = (
            f"This bill is due in {days_remaining} days."
        )
    else:
        status = "NOT YET DUE"
        explanation = (
            f"You have {days_remaining} days before payment is due."
        )

    return {
        "days_remaining": days_remaining,
        "status": status,
        "explanation": explanation
    }


def analyze_charges(charges, bill_total):
    """Check charge totals and detect repeated charge entries."""

    charge_total = sum(item["amount"] for item in charges)

    seen = set()
    duplicates = []

    for item in charges:
        key = (
            item["description"].strip().lower(),
            item["amount"]
        )

        if key in seen:
            duplicates.append(item["description"])
        else:
            seen.add(key)

    difference = round(bill_total - charge_total, 2)

    if abs(difference) < 0.01:
        total_status = "MATCH"
        explanation = "The listed charges add up to the bill total."
    else:
        total_status = "MISMATCH"
        explanation = (
            f"The listed charges differ from the bill total "
            f"by {abs(difference):,.2f}."
        )

    return {
        "charge_count": len(charges),
        "charge_total": round(charge_total, 2),
        "bill_total": round(bill_total, 2),
        "difference": difference,
        "total_status": total_status,
        "duplicates": duplicates,
        "explanation": explanation
    }
