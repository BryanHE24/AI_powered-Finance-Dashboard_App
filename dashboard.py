# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
from fpdf import FPDF

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import our modules
from processor import process_data, get_kpis, generate_chart_data
from assistant import ask_assistant, generate_insights, generate_summary

# Configure the page
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
css_file = 'static/css/streamlit_custom.css'
if os.path.exists(css_file):
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
else:
    st.warning(f"CSS file not found at {css_file}")

# Function to get the current file path
def get_current_file():
    shared_file = 'current_file.txt'
    if os.path.exists(shared_file):
        with open(shared_file, 'r') as f:
            return f.read().strip()
    return None

# Check for uploaded file
uploaded_file = get_current_file()

# Sidebar
with st.sidebar:
    st.title("Finance Dashboard")
    st.write("AI-powered financial analysis")

    # File uploader if not already provided by Flask
    if not uploaded_file:
        uploaded_file = st.file_uploader("Upload Financial Data", type=["xlsx", "xls", "csv"])
    else:
        st.success("File loaded successfully!")
        # Display filename
        st.write(f"Current file: {os.path.basename(uploaded_file)}")

    # Sample data option
    if not uploaded_file:
        if st.button("Use Sample Data"):
            # Use the sample data generator
            from generate_sample_data import generate_sample_data
            uploaded_file = generate_sample_data()

    # Show AI Assistant section
    st.subheader("AI Assistant")
    user_query = st.text_input("Ask about your finances:")

    if st.button("Get Insights"):
        if uploaded_file and user_query:
            # Load data
            if isinstance(uploaded_file, str):
                # It's a filepath
                if uploaded_file.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
            else:
                # It's a file object
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

            # Process data
            df = process_data(df)

            # Get AI response
            response = ask_assistant(user_query, df)
            st.write("AI Response:")
            st.info(response)
        else:
            st.warning("Please upload data and enter a question.")

