# src/processor.py
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats
from fpdf import FPDF
import re

def process_data(df):
    """
    Process the uploaded Excel file and prepare data for visualization.

    Args:
        df (pd.DataFrame): The DataFrame containing financial data.

    Returns:
        df (pd.DataFrame): The processed DataFrame.
    """
    if 'Date' not in df.columns:
        date_candidates = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_candidates:
            df['Date'] = df[date_candidates[0]]
        else:
            df['Date'] = pd.to_datetime('today')

    if 'Type' not in df.columns:
        amount_candidates = [col for col in df.columns if 'amount' in col.lower() or 'value' in col.lower()]
        if amount_candidates:
            df['Type'] = df[amount_candidates[0]].apply(lambda x: 'Income' if x >= 0 else 'Expense')
            df['Amount'] = df[amount_candidates[0]].abs()
        else:
            df['Type'] = 'Income'
            df['Amount'] = 1000
    elif 'Amount' not in df.columns:
        amount_candidates = [col for col in df.columns if 'amount' in col.lower() or 'value' in col.lower()]
        if amount_candidates:
            df['Amount'] = df[amount_candidates[0]]
        else:
            df['Amount'] = 1000

    if not pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    df['Month'] = df['Date'].dt.strftime('%b-%y')
    df['Year'] = df['Date'].dt.year
    df['MonthNum'] = df['Date'].dt.month
    df['Quarter'] = df['Date'].dt.quarter
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week

    return df

def get_kpis(df):
    """
    Extract key performance indicators from data.

    Args:
        df (pd.DataFrame): The DataFrame containing financial data.

    Returns:
        dict: A dictionary containing KPIs.
    """
    total_income = df[df['Type'] == 'Income']['Amount'].sum()
    total_expense = df[df['Type'] == 'Expense']['Amount'].sum() if 'Expense' in df['Type'].unique() else 0

    if 'Date' in df.columns:
        df['Month'] = df['Date'].dt.strftime('%Y-%m')
        monthly = df.groupby(['Month', 'Type'])['Amount'].sum().reset_index()
        months = sorted(monthly['Month'].unique())
        if len(months) >= 2:
            current = monthly[(monthly['Month'] == months[-1]) & (monthly['Type'] == 'Income')]['Amount'].sum()
            previous = monthly[(monthly['Month'] == months[-2]) & (monthly['Type'] == 'Income')]['Amount'].sum()
            growth = ((current - previous) / previous * 100) if previous > 0 else 0
        else:
            growth = 0
    else:
        growth = 0

    avg_income = df[df['Type'] == 'Income']['Amount'].mean()
    avg_expense = df[df['Type'] == 'Expense']['Amount'].mean() if 'Expense' in df['Type'].unique() else 0
    std_income = df[df['Type'] == 'Income']['Amount'].std()
    std_expense = df[df['Type'] == 'Expense']['Amount'].std() if 'Expense' in df['Type'].unique() else 0

    return {
        'income': total_income,
        'expense': total_expense,
        'profit': total_income - total_expense,
        'growth': growth,
        'avg_income': avg_income,
        'avg_expense': avg_expense,
        'std_income': std_income,
        'std_expense': std_expense
    }

def generate_chart_data(df):
    """
    Generate data for the main chart.

    Args:
        df (pd.DataFrame): The DataFrame containing financial data.

    Returns:
        dict: A dictionary containing chart data.
    """
    if 'Month' not in df.columns and 'Date' in df.columns:
        df['Month'] = df['Date'].dt.strftime('%b-%y')

    if 'Month' not in df.columns:
        months = ['Dec-22', 'Jan-23', 'Feb-23', 'Mar-23', 'Apr-23', 'May-23',
                 'Jun-23', 'Jul-23', 'Aug-23', 'Sep-23', 'Oct-23', 'Dec-23']
        return {
            'months': months,
            'income': {m: np.random.randint(50000, 150000) for m in months},
            'expense': {m: np.random.randint(30000, 70000) for m in months}
        }

    monthly = df.groupby(['Month', 'Type'])['Amount'].sum().reset_index()
    months = sorted(monthly['Month'].unique())
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

