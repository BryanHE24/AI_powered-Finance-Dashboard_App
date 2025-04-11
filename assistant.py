# assistant.py
import os
import pandas as pd
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now this should work
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_assistant(prompt, df):
    """Interact with OpenAI GPT to analyze financial data"""

    if not openai.api_key:
        return "Please set your OPENAI_API_KEY environment variable to use the AI assistant feature."

    try:
        # Generate a data summary for context
        data_summary = generate_data_summary(df)

        # Create a comprehensive prompt for the AI
        full_prompt = f"""You are a financial data analyst assistant helping with a finance dashboard.

 Here's a summary of the data:
 {data_summary}

 The user wants to know: {prompt}

 Provide a concise, helpful answer based on the financial data. If you need more specific data to answer accurately, mention what additional information would be helpful. Focus on insights rather than just stating numbers.
 """

        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a financial data assistant specializing in business analytics."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Sorry, I encountered an issue: {str(e)}"

def generate_data_summary(df):
    """Generate a summary of the financial data for the AI"""
    summary = []

    # Basic dataframe info
    summary.append(f"Dataset contains {len(df)} records.")

    # Column information
    summary.append(f"Columns: {', '.join(df.columns.tolist())}")

    # Time range if available
    if 'Date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Date']):
        min_date = df['Date'].min().strftime('%Y-%m-%d')
        max_date = df['Date'].max().strftime('%Y-%m-%d')
        summary.append(f"Date range: {min_date} to {max_date}")

    # Transaction types summary
    if 'Type' in df.columns:
        types = df['Type'].value_counts().to_dict()
        types_summary = ", ".join([f"{k}: {v}" for k, v in types.items()])
        summary.append(f"Transaction counts: {types_summary}")

    # Financial summaries
    if 'Amount' in df.columns:
        if 'Type' in df.columns:
            # Get amount by type
            for transaction_type in df['Type'].unique():
                amount_sum = df[df['Type'] == transaction_type]['Amount'].sum()
                summary.append(f"Total {transaction_type}: ${amount_sum:,.2f}")
        else:
            # Just total amount
            amount_sum = df['Amount'].sum()
            summary.append(f"Total Amount: ${amount_sum:,.2f}")

    return "\n".join(summary)

def generate_insights(df):
    """Generate automatic insights from financial data"""
    insights = []

    # Check if we have proper financial data
    if 'Type' in df.columns and 'Amount' in df.columns and 'Date' in df.columns:
        # Calculate profit margin
        income = df[df['Type'] == 'Income']['Amount'].sum()
        expense = df[df['Type'] == 'Expense']['Amount'].sum() if 'Expense' in df['Type'].unique() else 0

        if income > 0:
            profit_margin = (income - expense) / income * 100
            insights.append(f"Your current profit margin is {profit_margin:.1f}%.")

        # Month-over-month analysis
        df['Month'] = df['Date'].dt.strftime('%Y-%m')
        monthly = df.groupby(['Month', 'Type'])['Amount'].sum().reset_index()

        # Get months in order
        months = sorted(monthly['Month'].unique())

        if len(months) >= 2:
            # Compare last two months
            last_month = months[-1]
            prev_month = months[-2]

            last_income = monthly[(monthly['Month'] == last_month) & (monthly['Type'] == 'Income')]['Amount'].sum()
            prev_income = monthly[(monthly['Month'] == prev_month) & (monthly['Type'] == 'Income')]['Amount'].sum()

            if prev_income > 0:
                income_change = (last_income - prev_income) / prev_income * 100
                insights.append(f"Income {increase_or_decrease(income_change)} by {abs(income_change):.1f}% compared to previous month.")

            # Check expense growth if available
            if 'Expense' in df['Type'].unique():
                last_expense = monthly[(monthly['Month'] == last_month) & (monthly['Type'] == 'Expense')]['Amount'].sum()
                prev_expense = monthly[(monthly['Month'] == prev_month) & (monthly['Type'] == 'Expense')]['Amount'].sum()

                if prev_expense > 0:
                    expense_change = (last_expense - prev_expense) / prev_expense * 100
                    insights.append(f"Expenses {increase_or_decrease(expense_change)} by {abs(expense_change):.1f}% compared to previous month.")

    # Return default insight if we couldn't generate any
    if not insights:
        insights.append("Upload financial data with Date, Type, and Amount columns for automatic insights.")

    return insights

def increase_or_decrease(change):
    """Helper to generate increase/decrease text"""
    return "increased" if change >= 0 else "decreased"

def generate_summary(df):
    """Generate a written summary of the financial data using ChatGPT"""
    data_summary = generate_data_summary(df)

    prompt = f"""You are a financial analyst.
 Here's a summary of the data:
 {data_summary}

 Provide a written summary of the financial performance, including key insights, trends, and recommendations based on the data.
 """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a financial analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I encountered an issue: {str(e)}"
