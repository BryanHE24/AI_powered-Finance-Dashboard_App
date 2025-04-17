# src/generate_sample_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """
    Generate sample financial data for demo purposes.

    Returns:
        str: The filepath of the generated sample data.
    """
    np.random.seed(42)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    num_records = 1000
    dates = [start_date + timedelta(days=random.randint(0, 365)) for _ in range(num_records)]
    dates.sort()

    income_categories = [
        "Sales Revenue", "Consulting Fees", "Service Income",
        "Investment Returns", "Royalties", "Affiliate Income"
    ]

    expense_categories = [
        "Rent", "Utilities", "Salaries", "Marketing", "Software Subscriptions",
        "Office Supplies", "Insurance", "Travel", "Equipment", "Maintenance"
    ]

    records = []

    for i, date in enumerate(dates):
        is_income = random.random() < 0.6

        if is_income:
            category = random.choice(income_categories)
            amount = random.uniform(1000, 20000)
            transaction_type = "Income"
        else:
            category = random.choice(expense_categories)
            amount = random.uniform(100, 5000)
            transaction_type = "Expense"

        amount = round(amount, 2)

        month = date.month
        if month in [11, 12]:
            amount *= 1.2
        elif month in [1, 2]:
            amount *= 0.8

        records.append({
            "Date": date,
            "Category": category,
            "Description": f"{category} - Transaction {i+1}",
            "Amount": amount,
            "Type": transaction_type
        })

    df = pd.DataFrame(records)
    output_file = "data/sample_data.xlsx"
    df.to_excel(output_file, index=False)

    print(f"Sample data generated and saved to {output_file}")
    return output_file

if __name__ == "__main__":
    generate_sample_data()
