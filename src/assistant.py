# assistant.py
import os
import pandas as pd
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_assistant(prompt, df):
    """
    Interact with OpenAI GPT to analyze financial data.

    Args:
        prompt (str): The user's query.
        df (pd.DataFrame): The DataFrame containing financial data.

    Returns:
        str: The response from the AI assistant.
    """
    if not openai.api_key:
        return "Please set your OPENAI_API_KEY environment variable to use the AI assistant feature."

    try:
        data_summary = generate_data_summary(df)
        full_prompt = f"""You are a financial data analyst assistant helping with a finance dashboard.

Here's a summary of the data:
{data_summary}

The user wants to know: {prompt}

Provide a concise, helpful answer based on the financial data. If you need more specific data to answer accurately, mention what additional information would be helpful. Focus on insights rather than just stating numbers.
"""

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

def generate_insights(df):
    """
    Generate automatic insights from financial data.

    Args:
        df (pd.DataFrame): The DataFrame containing financial data.

    Returns:
        list: A list of insights.
    """
    insights = []

    if 'Type' in df.columns and 'Amount' in df.columns and 'Date' in df.columns:
        income = df[df['Type'] == 'Income']['Amount'].sum()
        expense = df[df['Type'] == 'Expense']['Amount'].sum() if 'Expense' in df['Type'].unique() else 0

        if income > 0:
            profit_margin = (income - expense) / income * 100
            insights.append(f"Your current profit margin is {profit_margin:.1f}%. " +
                          (f"This is {'healthy' if profit_margin > 20 else 'concerning'}." if profit_margin != 0 else ""))

        if 'Date' in df.columns:
            df['Month'] = df['Date'].dt.strftime('%Y-%m')
            monthly = df.groupby(['Month', 'Type'])['Amount'].sum().reset_index()
            months = sorted(monthly['Month'].unique())
            if len(months) >= 2:
                last_month = months[-1]
                prev_month = months[-2]
                last_income = monthly[(monthly['Month'] == last_month) & (monthly['Type'] == 'Income')]['Amount'].sum()
                prev_income = monthly[(monthly['Month'] == prev_month) & (monthly['Type'] == 'Income')]['Amount'].sum()

                if prev_income > 0:
                    income_change = (last_income - prev_income) / prev_income * 100
                    insights.append(f"Income {increase_or_decrease(income_change)} by {abs(income_change):.1f}% compared to previous month.")

                    if income_change > 0:
                        insights.append("This positive trend suggests potential growth opportunities.")
                    else:
                        insights.append("This decline may require attention to revenue streams.")

                if 'Expense' in df['Type'].unique():
                    last_expense = monthly[(monthly['Month'] == last_month) & (monthly['Type'] == 'Expense')]['Amount'].sum()
                    prev_expense = monthly[(monthly['Month'] == prev_month) & (monthly['Type'] == 'Expense')]['Amount'].sum()

                    if prev_expense > 0:
                        expense_change = (last_expense - prev_expense) / prev_expense * 100
                        insights.append(f"Expenses {increase_or_decrease(expense_change)} by {abs(expense_change):.1f}% compared to previous month.")

                        if income_change > 0 and expense_change < 0:
                            insights.append("Great job! Income is rising while expenses are falling - this is optimal for profitability.")
                        elif income_change < 0 and expense_change > 0:
                            insights.append("Warning: Income is decreasing while expenses are increasing - this is squeezing your profit margin.")

        if 'Category' in df.columns:
            expense_by_category = df[df['Type'] == 'Expense'].groupby('Category')['Amount'].sum()
            if not expense_by_category.empty:
                top_expense = expense_by_category.idxmax()
                top_expense_amount = expense_by_category.max()
                percent_of_total = (top_expense_amount / expense) * 100 if expense > 0 else 0

                insights.append(f"Your largest expense category is '{top_expense}' at ${top_expense_amount:.2f} ({percent_of_total:.1f}% of total expenses).")

                if percent_of_total > 40:
                    insights.append(f"Consider reviewing your {top_expense} expenses as they represent a significant portion of your total costs.")

        if len(months) >= 6:
            df['MonthNum'] = df['Date'].dt.month
            month_analysis = df.groupby(['MonthNum', 'Type'])['Amount'].sum().reset_index()

            if len(month_analysis) > 0:
                income_by_month = month_analysis[month_analysis['Type'] == 'Income']
                if len(income_by_month) > 0:
                    peak_month = income_by_month.loc[income_by_month['Amount'].idxmax()]['MonthNum']
                    month_name = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                                 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
                    insights.append(f"Your peak income month appears to be {month_name[peak_month]}.")

    if not insights:
        insights.append("Upload financial data with Date, Type, and Amount columns for automatic insights.")

    return insights