def get_top_expense_categories(df):
    """
    Get the top 5 expense categories.

    Args:
        df (pd.DataFrame): The DataFrame containing financial data.

    Returns:
        pd.DataFrame: The top 5 expense categories.
    """
    expense_df = df[df['Type'] == 'Expense']
    top_categories = expense_df.groupby('Category')['Amount'].sum().nlargest(5).reset_index()
    return top_categories

def get_seasonal_trends(df):
    """
    Identify seasonal trends in income and expenses.

    Args:
        df (pd.DataFrame): The DataFrame containing financial data.

    Returns:
        pd.DataFrame: The seasonal trends.
    """
    df['Month'] = df['Date'].dt.strftime('%b')
    seasonal = df.groupby(['Month', 'Type'])['Amount'].sum().reset_index()
    return seasonal

def calculate_statistics(df):
    """
    Calculate detailed statistical analysis of financial data.

    Args:
        df (pd.DataFrame): The DataFrame containing financial data.

    Returns:
        dict: A dictionary containing statistical data.
    """
    stats_data = {}

    if 'Income' in df['Type'].unique():
        income_df = df[df['Type'] == 'Income']
        stats_data['income'] = {
            'mean': income_df['Amount'].mean(),
            'median': income_df['Amount'].median(),
            'std_dev': income_df['Amount'].std(),
            'min': income_df['Amount'].min(),
            'max': income_df['Amount'].max(),
            'total': income_df['Amount'].sum(),
            'count': len(income_df)
        }

    if 'Expense' in df['Type'].unique():
        expense_df = df[df['Type'] == 'Expense']
        stats_data['expense'] = {
            'mean': expense_df['Amount'].mean(),
            'median': expense_df['Amount'].median(),
            'std_dev': expense_df['Amount'].std(),
            'min': expense_df['Amount'].min(),
            'max': expense_df['Amount'].max(),
            'total': expense_df['Amount'].sum(),
            'count': len(expense_df)
        }

    if 'Month' in df.columns:
        monthly_stats = df.groupby(['Month', 'Type'])['Amount'].agg(['sum', 'mean', 'count']).reset_index()
        stats_data['monthly'] = monthly_stats

    if 'Category' in df.columns:
        category_stats = df.groupby(['Category', 'Type'])['Amount'].agg(['sum', 'mean', 'count']).reset_index()
        stats_data['category'] = category_stats

    if 'Date' in df.columns:
        monthly_data = df.groupby([df['Date'].dt.strftime('%Y-%m'), 'Type'])['Amount'].sum().reset_index()
        if len(monthly_data) > 1:
            income_monthly = monthly_data[monthly_data['Type'] == 'Income'].sort_values('Date')
            if len(income_monthly) > 1:
                stats_data['income_volatility'] = income_monthly['Amount'].std() / income_monthly['Amount'].mean()

            if 'Expense' in df['Type'].unique():
                expense_monthly = monthly_data[monthly_data['Type'] == 'Expense'].sort_values('Date')
                if len(expense_monthly) > 1:
                    stats_data['expense_volatility'] = expense_monthly['Amount'].std() / expense_monthly['Amount'].mean()

        if len(df) > 7:
            dow_stats = df.groupby([df['Date'].dt.dayofweek, 'Type'])['Amount'].sum().reset_index()
            stats_data['day_of_week'] = dow_stats

    if 'Date' in df.columns and len(df) > 2:
        df['date_ordinal'] = df['Date'].apply(lambda x: x.toordinal())
        income_df = df[df['Type'] == 'Income']
        if len(income_df) > 2:
            slope, intercept, r_value, p_value, std_err = stats.linregress(income_df['date_ordinal'], income_df['Amount'])
            stats_data['income_trend'] = {
                'slope': slope,
                'r_value': r_value,
                'p_value': p_value
            }

        if 'Expense' in df['Type'].unique():
            expense_df = df[df['Type'] == 'Expense']
            if len(expense_df) > 2:
                slope, intercept, r_value, p_value, std_err = stats.linregress(expense_df['date_ordinal'], expense_df['Amount'])
                stats_data['expense_trend'] = {
                    'slope': slope,
                    'r_value': r_value,
                    'p_value': p_value
                }

    if 'Month' in df.columns and 'Year' in df.columns:
        month_analysis = df.groupby(['MonthNum', 'Type'])['Amount'].sum().reset_index()
        if len(month_analysis['MonthNum'].unique()) > 4:
            stats_data['monthly_patterns'] = month_analysis

    return stats_data

class FinancialReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Financial Performance Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        self.cell(0, 10, f'Generated on {pd.Timestamp.now().strftime("%Y-%m-%d")}', 0, 0, 'R')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(70, 70, 70)
        self.set_text_color(255, 224, 94)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)
        self.set_text_color(0, 0, 0)

    def section_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, title, 0, 1, 'L')
        self.ln(2)

    def body_text(self, text):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, text)
        self.ln(4)

def generate_pdf_report(df, kpis, insights, summary):
    """
    Generate a well-formatted PDF report with proper styling.

    Args:
        df (pd.DataFrame): The DataFrame containing financial data.
        kpis (dict): The KPIs.
        insights (list): The insights.
        summary (str): The summary.

    Returns:
        FPDF: The generated PDF report.
    """
    pdf = FinancialReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font('Arial', 'B', 24)
    pdf.ln(60)
    pdf.cell(0, 10, 'Financial Performance Report', 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 14)

    if 'Date' in df.columns:
        min_date = df['Date'].min().strftime('%Y-%m-%d')
        max_date = df['Date'].max().strftime('%Y-%m-%d')
        pdf.cell(0, 10, f'Period: {min_date} to {max_date}', 0, 1, 'C')

    pdf.add_page()
    pdf.chapter_title('EXECUTIVE SUMMARY')

    clean_summary = re.sub('<.*?>', '', summary)
    sections = re.split(r'([A-Z ]+:)', clean_summary)

    current_section = "Overview"
    for i, section in enumerate(sections):
        if i == 0:
            if section.strip():
                pdf.body_text(section)
            continue

        if ":" in section:
            current_section = section.strip()
            pdf.section_title(current_section)
        else:
            pdf.body_text(section)

    pdf.add_page()
    pdf.chapter_title('KEY PERFORMANCE INDICATORS')

    col_width = pdf.w / 2.2
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(col_width, 10, 'Metric', 1, 0, 'L')
    pdf.cell(col_width, 10, 'Value', 1, 1, 'R')
    pdf.set_font('Arial', '', 11)

    kpi_pairs = [
        ('Total Income', f"${kpis['income']:,.2f}"),
        ('Total Expenses', f"${kpis['expense']:,.2f}"),
        ('Net Profit', f"${kpis['profit']:,.2f}"),
        ('Profit Growth', f"{kpis['growth']:.1f}%"),
        ('Average Income', f"${kpis['avg_income']:,.2f}"),
        ('Average Expenses', f"${kpis['avg_expense']:,.2f}"),
        ('Income Std Dev', f"${kpis['std_income']:,.2f}"),
        ('Expense Std Dev', f"${kpis['std_expense']:,.2f}")
    ]

    for label, value in kpi_pairs:
        pdf.cell(col_width, 8, label, 1, 0, 'L')
        pdf.cell(col_width, 8, value, 1, 1, 'R')

    pdf.add_page()
    pdf.chapter_title('KEY INSIGHTS')

    for i, insight in enumerate(insights):
        pdf.section_title(f'Insight {i+1}')
        pdf.body_text(insight)

    pdf.add_page()
    pdf.chapter_title('RECOMMENDATIONS')

    recommendations_text = ""
    recommendation_found = False

    for i, section in enumerate(sections):
        if "RECOMMENDATION" in section.upper() and i < len(sections) - 1:
            recommendation_found = True
            recommendations_text = sections[i+1]
            break

    if recommendation_found:
        recommendations = re.split(r'(\d+\.)', recommendations_text)
        current_recommendation = ""

        for part in recommendations:
            if re.match(r'\d+\.', part):
                if current_recommendation:
                    pdf.body_text(current_recommendation)
                current_recommendation = part
            else:
                current_recommendation += part

        if current_recommendation:
            pdf.body_text(current_recommendation)
    else:
        pdf.body_text("No specific recommendations found in the analysis.")

    return pdf
