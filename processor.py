# processor.py
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats

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
    df['Year'] = df['Date'].dt.year
    df['MonthNum'] = df['Date'].dt.month
    df['Quarter'] = df['Date'].dt.quarter
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week
    
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

    # Additional statistics
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

def get_top_expense_categories(df):
    """Get the top 5 expense categories"""
    expense_df = df[df['Type'] == 'Expense']
    top_categories = expense_df.groupby('Category')['Amount'].sum().nlargest(5).reset_index()
    return top_categories

def get_seasonal_trends(df):
    """Identify seasonal trends in income and expenses"""
    df['Month'] = df['Date'].dt.strftime('%b')
    seasonal = df.groupby(['Month', 'Type'])['Amount'].sum().reset_index()
    return seasonal

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

def calculate_statistics(df):
    """Calculate detailed statistical analysis of financial data"""
    stats_data = {}
    
    # Income stats
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
    
    # Expense stats
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
    
    # Monthly trends
    if 'Month' in df.columns:
        monthly_stats = df.groupby(['Month', 'Type'])['Amount'].agg(['sum', 'mean', 'count']).reset_index()
        stats_data['monthly'] = monthly_stats
    
    # Category analysis
    if 'Category' in df.columns:
        category_stats = df.groupby(['Category', 'Type'])['Amount'].agg(['sum', 'mean', 'count']).reset_index()
        stats_data['category'] = category_stats
    
    # Time series analysis
    if 'Date' in df.columns:
        # Monthly volatility
        monthly_data = df.groupby([df['Date'].dt.strftime('%Y-%m'), 'Type'])['Amount'].sum().reset_index()
        if len(monthly_data) > 1:
            income_monthly = monthly_data[monthly_data['Type'] == 'Income'].sort_values('Date')
            if len(income_monthly) > 1:
                stats_data['income_volatility'] = income_monthly['Amount'].std() / income_monthly['Amount'].mean()
            
            if 'Expense' in df['Type'].unique():
                expense_monthly = monthly_data[monthly_data['Type'] == 'Expense'].sort_values('Date')
                if len(expense_monthly) > 1:
                    stats_data['expense_volatility'] = expense_monthly['Amount'].std() / expense_monthly['Amount'].mean()
        
        # Day of week analysis
        if len(df) > 7:
            dow_stats = df.groupby([df['Date'].dt.dayofweek, 'Type'])['Amount'].sum().reset_index()
            stats_data['day_of_week'] = dow_stats
    
    # Calculate trends using linear regression
    if 'Date' in df.columns and len(df) > 2:
        # Convert dates to ordinal for regression
        df['date_ordinal'] = df['Date'].apply(lambda x: x.toordinal())
        
        # Calculate income trend
        income_df = df[df['Type'] == 'Income']
        if len(income_df) > 2:
            slope, intercept, r_value, p_value, std_err = stats.linregress(income_df['date_ordinal'], income_df['Amount'])
            stats_data['income_trend'] = {
                'slope': slope,
                'r_value': r_value,
                'p_value': p_value
            }
        
        # Calculate expense trend
        if 'Expense' in df['Type'].unique():
            expense_df = df[df['Type'] == 'Expense']
            if len(expense_df) > 2:
                slope, intercept, r_value, p_value, std_err = stats.linregress(expense_df['date_ordinal'], expense_df['Amount'])
                stats_data['expense_trend'] = {
                    'slope': slope,
                    'r_value': r_value,
                    'p_value': p_value
                }
    
    # Seasonal analysis if we have enough data
    if 'Month' in df.columns and 'Year' in df.columns:
        # Group by month number to detect seasonality
        month_analysis = df.groupby(['MonthNum', 'Type'])['Amount'].sum().reset_index()
        if len(month_analysis['MonthNum'].unique()) > 4:  # Only if we have data for multiple months
            stats_data['monthly_patterns'] = month_analysis
    
    return stats_data

