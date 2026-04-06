import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import plotly.express as px

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
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    current_df = conn.read(worksheet="Expenses")
                    new_row = pd.DataFrame([{
                        "Date": date.strftime("%Y-%m-%d"),
                        "Category": category,
                        "Amount": amount,
                        "Note": note,
                        "Payment_Method": payment
                    }])
                    updated_df = pd.concat([current_df, new_row], ignore_index=True)
                    conn.update(worksheet="Expenses", data=updated_df)
                    st.success("Transaction Saved Successfully!")
                    st.balloons()
                    st.rerun()
                except Exception as save_error:
                    st.error(f"Save Failed: {save_error}")
            else:
                st.error("Please enter an amount.")

st.markdown("---")

# --- SECTION 2: DATA LOADING & ANALYTICS ---
try:
    # 1. Load Data
    df_raw = load_public_data(SHEET_URL, "0") 
    df_portfolio = load_public_data(SHEET_URL, "1218817484")

    # 2. Data Cleaning
    if not df_raw.empty:
        df_raw['Date'] = pd.to_datetime(df_raw['Date'])
        df_raw['Amount'] = pd.to_numeric(df_raw['Amount'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

        # 3. Sidebar Filter (FIXED: แก้ไขเรื่อง ArrowStringArray sort)
        # ดึงรายชื่อเดือนออกมา แปลงเป็น List แล้วค่อย Sort
        month_list = df_raw['Date'].dt.strftime('%Y-%m').unique().tolist()
        month_list.sort(reverse=True) # เรียงจากใหม่ไปเก่า
        
        selected_month = st.sidebar.selectbox("📅 Select Month", month_list)
        
        df_filtered = df_raw[df_raw['Date'].dt.strftime('%Y-%m') == selected_month]
        
        # 4. Dashboard Metrics
        st.subheader(f"💳 Spending Analysis: {selected_month}")
        total_ex = float(df_filtered['Amount'].sum())
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Spend", f"{total_ex:,.2f} THB")
        c2.metric("Daily Avg", f"{total_ex/30:,.2f} THB")
        
        if total_ex > 0:
            top_cat = df_filtered.groupby('Category')['Amount'].sum().idxmax()
            c3.metric("Top Category", str(top_cat))

        # Charts Row
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.markdown("#### Methods Breakdown")
            pay_sum = df_filtered.groupby('Payment_Method')['Amount'].sum().reset_index()
            fig_bar = px.bar(pay_sum, x='Payment_Method', y='Amount', color='Payment_Method', template="plotly_dark", height=350)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col_chart2:
            st.markdown("#### Category Distribution")
            cat_sum = df_filtered.groupby('Category')['Amount'].sum().reset_index()
            fig_pie = px.pie(cat_sum, values='Amount', names='Category', hole=0.4, template="plotly_dark", height=350)
            st.plotly_chart(fig_pie, use_container_width=True)

        # SECTION 3: RECENT TRANSACTIONS
        st.markdown("---")
        st.subheader("📜 Recent Transactions (This Month)")
        recent_df = df_filtered.sort_values(by='Date', ascending=False)
        st.dataframe(
            recent_df[['Date', 'Category', 'Amount', 'Payment_Method', 'Note']], 
            use_container_width=True,
            hide_index=True
        )

    # Portfolio Section
    st.markdown("---")
    st.subheader("📈 Portfolio Wealth")
    if not df_portfolio.empty:
        df_portfolio['Value'] = pd.to_numeric(df_portfolio['Value'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        total_v = float(df_portfolio['Value'].sum())
        st.metric("Total Net Worth", f"{total_v:,.2f} THB")
        st.dataframe(df_portfolio[['Asset_Name', 'Type', 'Value']], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Dashboard Error: {e}")

st.markdown("---")
st.caption("Strategic Intelligence & Minimalist Design by Your AI Consultant")
