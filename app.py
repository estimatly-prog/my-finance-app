import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้าเว็บและ Dark Theme เบื้องต้น
st.set_page_config(
    page_title="The Financial Brain | Dark Edition",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ปรับ CSS ให้เป็นธีมดาร์กแบบหรู (Custom Dark Minimalist)
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stMetric { background-color: #161B22; padding: 15px; border-radius: 10px; border: 1px solid #30363D; }
    </style>
    """, unsafe_allow_html=True)

def load_data(sheet_url, gid):
    base_url = sheet_url.split('/edit')[0]
    csv_url = f"{base_url}/export?format=csv&gid={gid}"
    return pd.read_csv(csv_url)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/edit?usp=sharing"

st.title("🌑 The Financial Brain: Dark Edition")

try:
    df_expense = load_data(SHEET_URL, "0") 
    df_portfolio = load_data(SHEET_URL, "1218817484")

    # ล้างข้อมูลตัวเลข
    for df in [df_expense, df_portfolio]:
        col = 'Amount' if 'Amount' in df.columns else 'Value'
        df[col] = df[col].astype(str).str.replace(',', '').str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- ส่วนที่ 1: Expense & Payment Insight ---
    st.header("💳 Expense & Payment Analysis")
    
    total_ex = float(df_expense['Amount'].sum())
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Expenses", f"{total_ex:,.2f} THB")
    
    # คำนวณ Insight การจ่ายเงิน (Payment Method)
    if 'Payment_Method' in df_expense.columns:
        payment_summary = df_expense.groupby('Payment_Method')['Amount'].sum()
        top_payment = payment_summary.idxmax()
        c2.metric("Primary Payment", top_payment)
        
        with st.expander("🔍 เจาะลึกการใช้บัตรเครดิตและพร้อมเพย์"):
            st.write("สรุปยอดแบ่งตามวิธีชำระเงิน:")
            st.bar_chart(payment_summary)
    
    # --- ส่วนที่ 2: Portfolio Health ---
    st.divider()
    st.header("📈 Portfolio Performance")
    total_v = float(df_portfolio['Value'].sum())
    
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        st.metric("Net Worth", f"{total_v:,.2f} THB")
        st.dataframe(df_portfolio, use_container_width=True)
    with col_p2:
        st.area_chart(df_portfolio.set_index('Asset_Name')['Value']) # เปลี่ยนเป็น Area Chart ให้ดู Modern ขึ้น

except Exception as e:
    st.error(f"Error: {e}")