def generate_summary(df):
    """
    Generate a well-formatted written summary of the financial data using ChatGPT.

    Args:
        df (pd.DataFrame): The DataFrame containing financial data.

    Returns:
        str: The formatted HTML summary.
    """
    data_summary = generate_data_summary(df)

    prompt = f"""You are a financial analyst.
Here's a summary of the data:
{data_summary}

Provide a written summary of the financial performance, including key insights, trends, and recommendations.
Format your response as plain text with clear sections. DO NOT use Markdown formatting.

- Use simple formatting - no special characters
- Use clear section headers in ALL CAPS followed by a colon
- Use simple numbering for lists (1., 2., etc.)
- Express all numbers using standard formatting with commas (e.g., $1,234,567.89)
- Keep paragraphs short and focused
- Include 3-4 specific, actionable recommendations

Structure your response with these sections:
- OVERVIEW OF FINANCIAL PERFORMANCE
- KEY INCOME AND EXPENSE ANALYSIS
- NOTABLE TRENDS
- RECOMMENDATIONS
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a financial analyst creating clear, well-structured reports with plain text formatting only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )
        summary_text = response.choices[0].message.content

        paragraphs = summary_text.split('\n\n')
        formatted_paragraphs = []

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            if paragraph.isupper() and ':' in paragraph:
                header = paragraph.replace(':', '')
                formatted_paragraphs.append(f"<h3 style='color:#F6E05E; margin-top:20px; margin-bottom:10px;'>{header}</h3>")
            else:
                formatted_paragraphs.append(f"<p style='margin-bottom:15px; line-height:1.5;'>{paragraph}</p>")

        formatted_html = "\n".join(formatted_paragraphs)

        return formatted_html
    except Exception as e:
        return f"<p>Sorry, I encountered an issue generating the summary: {str(e)}</p>"

def generate_data_summary(df):
    """
    Generate a summary of the financial data for the AI.

    Args:
        df (pd.DataFrame): The DataFrame containing financial data.

    Returns:
        str: The data summary.
    """
    summary = []

    summary.append(f"Dataset contains {len(df)} records.")
    summary.append(f"Columns: {', '.join(df.columns.tolist())}")

    if 'Date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Date']):
        min_date = df['Date'].min().strftime('%Y-%m-%d')
        max_date = df['Date'].max().strftime('%Y-%m-%d')
        summary.append(f"Date range: {min_date} to {max_date}")

    if 'Type' in df.columns:
        types = df['Type'].value_counts().to_dict()
        types_summary = ", ".join([f"{k}: {v}" for k, v in types.items()])
        summary.append(f"Transaction counts: {types_summary}")

    if 'Amount' in df.columns:
        if 'Type' in df.columns:
            for transaction_type in df['Type'].unique():
                amount_sum = df[df['Type'] == transaction_type]['Amount'].sum()
                summary.append(f"Total {transaction_type}: ${amount_sum:,.2f}")
        else:
            amount_sum = df['Amount'].sum()
            summary.append(f"Total Amount: ${amount_sum:,.2f}")

    if 'Category' in df.columns:
        category_amounts = df.groupby(['Category', 'Type'])['Amount'].sum().reset_index()
        top_categories = category_amounts.sort_values('Amount', ascending=False).head(5)
        summary.append("Top 5 categories by amount:")
        for _, row in top_categories.iterrows():
            summary.append(f"  - {row['Category']} ({row['Type']}): ${row['Amount']:,.2f}")

    if 'Month' in df.columns:
        monthly_amounts = df.groupby(['Month', 'Type'])['Amount'].sum().reset_index()
        recent_months = monthly_amounts.sort_values('Month', ascending=False).head(3)
        summary.append("Most recent 3 months:")
        for _, row in recent_months.iterrows():
            summary.append(f"  - {row['Month']} {row['Type']}: ${row['Amount']:,.2f}")

    return "\n".join(summary)

def increase_or_decrease(change):
    """
    Helper to generate increase/decrease text.

    Args:
        change (float): The change value.

    Returns:
        str: The increase/decrease text.
    """
    return "increased" if change >= 0 else "decreased"
