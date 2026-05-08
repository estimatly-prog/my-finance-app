import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. ประกาศ URL ส่วนกลาง (จาก app.py บรรทัดที่ 42)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/edit?usp=sharing"

def get_connection():
    """สร้างการเชื่อมต่อกับ Google Sheets"""
    return st.connection("gsheets", type=GSheetsConnection)

def load_all_data():
    """ดึงข้อมูลทุก Sheet ที่ต้องใช้ (ย้ายมาจาก app.py บรรทัดที่ 67-73)"""
    try:
        def read_sheet(gid):
            base_url = SHEET_URL.split('/edit')[0]
            csv_url = f"{base_url}/export?format=csv&gid={gid}"
            return pd.read_csv(csv_url)

        # คืนค่าเป็น Dictionary เพื่อให้หน้าอื่นๆ เรียกใช้ง่าย
        return {
            "cash_flow": read_sheet("0"),
            "portfolio": read_sheet("1218817484"),
            "budget": read_sheet("2055623351"),
            "goals": read_sheet("1271566138"),
            "master": read_sheet("687236707"),
            "rules": read_sheet("700317739"),
            "fixed_expenses": read_sheet("2141043717")
        }
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return {}

def delete_asset(asset_name):
    """ฟังก์ชันลบสินทรัพย์ (ย้ายมาจาก app.py บรรทัดที่ 32)"""
    try:
        conn = get_connection()
        df = conn.read(worksheet="Portfolio", ttl=0)
        df = df[df['Asset_Name'] != asset_name]
        conn.update(worksheet="Portfolio", data=df)
        return True
    except:
        return False

def save_new_asset(new_a_df):
    """ฟังก์ชันบันทึกสินทรัพย์ใหม่ (ย้ายมาจาก app.py บรรทัดที่ 307-311)"""
    try:
        conn = get_connection()
        curr = conn.read(worksheet="Portfolio", ttl=0)
        # กรองตัวซ้ำออกแล้วต่อแถวใหม่เข้าไป
        name_to_save = new_a_df['Asset_Name'].iloc[0]
        updated = pd.concat([curr[curr['Asset_Name'] != name_to_save], new_a_df], ignore_index=True)
        conn.update(worksheet="Portfolio", data=updated)
        return True
    except:
        return False
