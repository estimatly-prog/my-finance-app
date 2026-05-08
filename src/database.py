import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

def get_connection():
    """สร้างการเชื่อมต่อโดยใช้ Service Account จาก Secrets"""
    return st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300) # จำข้อมูลไว้ 5 นาที (300 วินาที) เพื่อลดการยิง API
def get_worksheet_data(worksheet_name):
    """ฟังก์ชันดึงข้อมูลเฉพาะแผ่นที่ต้องการ และใช้ระบบ Cache"""
    try:
        conn = get_connection()
        # เปลี่ยน ttl เป็น 300 เพื่อให้ตัว gsheets connection ช่วยจำข้อมูลด้วยอีกแรง
        return conn.read(worksheet=worksheet_name, ttl=300)
    except Exception as e:
        st.error(f"❌ ไม่สามารถโหลดหน้า {worksheet_name}: {e}")
        return pd.DataFrame()

def delete_asset(asset_name):
    """ฟังก์ชันลบ: ไม่ใช้ Cache เพราะต้องการให้อัปเดตทันที"""
    try:
        conn = get_connection()
        # ดึงแบบสด (ttl=0) เฉพาะตอนจะลบ เพื่อให้ได้ข้อมูลล่าสุดจริงๆ
        df = conn.read(worksheet="Portfolio", ttl=0)
        df = df[df['Asset_Name'] != asset_name]
        conn.update(worksheet="Portfolio", data=df)
        
        # สำคัญ: ล้าง Cache ของหน้า Portfolio หลังจากลบเสร็จ เพื่อให้ครั้งต่อไปดึงข้อมูลใหม่ที่ลบแล้ว
        st.cache_data.clear() 
        return True
    except: return False

def save_new_asset(new_a_df):
    """ฟังก์ชันบันทึก: ไม่ใช้ Cache เพราะต้องการให้อัปเดตทันที"""
    try:
        conn = get_connection()
        # ดึงแบบสด (ttl=0) เพื่อป้องกันการเขียนทับข้อมูลเก่า
        curr = conn.read(worksheet="Portfolio", ttl=0)
        name_to_save = new_a_df['Asset_Name'].iloc[0]
        updated = pd.concat([curr[curr['Asset_Name'] != name_to_save], new_a_df], ignore_index=True)
        conn.update(worksheet="Portfolio", data=updated)
        
        # สำคัญ: ล้าง Cache หลังจากบันทึกเสร็จ
        st.cache_data.clear()
        return True
    except: return False


def save_transaction(new_entry_df):
    """ฟังก์ชันบันทึกรายจ่ายลง Google Sheets และล้าง Cache"""
    try:
        conn = get_connection()
        # ดึงข้อมูลปัจจุบันแบบสดๆ (ttl=0) เพื่อนำมาต่อท้าย
        existing_data = conn.read(worksheet="Expenses", ttl=0)
        
        # ต่อแถวใหม่เข้าไป
        updated_df = pd.concat([existing_data, new_entry_df], ignore_index=True)
        
        # อัปเดตกลับไปที่ Google Sheets
        conn.update(worksheet="Expenses", data=updated_df)
        
        # สำคัญมาก: ล้าง Cache ทุกอย่างเพื่อให้หน้า Cash Flow โหลดข้อมูลใหม่มาโชว์ทันที
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"❌ บันทึกไม่สำเร็จ: {e}")
        return False
