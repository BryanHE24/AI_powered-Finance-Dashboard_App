# dashboard.py 
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
from fpdf import FPDF
import re

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from processor import process_data, get_kpis, generate_chart_data, get_seasonal_trends, get_top_expense_categories, generate_pdf_report
from assistant import ask_assistant, generate_insights, generate_summary

# Configure the page
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
css_file = 'app/static/css/streamlit_custom.css'
if os.path.exists(css_file):
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
else:
    st.warning(f"CSS file not found at {css_file}")

# Function to get the current file path
def get_current_file():
    """
    Get the current file path from the shared file.

    Returns:
        str: The filepath.
    """
    shared_file = 'data/current_file.txt'
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

    if not uploaded_file:
        uploaded_file = st.file_uploader("Upload Financial Data", type=["xlsx", "xls", "csv"])
    else:
        st.success("File loaded successfully!")
        st.write(f"Current file: {os.path.basename(uploaded_file)}")

    if not uploaded_file:
        if st.button("Use Sample Data"):
            from src.generate_sample_data import generate_sample_data
            uploaded_file = generate_sample_data()

    st.subheader("AI Assistant")
    user_query = st.text_input("Ask about your finances:")

    if st.button("Get Insights"):
        if uploaded_file and user_query:
            if isinstance(uploaded_file, str):
                if uploaded_file.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
            else:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

            df = process_data(df)
            response = ask_assistant(user_query, df)
            st.write("AI Response:")
            st.info(response)
        else:
            st.warning("Please upload data and enter a question.")

# Main content
def main():
    """
    Main function to display the financial dashboard.
    """
    st.title("Financial Performance Dashboard")

    if not uploaded_file:
        st.info("Upload a financial data file to get started.")
        return

    try:
        if isinstance(uploaded_file, str):
            if uploaded_file.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        else:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

        df = process_data(df)
        kpis = get_kpis(df)

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

        chart_data = generate_chart_data(df)

        st.subheader("Income vs Expenses")

        chart_df = pd.DataFrame({
            'Month': chart_data['months'] * 2,
            'Amount': [chart_data['income'].get(m, 0) for m in chart_data['months']] +
                     [chart_data['expense'].get(m, 0) for m in chart_data['months']],
            'Type': ['Income'] * len(chart_data['months']) + ['Expense'] * len(chart_data['months'])
        })

        fig = px.bar(
            chart_df,
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
            legend_bgcolor='rgba(0,0,0,0)',
            legend_bordercolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Financial Insights")

        insights = generate_insights(df)

        for insight in insights:
            st.info(insight)

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

        st.subheader("Written Summary")

        summary_html = generate_summary(df)

        summary_container = st.container()
        with summary_container:
            st.markdown("""
            <style>
            .summary-box {
                background-color: rgba(30, 30, 30, 0.6);
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                border-left: 4px solid #F6E05E;
            }
            </style>
            """, unsafe_allow_html=True)

            st.markdown(f'<div class="summary-box">{summary_html}</div>', unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)

            plain_text = re.sub('<.*?>', '', summary_html)

            st.download_button(
                label="Download Summary as Text",
                data=plain_text,
                file_name="financial_summary.txt",
                mime="text/plain"
            )

        st.subheader("Download Report")
        if st.button("Generate PDF Report"):
            try:
                pdf = generate_pdf_report(df, kpis, insights, plain_text)
                pdf_filename = "financial_report.pdf"
                pdf.output(pdf_filename)

                with open(pdf_filename, "rb") as file:
                    st.download_button(
                        label="📊 Download Detailed Financial Report (PDF)",
                        data=file,
                        file_name="financial_report.pdf",
                        mime="application/pdf",
                        help="Download a professionally formatted PDF with all financial analyses"
                    )

                st.success("Report generated successfully! Click the button above to download.")
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
                st.exception(e)

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()
