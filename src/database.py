import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

def get_connection():
    """สร้างการเชื่อมต่อโดยใช้ Service Account จาก Secrets"""
    return st.connection("gsheets", type=GSheetsConnection)

def load_all_data():
    """ดึงข้อมูลทุกหน้าผ่านระบบ Connection (ปลอดภัยกว่า)"""
    data = {}
    try:
        conn = get_connection()
        # ใช้ชื่อ Worksheet ให้ตรงกับใน Google Sheets ของคุณเป๊ะๆ
        data["cash_flow"] = conn.read(worksheet="Expenses", ttl=0) # หรือชื่อแผ่นแรกของคุณ
        data["portfolio"] = conn.read(worksheet="Portfolio", ttl=0)
        data["budget"] = conn.read(worksheet="Budget", ttl=0)
        data["goals"] = conn.read(worksheet="Goals", ttl=0)
        data["Cards_Master"] = conn.read(worksheet="Cards_Master", ttl=0)
        data["rules"] = conn.read(worksheet="Rules", ttl=0)
        data["fixed_expenses"] = conn.read(worksheet="Fixed_Expenses", ttl=0)
        return data
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return {}

def delete_asset(asset_name):
    try:
        conn = get_connection()
        df = conn.read(worksheet="Portfolio", ttl=0)
        df = df[df['Asset_Name'] != asset_name]
        conn.update(worksheet="Portfolio", data=df)
        return True
    except: return False

def save_new_asset(new_a_df):
    try:
        conn = get_connection()
        curr = conn.read(worksheet="Portfolio", ttl=0)
        name_to_save = new_a_df['Asset_Name'].iloc[0]
        updated = pd.concat([curr[curr['Asset_Name'] != name_to_save], new_a_df], ignore_index=True)
        conn.update(worksheet="Portfolio", data=updated)
        return True
    except: return False
