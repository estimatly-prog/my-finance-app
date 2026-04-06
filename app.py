import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="Financial Brain Pro", page_icon="🧠", layout="wide")

# 2. Professional Dark Theme CSS
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; padding: 15px; border-radius: 10px; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #238636; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- NEW SECTION: QUICK INPUT FORM ---
st.title("🧠 Financial Brain Pro")

with st.expander("➕ Quick Transaction Entry", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            date = st.date_input("Date", datetime.now())
            category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Investment", "Bills", "Others"])
        
        with col_f2:
            amount = st.number_input("Amount (THB)", min_value=0.0, step=1.0)
            payment = st.selectbox("Payment Method", ["PromptPay", "Credit: KTC", "Credit: SCB", "Cash"])
            
        with col_f3:
            note = st.text_input("Note (Optional)")
            submitted = st.form_submit_button("Save Transaction")
            
        if submitted:
            if amount > 0:
                # Logic to send data to Google Sheets will go here
                st.success(f"Saved: {amount} THB to {category} via {payment}")
                st.balloons()
            else:
                st.error("Please enter an amount greater than 0")

st.markdown("---")

# 3. Data Loading (Existing Logic)
def load_data(sheet_url, gid):
    base_url = sheet_url.split('/edit')[0]
    csv_url = f"{base_url}/export?format=csv&gid={gid}"
    return pd.read_csv(csv_url)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/edit?usp=sharing"

try:
    df_expense = load_data(SHEET_URL, "0") 
    df_portfolio = load_data(SHEET_URL, "1218817484")

    # (Cleaning & Dashboard Logic remains the same as previous version...)
    # [Insert the Spending Analysis and Portfolio Wealth sections here]
    st.subheader("💳 Spending Analysis")
    # ... (Code จากเวอร์ชันก่อนหน้า)
    
except Exception as e:
    st.error(f"System Error: {e}")

st.caption("Strategic Intelligence & Minimalist Design by Your AI Consultant")
