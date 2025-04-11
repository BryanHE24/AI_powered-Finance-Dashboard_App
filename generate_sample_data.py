# generate_sample_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """Generate sample financial data for demo purposes"""
    # Set random seed for reproducibility
    np.random.seed(42)

    # Date range for the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    # Generate dates
    num_records = 1000
    dates = [start_date + timedelta(days=random.randint(0, 365)) for _ in range(num_records)]
    dates.sort()

    # Transaction categories
    income_categories = [
        "Sales Revenue", "Consulting Fees", "Service Income",
        "Investment Returns", "Royalties", "Affiliate Income"
    ]

    expense_categories = [
        "Rent", "Utilities", "Salaries", "Marketing", "Software Subscriptions",
        "Office Supplies", "Insurance", "Travel", "Equipment", "Maintenance"
    ]

    # Generate records
    records = []

    for i, date in enumerate(dates):
        # Determine if it's income or expense (60% chance for income)
        is_income = random.random() < 0.6

        if is_income:
            category = random.choice(income_categories)
            # Income amounts tend to be larger
            amount = random.uniform(1000, 20000)
            transaction_type = "Income"
        else:
            category = random.choice(expense_categories)
            # Expense amounts tend to be smaller
            amount = random.uniform(100, 5000)
            transaction_type = "Expense"

        # Round to 2 decimal places
        amount = round(amount, 2)

        # Add some seasonal variation
        month = date.month
        if month in [11, 12]:  # Holiday season
            amount *= 1.2  # 20% increase
        elif month in [1, 2]:  # Post-holiday slump
            amount *= 0.8  # 20% decrease

        # Add record
        records.append({
            "Date": date,
            "Category": category,
            "Description": f"{category} - Transaction {i+1}",
            "Amount": amount,
            "Type": transaction_type
        })

    # Convert to DataFrame
    df = pd.DataFrame(records)

    # Save to Excel
    output_file = "sample_data.xlsx"
    df.to_excel(output_file, index=False)

    print(f"Sample data generated and saved to {output_file}")
    return output_file

if __name__ == "__main__":
    generate_sample_data()
