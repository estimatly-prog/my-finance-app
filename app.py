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
                    new_data = pd.DataFrame([{
                        "Date": date.strftime("%Y-%m-%d"),
                        "Category": category,
                        "Amount": amount,
                        "Note": note,
                        "Payment_Method": payment
                    }])
                    updated_df = pd.concat([current_df, new_data], ignore_index=True)
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
    # 1. โหลดข้อมูลก่อน (ต้องทำก่อนทำ Filter)
    df_raw = load_public_data(SHEET_URL, "0") 
    df_portfolio = load_public_data(SHEET_URL, "1218817484")

    # 2. Data Cleaning
    if not df_raw.empty:
        df_raw['Date'] = pd.to_datetime(df_raw['Date'])
        df_raw['Amount'] = pd.to_numeric(df_raw['Amount'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

    # 3. --- ADD FILTER SIDEBAR ---
    if not df_raw.empty:
        # สร้างรายการเดือนจากข้อมูลที่มี
        month_list = df_raw['Date'].dt.strftime('%B %Y').unique()
        selected_month = st.sidebar.selectbox("📅 Select Month", month_list)
        
        # กรองข้อมูลเก็บไว้ใน df_filtered
        df_filtered = df_raw[df_raw['Date'].dt.strftime('%B %Y') == selected_month]
    else:
        df_filtered = df_raw

    # 4. Spending Analysis
    st.subheader(f"💳 Spending Analysis: {selected_month if not df_raw.empty else ''}")
    if not df_filtered.empty:
        total_ex = float(df_filtered['Amount'].sum())
        daily_avg = total_ex / 30
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Spend", f"{total_ex:,.2f} THB")
        c2.metric("Daily Avg", f"{daily_avg:,.2f} THB")
        
        if total_ex > 0:
            top_cat = df_filtered.groupby('Category')['Amount'].sum().idxmax()
            c3.metric("Top Category", str(top_cat))

        # --- Row 1: Bar Chart ---
        st.markdown("#### Payment Methods Breakdown")
        payment_summary = df_filtered.groupby('Payment_Method')['Amount'].sum().reset_index()
        fig_bar = px.bar(
            payment_summary, x='Payment_Method', y='Amount',
            color='Payment_Method', color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_dark", height=350
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # --- Row 2: Pie Chart ---
        st.markdown("#### Spending Distribution (%)")
        cat_summary = df_filtered.groupby('Category')['Amount'].sum().reset_index()
        fig_pie = px.pie(
            cat_summary, values='Amount', names='Category',
            hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_dark", height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Portfolio Section
    st.markdown("---")
    st.subheader("📈 Portfolio Wealth")
    if not df_portfolio.empty:
        df_portfolio['Value'] = pd.to_numeric(df_portfolio['Value'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
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
