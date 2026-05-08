import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# เก็บ URL ไว้ที่นี่ที่เดียว เวลาเปลี่ยนจะได้แก้ง่ายๆ
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/edit?usp=sharing"

def get_connection():
    """สร้างการเชื่อมต่อกับ Google Sheets"""
    return st.connection("gsheets", type=GSheetsConnection)

def load_all_data():
    """
    ฟังก์ชันเดียวที่ดึงข้อมูลทุก Sheet ที่คุณต้องใช้
    ดึงมาจาก app.py บรรทัดที่ 67-73
    """
    try:
        # ใช้ฟังก์ชันเดิมที่คุณเขียนไว้ (ปรับให้รับ GID โดยตรง)
        def read_sheet(gid):
            base_url = SHEET_URL.split('/edit')[0]
            csv_url = f"{base_url}/export?format=csv&gid={gid}"
            return pd.read_csv(csv_url)

        data = {
            "cash_flow": read_sheet("0"),
            "portfolio": read_sheet("1218817484"),
            "budget": read_sheet("2055623351"),
            "goals": read_sheet("1271566138"),
            "master": read_sheet("687236707"),
            "rules": read_sheet("700317739"),
            "fixed_expenses": read_sheet("2141043717")
        }
        return data
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

def delete_asset_logic(asset_name):
    """ย้ายมาจากฟังก์ชัน delete_asset ใน app.py"""
    try:
        conn = get_connection()
        df = conn.read(worksheet="Portfolio", ttl=0)
        df = df[df['Asset_Name'] != asset_name]
        conn.update(worksheet="Portfolio", data=df)
        return True
    except:
        return False
