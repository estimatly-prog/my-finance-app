import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Financial Brain", layout="wide")

# 2. ฟังก์ชันดึงข้อมูล (ปรับปรุงใหม่ให้ฉลาดขึ้น)
def load_data(sheet_url, gid):
    # ลบส่วนท้ายออกก่อนเพื่อความชัวร์ แล้วประกอบร่างใหม่เป็นลิงก์ Export CSV
    base_url = sheet_url.split('/edit')[0]
    csv_url = f"{base_url}/export?format=csv&gid={gid}"
    return pd.read_csv(csv_url)

# URL ของคุณ (ผมใช้ตัวเดิมที่คุณส่งมา)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/edit?usp=sharing"

st.title("🧠 The Financial Brain")

try:
    # ดึงข้อมูลจาก Tab
    # อย่าลืม: เช็คว่าใน Sheet ของคุณ Tab แรก (gid=0) คือ Expenses ใช่ไหม
    df_expense = load_data(SHEET_URL, "0") 
    df_portfolio = load_data(SHEET_URL, "1218817484")

    # --- ส่วนที่ 1: Insight การใช้จ่าย ---
    st.header("💳 Expense Insight")
    
    if not df_expense.empty:
        total_expense = df_expense['Amount'].sum()
        avg_per_day = total_expense / 30
        
        c1, c2, c3 = st.columns(3)
        c1.metric("ยอดจ่ายรวมเดือนนี้", f"{total_expense:,.2f} บาท")
        c2.metric("เฉลี่ยจ่ายรายวัน", f"{avg_per_day:,.2f} บาท")
        
        # ป้องกันกรณีไม่มีข้อมูล Category
        if 'Category' in df_expense.columns:
            top_cat = df_expense.groupby('Category')['Amount'].sum().idxmax()
            c3.metric("รายการที่จ่ายหนักสุด", top_cat)
    else:
        st.info("ยังไม่มีข้อมูลรายจ่ายใน Google Sheets")

    # --- ส่วนที่ 2: Insight ทรัพย์สิน ---
    st.divider()
    st.header("📈 Portfolio Health")
    
    if not df_portfolio.empty:
        total_value = df_portfolio['Value'].sum()
        
        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            st.metric("มูลค่าพอร์ตรวม", f"{total_value:,.2f} บาท")
            st.dataframe(df_portfolio, use_container_width=True)
            
        with col_p2:
            st.bar_chart(df_portfolio.set_index('Asset_Name')['Value'])
    else:
        st.info("ยังไม่มีข้อมูลพอร์ตใน Google Sheets")

except Exception as e:
    # ส่วนนี้จะบอกเราว่า "พังเพราะอะไร"
    st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
    st.info("จุดที่ควรเช็ค:\n1. ชื่อ Column ใน Sheets สะกดตรงไหม (Date, Category, Amount, Asset_Name, Value)?\n2. เลข gid ถูกต้องตาม Tab ไหม?\n3. ลืมใส่ข้อมูลลงในแถวแรกๆ หรือเปล่า?")