# Add this to processor.py
def generate_pdf_report(df, kpis, insights, summary):
    """Generate a well-formatted PDF report with proper styling"""
    from fpdf import FPDF
    import re
    import pandas as pd

    class FinancialReport(FPDF):
        def header(self):
            # Set font for the header
            self.set_font('Arial', 'B', 16)
            # Title
            self.cell(0, 10, 'Financial Performance Report', 0, 1, 'C')
            # Line break
            self.ln(10)

        def footer(self):
            # Position at 1.5 cm from bottom
            self.set_y(-15)
            # Set font
            self.set_font('Arial', 'I', 8)
            # Page number
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
            # Date
            self.cell(0, 10, f'Generated on {pd.Timestamp.now().strftime("%Y-%m-%d")}', 0, 0, 'R')

        def chapter_title(self, title):
            # Set font
            self.set_font('Arial', 'B', 14)
            # Background color
            self.set_fill_color(70, 70, 70)
            # Text color
            self.set_text_color(255, 224, 94)  # Yellow/gold to match dashboard
            # Title
            self.cell(0, 10, title, 0, 1, 'L', 1)
            # Line break
            self.ln(4)
            # Reset text color
            self.set_text_color(0, 0, 0)

        def section_title(self, title):
            # Set font
            self.set_font('Arial', 'B', 12)
            # Title
            self.cell(0, 8, title, 0, 1, 'L')
            # Line break
            self.ln(2)

        def body_text(self, text):
            # Set font
            self.set_font('Arial', '', 11)
            # Output justified text
            self.multi_cell(0, 6, text)
            # Line break
            self.ln(4)

    # Initialize PDF
    pdf = FinancialReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Cover page
    pdf.set_font('Arial', 'B', 24)
    pdf.ln(60)
    pdf.cell(0, 10, 'Financial Performance Report', 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 14)
    
    # Date range
    if 'Date' in df.columns:
        min_date = df['Date'].min().strftime('%Y-%m-%d')
        max_date = df['Date'].max().strftime('%Y-%m-%d')
        pdf.cell(0, 10, f'Period: {min_date} to {max_date}', 0, 1, 'C')
    
    # Executive Summary page
    pdf.add_page()
    pdf.chapter_title('EXECUTIVE SUMMARY')
    
    # Clean summary text of any HTML tags
    clean_summary = re.sub('<.*?>', '', summary)
    
    # Extract main sections from summary
    sections = re.split(r'([A-Z ]+:)', clean_summary)
    
    # Process sections
    current_section = "Overview"
    for i, section in enumerate(sections):
        if i == 0:  # First element might be empty or intro
            if section.strip():
                pdf.body_text(section)
            continue
            
        if ":" in section:  # This is a section title
            current_section = section.strip()
            pdf.section_title(current_section)
        else:  # This is section content
            pdf.body_text(section)
    
    # KPI Summary
    pdf.add_page()
    pdf.chapter_title('KEY PERFORMANCE INDICATORS')
    
    # Create a table-like structure for KPIs
    col_width = pdf.w / 2.2
    
    # KPI table headers
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(col_width, 10, 'Metric', 1, 0, 'L')
    pdf.cell(col_width, 10, 'Value', 1, 1, 'R')
    
    # KPI table data
    pdf.set_font('Arial', '', 11)
    
    # Add KPIs in pairs
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
    
    # Key Insights
    pdf.add_page()
    pdf.chapter_title('KEY INSIGHTS')
    
    for i, insight in enumerate(insights):
        pdf.section_title(f'Insight {i+1}')
        pdf.body_text(insight)
    
    # Recommendations
    pdf.add_page()
    pdf.chapter_title('RECOMMENDATIONS')
    
    # Extract recommendations from the summary
    recommendations_text = ""
    recommendation_found = False
    
    for i, section in enumerate(sections):
        if "RECOMMENDATION" in section.upper() and i < len(sections) - 1:
            recommendation_found = True
            recommendations_text = sections[i+1]
            break
    
    if recommendation_found:
        # Split recommendations by numbers
        recommendations = re.split(r'(\d+\.)', recommendations_text)
        current_recommendation = ""
        
        for part in recommendations:
            if re.match(r'\d+\.', part):  # This is a recommendation number
                if current_recommendation:  # Output previous recommendation
                    pdf.body_text(current_recommendation)
                current_recommendation = part  # Start new recommendation
            else:
                current_recommendation += part
        
        # Output the last recommendation
        if current_recommendation:
            pdf.body_text(current_recommendation)
    else:
        pdf.body_text("No specific recommendations found in the analysis.")
    
    return pdf