import streamlit as st
import pandas as pd

st.set_page_config(page_title="Financial Brain", layout="wide")

def load_data(sheet_url, gid):
    base_url = sheet_url.split('/edit')[0]
    csv_url = f"{base_url}/export?format=csv&gid={gid}"
    # เพิ่ม keep_default_na=False เพื่อไม่ให้ค่าว่างกลายเป็น NaN
    return pd.read_csv(csv_url)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/edit?usp=sharing"

st.title("🧠 The Financial Brain")

try:
    df_expense = load_data(SHEET_URL, "0") 
    df_portfolio = load_data(SHEET_URL, "1218817484")

    # --- ส่วนที่ 1: Insight การใช้จ่าย ---
    st.header("💳 Expense Insight")
    if not df_expense.empty:
        # ล้างข้อมูล Amount: ลบช่องว่าง และเครื่องหมายคอมม่าออกก่อนแปลง
        df_expense['Amount'] = df_expense['Amount'].astype(str).str.replace(',', '').str.strip()
        df_expense['Amount'] = pd.to_numeric(df_expense['Amount'], errors='coerce').fillna(0)
        
        total_ex = float(df_expense['Amount'].sum())
        avg_ex = float(total_ex / 30)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("ยอดจ่ายรวมเดือนนี้", f"{total_ex:,.2f} บาท")
        c2.metric("เฉลี่ยจ่ายรายวัน", f"{avg_ex:,.2f} บาท")
        
        if 'Category' in df_expense.columns and total_ex > 0:
            top_cat = df_expense.groupby('Category')['Amount'].sum().idxmax()
            c3.metric("รายการที่จ่ายหนักสุด", str(top_cat))

    # --- ส่วนที่ 2: Insight ทรัพย์สิน (จุดที่เกิดปัญหา) ---
    st.divider()
    st.header("📈 Portfolio Health")
    if not df_portfolio.empty:
        # ล้างข้อมูล Value: สำคัญมาก! ลบทุกอย่างที่ไม่ใช่ตัวเลขออก
        df_portfolio['Value'] = df_portfolio['Value'].astype(str).str.replace(',', '').str.strip()
        df_portfolio['Value'] = pd.to_numeric(df_portfolio['Value'], errors='coerce').fillna(0)
        
        total_v = float(df_portfolio['Value'].sum())
        
        # แสดงตารางดิบๆ เพื่อเช็คว่าข้อมูลมาจริงไหม (Debug Mode)
        with st.expander("🔍 คลิกเพื่อดูข้อมูลดิบจาก Sheets (เช็คว่า Value มาไหม)"):
            st.write(df_portfolio)

        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            st.metric("มูลค่าพอร์ตรวม", f"{total_v:,.2f} บาท")
            st.dataframe(df_portfolio, use_container_width=True)
            
        with col_p2:
            chart_data = df_portfolio.set_index('Asset_Name')['Value']
            st.bar_chart(chart_data)

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