# Main content
def main():
    st.title("Financial Performance Dashboard")

    # Show loading message if no file
    if not uploaded_file:
        st.info("Upload a financial data file to get started.")
        return

    # Load and process data
    try:
        if isinstance(uploaded_file, str):
            # It's a filepath
            if uploaded_file.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        else:
            # It's a file object
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

        # Process data
        df = process_data(df)

        # Get KPIs
        kpis = get_kpis(df)

        # Create layout with columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Income", f"${kpis['income']:,.2f}")
            st.metric("Average Income", f"${kpis['avg_income']:,.2f}")
            st.metric("Std Dev Income", f"${kpis['std_income']:,.2f}")

        with col2:
            st.metric("Total Expenses", f"${kpis['expense']:,.2f}")
            st.metric("Average Expenses", f"${kpis['avg_expense']:,.2f}")
            st.metric("Std Dev Expenses", f"${kpis['std_expense']:,.2f}")

        with col3:
            st.metric("Net Profit", f"${kpis['profit']:,.2f}",
                     delta=f"{kpis['growth']:.1f}%" if kpis['growth'] != 0 else None)

        # Generate chart data
        chart_data = generate_chart_data(df)

        # Main chart
        st.subheader("Income vs Expenses")

        # Create data for the chart
        chart_df = pd.DataFrame({
            'Month': chart_data['months'] * 2,
            'Amount': [chart_data['income'].get(m, 0) for m in chart_data['months']] +
                     [chart_data['expense'].get(m, 0) for m in chart_data['months']],
            'Type': ['Income'] * len(chart_data['months']) + ['Expense'] * len(chart_data['months'])
        })

        # Create interactive chart with Plotly
        fig = px.bar(
            chart_df,
            x='Month',
            y='Amount',
            color='Type',
            barmode='group',
            color_discrete_map={
                'Income': '#F6E05E',  # Yellow for income
                'Expense': '#FC8181'   # Red for expense
            },
            height=400
        )

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#FFFFFF',
            legend_bgcolor='rgba(0,0,0,0)',
            legend_bordercolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Additional analyses sections
        st.subheader("Financial Insights")

        # Generate automatic insights
        insights = generate_insights(df)

        for insight in insights:
            st.info(insight)

        # Category breakdown
        if 'Category' in df.columns:
            st.subheader("Expense Breakdown by Category")
            expense_df = df[df['Type'] == 'Expense']

            category_totals = expense_df.groupby('Category')['Amount'].sum().reset_index()
            category_totals = category_totals.sort_values('Amount', ascending=False)

            fig = px.pie(
                category_totals,
                values='Amount',
                names='Category',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Plasma_r
            )

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF',
                margin=dict(l=20, r=20, t=40, b=20),
            )

            st.plotly_chart(fig, use_container_width=True)

        # Top 5 Expense Categories
        st.subheader("Top 5 Expense Categories")
        top_categories = get_top_expense_categories(df)
        fig = px.bar(
            top_categories,
            x='Category',
            y='Amount',
            color='Amount',
            color_continuous_scale=px.colors.sequential.Plasma_r,
            height=400
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#FFFFFF',
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Income vs Expense Trend Over Time
        st.subheader("Income vs Expense Trend Over Time")
        trend_df = df.groupby(['Date', 'Type'])['Amount'].sum().reset_index()
        trend_df = trend_df.pivot(index='Date', columns='Type', values='Amount').fillna(0).reset_index()
        trend_df['Date'] = pd.to_datetime(trend_df['Date'])
        trend_df = trend_df.sort_values('Date')

        fig = px.line(
            trend_df,
            x='Date',
            y=['Income', 'Expense'],
            title='Income vs Expense Trend Over Time',
            color_discrete_map={
                'Income': '#F6E05E',
                'Expense': '#FC8181'
            },
            height=400
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#FFFFFF',
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Seasonal Analysis
        st.subheader("Seasonal Analysis")
        seasonal_df = get_seasonal_trends(df)
        fig = px.bar(
            seasonal_df,
            x='Month',
            y='Amount',
            color='Type',
            barmode='group',
            color_discrete_map={
                'Income': '#F6E05E',
                'Expense': '#FC8181'
            },
            height=400
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#FFFFFF',
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Written Summary
        st.subheader("Written Summary")
        summary = generate_summary(df)
        st.write(summary)

        # Downloadable Report
        st.subheader("Download Report")
        if st.button("Generate PDF Report"):
            # Generate PDF report using FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Add title to the PDF
            pdf.cell(200, 10, "Financial Performance Report", 0, 1, 'C')

            # Add KPIs to the PDF
            pdf.cell(200, 10, f"Total Income: ${kpis['income']:,.2f}", 0, 1)
            pdf.cell(200, 10, f"Total Expenses: ${kpis['expense']:,.2f}", 0, 1)
            pdf.cell(200, 10, f"Net Profit: ${kpis['profit']:,.2f}", 0, 1)
            pdf.cell(200, 10, f"Growth: {kpis['growth']:.1f}%", 0, 1)
            pdf.cell(200, 10, f"Average Income: ${kpis['avg_income']:,.2f}", 0, 1)
            pdf.cell(200, 10, f"Average Expenses: ${kpis['avg_expense']:,.2f}", 0, 1)
            pdf.cell(200, 10, f"Std Dev Income: ${kpis['std_income']:,.2f}", 0, 1)
            pdf.cell(200, 10, f"Std Dev Expenses: ${kpis['std_expense']:,.2f}", 0, 1)

            # Add insights to the PDF
            pdf.cell(200, 10, "Insights:", 0, 1)
            for insight in insights:
                pdf.multi_cell(0, 10, insight)

            # Add summary to the PDF
            pdf.cell(200, 10, "Summary:", 0, 1)
            pdf.multi_cell(0, 10, summary)

            # Save the PDF to a file
            pdf_filename = "financial_report.pdf"
            pdf.output(pdf_filename)

            # Provide the PDF file for download
            with open(pdf_filename, "rb") as file:
                st.download_button("Download Report", file, "financial_report.pdf")

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()
