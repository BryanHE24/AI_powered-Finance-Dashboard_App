# processor.py
import pandas as pd
import numpy as np
from datetime import datetime

def process_data(df):
    """Process the uploaded Excel file and prepare data for visualization"""
    # Ensure we have Date and Type columns
    if 'Date' not in df.columns:
        # Try to guess which column might be the date
        date_candidates = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_candidates:
            df['Date'] = df[date_candidates[0]]
        else:
            # Create a dummy date column if none exists
            df['Date'] = pd.to_datetime('today')

    if 'Type' not in df.columns:
        # Try to determine transaction types based on amount
        amount_candidates = [col for col in df.columns if 'amount' in col.lower() or 'value' in col.lower()]
        if amount_candidates:
            # Positive amounts are income, negative are expenses
            df['Type'] = df[amount_candidates[0]].apply(lambda x: 'Income' if x >= 0 else 'Expense')
            # Make all amounts positive for easier processing
            df['Amount'] = df[amount_candidates[0]].abs()
        else:
            # Create dummy Type and Amount columns
            df['Type'] = 'Income'  # Default all to income
            df['Amount'] = 1000    # Default amount
    elif 'Amount' not in df.columns:
        # Try to find an amount column
        amount_candidates = [col for col in df.columns if 'amount' in col.lower() or 'value' in col.lower()]
        if amount_candidates:
            df['Amount'] = df[amount_candidates[0]]
        else:
            # Create a dummy amount
            df['Amount'] = 1000

    # Ensure Date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Add Month column for aggregation
    df['Month'] = df['Date'].dt.strftime('%b-%y')

    return df

def get_kpis(df):
    """Extract key performance indicators from data"""
    total_income = df[df['Type'] == 'Income']['Amount'].sum()
    total_expense = df[df['Type'] == 'Expense']['Amount'].sum() if 'Expense' in df['Type'].unique() else 0

    # Calculate month-over-month growth
    if 'Date' in df.columns:
        df['Month'] = df['Date'].dt.strftime('%Y-%m')
        monthly = df.groupby(['Month', 'Type'])['Amount'].sum().reset_index()

        # Get the last two months if available
        months = sorted(monthly['Month'].unique())
        if len(months) >= 2:
            current = monthly[(monthly['Month'] == months[-1]) & (monthly['Type'] == 'Income')]['Amount'].sum()
            previous = monthly[(monthly['Month'] == months[-2]) & (monthly['Type'] == 'Income')]['Amount'].sum()
            growth = ((current - previous) / previous * 100) if previous > 0 else 0
        else:
            growth = 0
    else:
        growth = 0

    return {
        'income': total_income,
        'expense': total_expense,
        'profit': total_income - total_expense,
        'growth': growth
    }

def generate_chart_data(df):
    """Generate data for the main chart"""
    # Ensure we have month data
    if 'Month' not in df.columns and 'Date' in df.columns:
        df['Month'] = df['Date'].dt.strftime('%b-%y')

    # If no Month or Date columns exist, create sample data
    if 'Month' not in df.columns:
        months = ['Dec-22', 'Jan-23', 'Feb-23', 'Mar-23', 'Apr-23', 'May-23',
                  'Jun-23', 'Jul-23', 'Aug-23', 'Sep-23', 'Oct-23', 'Dec-23']
        return {
            'months': months,
            'income': {m: np.random.randint(50000, 150000) for m in months},
            'expense': {m: np.random.randint(30000, 70000) for m in months}
        }

    # Real data processing
    monthly = df.groupby(['Month', 'Type'])['Amount'].sum().reset_index()

    # Get all unique months
    months = sorted(monthly['Month'].unique())

    # Aggregate income and expense by month
    income_by_month = {}
    expense_by_month = {}

    for month in months:
        income = monthly[(monthly['Month'] == month) & (monthly['Type'] == 'Income')]['Amount'].sum()
        income_by_month[month] = income

        expense = monthly[(monthly['Month'] == month) & (monthly['Type'] == 'Expense')]['Amount'].sum()
        expense_by_month[month] = expense

    return {
        'months': months,
        'income': income_by_month,
        'expense': expense_by_month
    }
