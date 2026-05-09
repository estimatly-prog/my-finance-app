import streamlit as st

def show_goals():
    st.markdown('<h1 class="app-title">TARGETS.</h1>', unsafe_allow_html=True)
    
    # พื้นที่สำหรับโปรเจกต์ในอนาคตของคุณ
    st.info("Section นี้ใช้ดู Budget และเป้าหมายการออมครับ")
    
    # ตัวอย่างการเพิ่ม Widget ง่ายๆ เผื่อคุณอยากใช้
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏁 Savings Goal")
        st.write("เป้าหมายการออมในปี 2026")
    with col2:
        st.subheader("📊 Budget Allocation")
        st.write("การจัดสรรงบประมาณรายเดือน")
