import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. Page Configuration
st.set_page_config(page_title="Financial Brain Pro", page_icon="🧠", layout="wide")

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

# 3. Setup Connection
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🧠 Financial Brain Pro")

# เริ่มต้น Block ตรวจสอบการทำงาน
try:
    # 4. Data Loading (สังเกตการย่อหน้าด้านล่างนี้ ต้องตรงกันทั้งหมด)
    df_expense = conn.read(worksheet="Expenses", ttl="5s") 
    df_portfolio = conn.read(worksheet="Portfolio", ttl="1m")

    # Data Cleaning Logic
    for df in [df_expense, df_portfolio]:
        if not df.empty:
            target_col = 'Amount' if 'Amount' in df.columns else 'Value'
            if target_col in df.columns:
                df[target_col] = df[target_col].astype(str).str.replace(',', '').str.strip()
                df[target_col] = pd.to_numeric(df[target_col], errors='coerce').fillna(0)

    # --- SECTION 1: QUICK TRANSACTION ENTRY ---
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
                    new_data = pd.DataFrame([{
                        "Date": date.strftime("%Y-%m-%d"),
                        "Category": category,
                        "Amount": amount,
                        "Note": note,
                        "Payment_Method": payment
                    }])
                    updated_df = pd.concat([df_expense, new_data], ignore_index=True)
                    conn.update(worksheet="Expenses", data=updated_df)
                    st.success("Transaction Saved Successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Please enter an amount.")

    # --- SECTION 2: ANALYTICS DASHBOARD ---
    st.markdown("---")
    
    # Spending Analysis
    st.subheader("💳 Spending Analysis")
    if not df_expense.empty:
        total_ex = float(df_expense['Amount'].sum())
        daily_avg = total_ex / 30
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Monthly Spend", f"{total_ex:,.2f} THB")
        c2.metric("Daily Burn Rate", f"{daily_avg:,.2f} THB")
        
        if total_ex > 0:
            top_cat = df_expense.groupby('Category')['Amount'].sum().idxmax()
            c3.metric("Top Spending Category", str(top_cat))

        if 'Payment_Method' in df_expense.columns:
            st.markdown("#### Payment Methods Breakdown")
            pay_col1, pay_col2 = st.columns([1, 2])
            with pay_col1:
                payment_summary = df_expense.groupby('Payment_Method')['Amount'].sum()
                st.dataframe(payment_summary, use_container_width=True)
            with pay_col2:
                st.bar_chart(payment_summary)

    # Portfolio Wealth
    st.markdown("---")
    st.subheader("📈 Portfolio Wealth")
    if not df_portfolio.empty:
        total_v = float(df_portfolio['Value'].sum())
        
        p_col1, p_col2 = st.columns([1, 2])
        with p_col1:
            st.metric("Total Net Worth", f"{total_v:,.2f} THB")
            st.write("**Asset Allocation**")
            st.dataframe(df_portfolio[['Asset_Name', 'Type', 'Value']], use_container_width=True)
        with p_col2:
            if 'Asset_Name' in df_portfolio.columns:
                chart_data = df_portfolio.set_index('Asset_Name')['Value']
                st.area_chart(chart_data)

# นี่คือส่วนที่หายไป (except block) ซึ่งเป็นสาเหตุของ Error
except Exception as e:
    st.error("⚠️ System Error")
    st.write(f"Details: {e}")
    st.info("Check: 1. Secrets Setup 2. Google Sheets Tab Names 3. Editor Permission")

st.markdown("---")
st.caption("Strategic Intelligence & Minimalist Design by Your AI Consultant")
