import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. Page Configuration
st.set_page_config(page_title="Financial Brain Pro", page_icon="🧠", layout="wide")

# 2. Setup Connection & Constants
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/edit?usp=sharing"

def load_public_data(url, gid):
    try:
        base_url = url.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid={gid}"
        return pd.read_csv(csv_url)
    except:
        return pd.DataFrame()

st.title("🧠 Financial Brain Pro")

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
                try:
                    # เรียกการเชื่อมต่อ
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    
                    # 1. อ่านข้อมูลปัจจุบันที่มีอยู่ใน Sheets ออกมานิ่งๆ ก่อน
                    current_df = conn.read(worksheet="Expenses")
                    
                    # 2. เตรียมข้อมูลใหม่ที่เราเพิ่งกรอก
                    new_data = pd.DataFrame([{
                        "Date": date.strftime("%Y-%m-%d"),
                        "Category": category,
                        "Amount": amount,
                        "Note": note,
                        "Payment_Method": payment
                    }])
                    
                    # 3. เอาข้อมูลใหม่ไป "ต่อตูด" (Append) ข้อมูลเก่า
                    # เราใช้ verify_integrity=False เพื่อความลื่นไหล
                    updated_df = pd.concat([current_df, new_data], ignore_index=True)
                    
                    # 4. ส่งข้อมูลที่รวมกันแล้วกลับไปทับที่เดิม (ใช้ update แทน create)
                    conn.update(worksheet="Expenses", data=updated_df)
                    
                    st.success("Transaction Saved Successfully!")
                    st.balloons()
                    st.rerun()
                except Exception as save_error:
                    st.error(f"Save Failed: {save_error}")
            else:
                st.error("Please enter an amount.")

st.markdown("---")

# --- SECTION 2: ANALYTICS DASHBOARD ---
try:
    # Load data for charts
    df_expense = load_public_data(SHEET_URL, "0") 
    df_portfolio = load_public_data(SHEET_URL, "1218817484")

    # Data Cleaning
    for df in [df_expense, df_portfolio]:
        if not df.empty:
            target_col = 'Amount' if 'Amount' in df.columns else 'Value'
            if target_col in df.columns:
                df[target_col] = df[target_col].astype(str).str.replace(',', '').str.strip()
                df[target_col] = pd.to_numeric(df[target_col], errors='coerce').fillna(0)

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
                st.dataframe(df_expense.groupby('Payment_Method')['Amount'].sum(), use_container_width=True)
            with pay_col2:
                st.bar_chart(df_expense.groupby('Payment_Method')['Amount'].sum())

    # Portfolio Wealth
    st.markdown("---")
    st.subheader("📈 Portfolio Wealth")
    if not df_portfolio.empty:
        total_v = float(df_portfolio['Value'].sum())
        p_col1, p_col2 = st.columns([1, 2])
        with p_col1:
            st.metric("Total Net Worth", f"{total_v:,.2f} THB")
            st.dataframe(df_portfolio[['Asset_Name', 'Type', 'Value']], use_container_width=True)
        with p_col2:
            if 'Asset_Name' in df_portfolio.columns:
                st.area_chart(df_portfolio.set_index('Asset_Name')['Value'])

except Exception as e:
    st.error(f"Dashboard Error: {e}")

st.markdown("---")
st.caption("Strategic Intelligence & Minimalist Design by Your AI Consultant")
