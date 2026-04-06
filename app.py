import streamlit as st
import pandas as pd

# 1. Page Configuration: Setting a professional title and wide layout
st.set_page_config(
    page_title="Financial Brain | Analytics Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Custom CSS for Minimalist Dark Theme
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        padding: 15px;
        border-radius: 10px;
    }
    .stHeader { color: #58A6FF; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Loading Function with Google Sheets CSV Export logic
def load_data(sheet_url, gid):
    base_url = sheet_url.split('/edit')[0]
    csv_url = f"{base_url}/export?format=csv&gid={gid}"
    return pd.read_csv(csv_url)

# Your Google Sheets URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/edit?usp=sharing"

st.title("🧠 Financial Brain Pro")
st.markdown("---")

try:
    # Fetching Data from Sheets (gid 0 for Expenses, 1218817484 for Portfolio)
    df_expense = load_data(SHEET_URL, "0") 
    df_portfolio = load_data(SHEET_URL, "1218817484")

    # Data Cleaning: Removing commas and converting to numeric values
    for df in [df_expense, df_portfolio]:
        target_col = 'Amount' if 'Amount' in df.columns else 'Value'
        df[target_col] = df[target_col].astype(str).str.replace(',', '').str.strip()
        df[target_col] = pd.to_numeric(df[target_col], errors='coerce').fillna(0)

    # --- SECTION 1: EXPENSE ANALYTICS ---
    st.subheader("💳 Spending Analysis")
    total_ex = float(df_expense['Amount'].sum())
    daily_avg = total_ex / 30
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Monthly Spend", f"{total_ex:,.2f} THB")
    col2.metric("Daily Burn Rate", f"{daily_avg:,.2f} THB")
    
    # Logic for Top Spending Category
    if not df_expense.empty and total_ex > 0:
        top_cat = df_expense.groupby('Category')['Amount'].sum().idxmax()
        col3.metric("Top Spending Category", top_cat)
