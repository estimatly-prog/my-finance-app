import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. ระบุ ID ของไฟล์ให้ชัดเจน (ดึงจากลิงก์ที่คุณส่งมา)
FILE_ID = "1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4"

def read_sheet(gid):
    """ฟังก์ชันกลางสำหรับดึง CSV จาก Google Sheets"""
    url = f"https://docs.google.com/spreadsheets/d/{FILE_ID}/export?format=csv&gid={gid}"
    return pd.read_csv(url)

def load_all_data():
    """ฟังก์ชันโหลดข้อมูลทุกหน้า"""
    data = {}
    try:
        # ทดลองดึงทีละหน้า ถ้าหน้าไหนพัง จะได้รู้ว่าพังที่ GID ไหน
        data["cash_flow"] = read_sheet("0")
        data["portfolio"] = read_sheet("1218817484")
        data["budget"] = read_sheet("2055623351")
        data["goals"] = read_sheet("1271566138")
        data["master"] = read_sheet("687236707")
        data["rules"] = read_sheet("700317739")
        data["fixed_expenses"] = read_sheet("2141043717")
        return data
    except Exception as e:
        # ถ้าพัง ให้โชว์ Error เลยว่าพังเพราะอะไร และ URL ไหน
        st.error(f"❌ ดึงข้อมูลไม่สำเร็จ: {e}")
        return {}

def delete_asset(asset_name):
    """ฟังก์ชันลบ (ใช้ GSheetsConnection เหมือนเดิม)"""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Portfolio", ttl=0)
        df = df[df['Asset_Name'] != asset_name]
        conn.update(worksheet="Portfolio", data=df)
        return True
    except: return False

def save_new_asset(new_a_df):
    """ฟังก์ชันบันทึก (ใช้ GSheetsConnection เหมือนเดิม)"""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        curr = conn.read(worksheet="Portfolio", ttl=0)
        name_to_save = new_a_df['Asset_Name'].iloc[0]
        updated = pd.concat([curr[curr['Asset_Name'] != name_to_save], new_a_df], ignore_index=True)
        conn.update(worksheet="Portfolio", data=updated)
        return True
    except: return False
