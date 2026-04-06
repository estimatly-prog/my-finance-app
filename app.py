import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเว็บแบบ Minimalist
st.set_page_config(page_title="Financial Brain", layout="wide")

st.title("🧠 The Financial Brain")
st.subheader("ระบบวิเคราะห์การเงินส่วนบุคคล (Beta)")

# ส่วนของการจำลองข้อมูล (ในอนาคตเราจะเชื่อม Google Sheets จริง)
st.info("💡 เคล็ดลับจากที่ปรึกษา: การคุมรายจ่ายที่ดีที่สุดคือการเห็น 'ความจริง' ของตัวเลขทุกวัน")

# สร้าง Sidebar สำหรับกรอกข้อมูลด่วน
with st.sidebar:
    st.header("Quick Input")
    amount = st.number_input("ยอดใช้จ่ายวันนี้ (บาท)", min_value=0)
    category = st.selectbox("หมวดหมู่", ["อาหาร", "เดินทาง", "ช้อปปิ้ง", "การลงทุน"])
    if st.button("บันทึก"):
        st.success("บันทึกเรียบร้อย! (ระบบจำลอง)")

# ส่วนแสดง Insight
col1, col2 = st.columns(2)

with col1:
    st.metric(label="Daily Burn Rate (เฉลี่ยต่อวัน)", value="450 THB", delta="-50 บาทจากเมื่อวาน")
    st.write("📈 **Insight:** หากใช้จ่ายระดับนี้ คุณจะมีเงินเก็บเพิ่มขึ้น 3,000 บาทในเดือนนี้")

with col2:
    # สร้างกราฟวงกลมทรัพย์สินแบบง่าย
    data = {'Asset': ['TISCO', 'SCB', 'Cash'], 'Value': [207000, 36800, 50000]}
    df = pd.DataFrame(data)
    st.write("📊 **Portfolio Mix**")
    st.bar_chart(df.set_index('Asset'))

st.divider()
st.caption("Designed with Minimalism by Your Personal AI Consultant")
