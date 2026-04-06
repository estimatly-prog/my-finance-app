import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Financial Brain", layout="wide")

def load_data(sheet_url, gid):
    base_url = sheet_url.split('/edit')[0]
    csv_url = f"{base_url}/export?format=csv&gid={gid}"
    return pd.read_csv(csv_url)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/edit?usp=sharing"

st.title("🧠 The Financial Brain")

try:
    # ดึงข้อมูล
    df_expense = load_data(SHEET_URL, "0") 
    df_portfolio = load_data(SHEET_URL, "1218817484")

    # --- ส่วนที่ 1: Insight การใช้จ่าย ---
    st.header("💳 Expense Insight")
    
    if not df_expense.empty:
        # แปลง Amount เป็นตัวเลข และลบค่าที่แสดงผลไม่ได้ออก
        df_expense['Amount'] = pd.to_numeric(df_expense['Amount'], errors='coerce').fillna(0)
        
        # คำนวณเป็นตัวเลขเพียวๆ ก่อน
        total_ex = float(df_expense['Amount'].sum())
        avg_ex = float(total_ex / 30)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("ยอดจ่ายรวมเดือนนี้", f"{total_ex:,.2f} บาท")
        c2.metric("เฉลี่ยจ่ายรายวัน", f"{avg_ex:,.2f} บาท")
        
        if 'Category' in df_expense.columns and total_ex > 0:
            top_cat = df_expense.groupby('Category')['Amount'].sum().idxmax()
            c3.metric("รายการที่จ่ายหนักสุด", str(top_cat))
    else:
        st.info("ยังไม่มีข้อมูลรายจ่าย")

    # --- ส่วนที่ 2: Insight ทรัพย์สิน ---
    st.divider()
    st.header("📈 Portfolio Health")
    
    if not df_portfolio.empty:
        # แปลง Value เป็นตัวเลข
        df_portfolio['Value'] = pd.to_numeric(df_portfolio['Value'], errors='coerce').fillna(0)
        
        # คำนวณเป็นตัวเลขเพียวๆ
        total_v = float(df_portfolio['Value'].sum())
        
        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            st.metric("มูลค่าพอร์ตรวม", f"{total_v:,.2f} บาท")
            st.dataframe(df_portfolio, use_container_width=True)
            
        with col_p2:
            # มั่นใจว่า Value เป็นตัวเลขก่อนวาดกราฟ
            chart_data = df_portfolio.set_index('Asset_Name')['Value']
            st.bar_chart(chart_data)
    else:
        st.info("ยังไม่มีข้อมูลพอร์ต")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")

# --- ส่วนที่ 3: Financial Future (ส่วนที่ฉลาดที่สุด) ---
    st.divider()
    st.header("🔮 Financial Future Prediction")
    
    # คำนวณเงินออมเฉลี่ย (รายได้ - รายจ่าย) 
    # สมมติรายได้นิ่งๆ ไว้ก่อน หรือดึงจาก Sheet ก็ได้
    monthly_income = st.number_input("ระบุรายได้เฉลี่ยต่อเดือนของคุณ (บาท)", value=50000)
    monthly_savings = monthly_income - total_ex
    
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        st.write(f"💰 **เงินออมคาดการณ์:** {monthly_savings:,.2f} บาท/เดือน")
        if monthly_savings > 0:
            years_to_million = 1000000 / (monthly_savings * 12)
            st.success(f"คุณจะเก็บเงินครบ 1 ล้านบาท ภายใน **{years_to_million:.1f} ปี**")
        else:
            st.warning("⚠️ รายจ่ายสูงกว่ารายได้ รีบปรับแผนการเงินด่วนครับ!")

    with col_f2:
        # วิเคราะห์ปันผล (กรณีมีหุ้นปันผลอย่าง TISCO)
        st.write("⚓ **Passive Income Check**")
        dividend_rate = st.slider("คาดการณ์ปันผลเฉลี่ยของพอร์ต (%)", 0, 10, 5)
        annual_div = total_v * (dividend_rate / 100)
        st.info(f"พอร์ตนี้จะสร้างเงินปันผลให้คุณปีละ **{annual_div:,.2f} บาท** (เฉลี่ยเดือนละ {annual_div/12:,.2f} บาท)")
