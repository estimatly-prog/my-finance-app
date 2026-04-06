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

# 3. Setup Connection & Constants
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/edit?usp=sharing"

def load_public_data(url, gid):
    try:
        base_url = url.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid={gid}"
        return pd.read_csv(csv_url)
    except:
        return pd.DataFrame()

st.title("🧠 Financial Brain Pro")

try:
    # 4. Data Loading - Hybrid Approach
    # เราใช้การอ่านแบบ Public (GID) เพื่อความชัวร์ว่ากราฟจะขึ้นแน่นอน
    df_expense = load_public_data(SHEET_URL, "0") 
    df_portfolio = load_public_data(SHEET_URL, "1218817484")

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
                    try:
                        # การเขียน (Update) จะใช้ Connection จาก Secrets
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        new_data = pd.DataFrame([{
                            "Date": date.strftime("%Y-%m-%d"),
                            "Category": category,
                            "Amount": amount,
                            "Note": note,
                            "Payment_Method": payment
                        }])
                        # ดึงข้อมูลปัจจุบันมาต่อท้าย
                        current_df = conn.read(worksheet="Expenses")
                        updated_df = pd.concat([current_df, new_data], ignore_index=True)
                        conn.update(worksheet="Expenses", data=updated_df)
                        st.success("Transaction Saved!")
                        st.balloons()
                        st.rerun()
                    except Exception as save_error:
                        st.error(f"Save Failed: {save_error}")
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
            st.area_chart(df_portfolio.set_index('Asset_Name')['Value'])

except Exception as e:
    st.error(f"Dashboard Error: {e}")

st.markdown("---")
st.caption("Strategic Intelligence & Minimalist Design by Your AI Consultant")
