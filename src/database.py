import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

def load_all_data():
    """ฟังก์ชันโหลดข้อมูลแบบระบุ URL ตรงๆ ทีละหน้า"""
    data = {}
    # กำหนดฐานของ URL (ID ของไฟล์คุณ)
    base = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/export?format=csv&gid="
    
    try:
        # ลองดึงทีละหน้าแบบ Hard-code URL เพื่อความชัวร์
        data["cash_flow"] = pd.read_csv(f"{base}0")
        data["portfolio"] = pd.read_csv(f"{base}1218817484")
        data["budget"] = pd.read_csv(f"{base}2055623351")
        data["goals"] = pd.read_csv(f"{base}1271566138")
        data["master"] = pd.read_csv(f"{base}687236707")
        data["rules"] = pd.read_csv(f"{base}700317739")
        data["fixed_expenses"] = pd.read_csv(f"{base}2141043717")
        return data
    except Exception as e:
        # แสดง Error ออกมาให้เห็นชัดๆ ว่าตัวไหนมีปัญหา
        st.error(f"❌ ระบบดึงข้อมูลขัดข้อง: {e}")
        return {}

def delete_asset(asset_name):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Portfolio", ttl=0)
        df = df[df['Asset_Name'] != asset_name]
        conn.update(worksheet="Portfolio", data=df)
        return True
    except: return False

def save_new_asset(new_a_df):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        curr = conn.read(worksheet="Portfolio", ttl=0)
        name_to_save = new_a_df['Asset_Name'].iloc[0]
        updated = pd.concat([curr[curr['Asset_Name'] != name_to_save], new_a_df], ignore_index=True)
        conn.update(worksheet="Portfolio", data=updated)
        return True
    except: return False
