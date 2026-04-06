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

# --- SECTION 2: DATA LOADING & BUDGET LOGIC ---
try:
    # Load Data from 3 Tabs
    df_raw = load_public_data(SHEET_URL, "0")          # Expenses
    df_portfolio = load_public_data(SHEET_URL, "1218817484") # Portfolio
    df_budget = load_public_data(SHEET_URL, "1880535920") # Budget (ใส่ GID ของ Tab Budget ของคุณ)

    if not df_raw.empty:
        df_raw['Date'] = pd.to_datetime(df_raw['Date'])
        df_raw['Amount'] = pd.to_numeric(df_raw['Amount'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

        # Sidebar Filter
        month_list = df_raw['Date'].dt.strftime('%Y-%m').unique().tolist()
        month_list.sort(reverse=True)
        selected_month = st.sidebar.selectbox("📅 Select Month", month_list)
        df_filtered = df_raw[df_raw['Date'].dt.strftime('%Y-%m') == selected_month]
        
        # --- BUDGET TRACKER VISUALS ---
        st.subheader(f"🎯 Budget Tracker: {selected_month}")
        
        if not df_budget.empty:
            # รวมยอดจ่ายจริงแยกตามหมวดหมู่
            actual_spending = df_filtered.groupby('Category')['Amount'].sum().reset_index()
            # รวมข้อมูล Budget กับ Actual เข้าด้วยกัน
            budget_comparison = pd.merge(df_budget, actual_spending, on='Category', how='left').fillna(0)
            
            # วนลูปแสดง Progress Bar ของแต่ละหมวดหมู่
            cols = st.columns(len(budget_comparison))
            for i, row in budget_comparison.iterrows():
                with cols[i % len(cols)]:
                    cat = row['Category']
                    actual = row['Amount']
                    budget = row['Monthly_Budget']
                    percent = min(actual / budget, 1.0) if budget > 0 else 0
                    
                    # เลือกสีตามความอันตราย
                    color = "green" if percent < 0.7 else "orange" if percent < 0.9 else "red"
                    
                    st.metric(cat, f"{actual:,.0f} / {budget:,.0f}", f"{percent*100:.1f}% used", delta_color="inverse")
                    st.progress(percent)
        
        st.markdown("---")
        
        # 4. Spending Analysis Charts
        st.subheader("💳 Spending Details")
        total_ex = float(df_filtered['Amount'].sum())
        c1, c2 = st.columns([1, 1])
        with c1:
            pay_sum = df_filtered.groupby('Payment_Method')['Amount'].sum().reset_index()
            fig_bar = px.bar(pay_sum, x='Payment_Method', y='Amount', color='Payment_Method', title="Methods", template="plotly_dark", height=300)
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            cat_sum = df_filtered.groupby('Category')['Amount'].sum().reset_index()
            fig_pie = px.pie(cat_sum, values='Amount', names='Category', hole=0.4, title="Categories", template="plotly_dark", height=300)
            st.plotly_chart(fig_pie, use_container_width=True)

        # Recent Transactions
        with st.expander("📜 View Full Transaction History"):
            st.dataframe(df_filtered.sort_values(by='Date', ascending=False), use_container_width=True, hide_index=True)

    # Portfolio Section
    st.markdown("---")
    st.subheader("📈 Portfolio Wealth")
    if not df_portfolio.empty:
        df_portfolio['Value'] = pd.to_numeric(df_portfolio['Value'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        total_v = float(df_portfolio['Value'].sum())
        st.metric("Total Net Worth", f"{total_v:,.2f} THB")
        st.area_chart(df_portfolio.set_index('Asset_Name')['Value'])

except Exception as e:
    st.error(f"Dashboard Error: {e}")

st.markdown("---")
st.caption("Strategic Intelligence & Minimalist Design by Your AI Consultant")
