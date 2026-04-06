import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Financial Brain | Pro Analytics",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Professional Dark Theme CSS
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        padding: 15px;
        border-radius: 10px;
    }
    header, .stMarkdown { color: #E0E0E0; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Loading Function
def load_data(sheet_url, gid):
    base_url = sheet_url.split('/edit')[0]
    csv_url = f"{base_url}/export?format=csv&gid={gid}"
    return pd.read_csv(csv_url)

# Your Google Sheets URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/edit?usp=sharing"

st.title("🧠 Financial Brain Pro")
st.markdown("---")

try:
    # Fetching Data (gid 0: Expenses, gid 1218817484: Portfolio)
    df_expense = load_data(SHEET_URL, "0") 
    df_portfolio = load_data(SHEET_URL, "1218817484")

    # Data Cleaning Logic
    for df in [df_expense, df_portfolio]:
        target_col = 'Amount' if 'Amount' in df.columns else 'Value'
        if target_col in df.columns:
            df[target_col] = df[target_col].astype(str).str.replace(',', '').str.strip()
            df[target_col] = pd.to_numeric(df[target_col], errors='coerce').fillna(0)

    # --- SECTION 1: SPENDING ANALYTICS ---
    st.subheader("💳 Spending Analysis")
    total_ex = float(df_expense['Amount'].sum())
    daily_avg = total_ex / 30
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Monthly Spend", f"{total_ex:,.2f} THB")
    col2.metric("Daily Burn Rate", f"{daily_avg:,.2f} THB")
    
    # Logic for Top Spending Category
    if not df_expense.empty and total_ex > 0:
        top_cat = df_expense.groupby('Category')['Amount'].sum().idxmax()
        col3.metric("Top Spending Category", str(top_cat))

    # Payment Method Breakdown
    if 'Payment_Method' in df_expense.columns:
        st.markdown("#### Payment Methods Breakdown")
        pay_col1, pay_col2 = st.columns([1, 2])
        with pay_col1:
            payment_summary = df_expense.groupby('Payment_Method')['Amount'].sum()
            st.dataframe(payment_summary, use_container_width=True)
        with pay_col2:
            st.bar_chart(payment_summary)

    # --- SECTION 2: PORTFOLIO PERFORMANCE ---
    st.markdown("---")
    st.subheader("📈 Portfolio Wealth")
    total_v = float(df_portfolio['Value'].sum())
    
    p_col1, p_col2 = st.columns([1, 2])
    with p_col1:
        st.metric("Total Net Worth", f"{total_v:,.2f} THB")
        st.write("**Asset Allocation**")
        st.dataframe(df_portfolio[['Asset_Name', 'Type', 'Value']], use_container_width=True)
        
    with p_col2:
        if not df_portfolio.empty:
            chart_data = df_portfolio.set_index('Asset_Name')['Value']
            st.area_chart(chart_data)

except Exception as e:
    st.error(f"System Error: {e}")
    st.info("Check: 1. Column headers (Case Sensitive) 2
