import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Financial Brain", layout="wide")

# 2. ฟังก์ชันดึงข้อมูลจาก Google Sheets (ฉบับมินิมอล)
def load_data(url):
    # เปลี่ยนลิงก์แชร์ให้เป็นลิงก์สำหรับดาวน์โหลด CSV
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv')
    return pd.read_csv(csv_url)

# วาง Link ของ Google Sheets คุณที่นี่ (อันที่คุณ Copy มา)
# หมายเหตุ: แทนที่ข้อความข้างล่างนี้ด้วย URL ของคุณจริงๆ
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/edit?usp=sharing"

st.title("🧠 The Financial Brain")

try:
    # ดึงข้อมูลจาก Tab ชื่อ 'Expenses' และ 'Portfolio'
    # หมายเหตุ: ใน Google Sheets ต้องตั้งชื่อ Tab ให้ตรง และใส่ gid ให้ถูกต้อง (0 คือ Tab แรก)
    df_expense = load_data(SHEET_URL + "&gid=0") 
    df_portfolio = load_data(SHEET_URL + "&gid=1218817484") # ใส่ gid ของ Tab Portfolio

    # --- ส่วนที่ 1: Insight การใช้จ่าย (Daily Burn Rate) ---
    st.header("💳 Expense Insight")
    total_expense = df_expense['Amount'].sum()
    avg_per_day = total_expense / 30 # สมมติคิดรายเดือน
    
    col1, col2, col3 = st.columns(3)
    col1.metric("ยอดจ่ายรวมเดือนนี้", f"{total_expense:,.2f} บาท")
    col2.metric("เฉลี่ยจ่ายรายวัน", f"{avg_per_day:,.2f} บาท")
    col3.metric("รายการที่จ่ายหนักสุด", df_expense.groupby('Category')['Amount'].sum().idxmax())

    # --- ส่วนที่ 2: Insight ทรัพย์สิน (Portfolio Health) ---
    st.divider()
    st.header("📈 Portfolio Health")
    total_value = df_portfolio['Value'].sum()
    
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        st.metric("มูลค่าพอร์ตรวม", f"{total_value:,.2f} บาท")
        st.write("**สัดส่วนสินทรัพย์:**")
        st.dataframe(df_portfolio)
        
    with col_p2:
        # กราฟแสดงสัดส่วนทรัพย์สิน
        st.bar_chart(df_portfolio.set_index('Asset_Name')['Value'])

except Exception as e:
    st.warning("กำลังรอการเชื่อมต่อข้อมูล... อย่าลืมใส่ URL ของ Google Sheets ใน Code นะครับ")
    st.info("คำแนะนำ: ตรวจสอบว่าแชร์ Link เป็น 'Anyone with the link' หรือยัง")
