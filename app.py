import streamlit as st
import pandas as pd
from src.database import get_worksheet_data
from views import portfolio, cashflow, yearly_planning, reward_tracking, goals

# 1. Page Configuration
st.set_page_config(page_title="VELO. | Money Intelligence", page_icon="👻", layout="wide")

# --- CUSTOM CSS ---
# ผมเลือก Option 1 (ม่วงเข้ม + เขียว Lime) มาเป็นต้นแบบนะครับ อ่านง่ายและ Professional
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    /* 1. ตั้งค่าฟอนต์หลักและสีตัวหนังสือปกติ (Secondary Text) */
    html, body, [class*="css"], [data-testid="stWidgetLabel"] { 
        font-family: 'Inter', sans-serif; 
        color: #455A64 !important; /* Slate Gray: อ่านง่ายบนพื้นขาว */
    }
    
    /* 2. ตั้งค่าสีพื้นหลังหน้าเว็บเป็นสีขาว (เผื่อไว้) */
    .stApp {
        background-color: #FFFFFF;
    }

    /* 3. ตกแต่ง Sidebar (ถ้า Sidebar ยังหมอง ให้แก้ตรงนี้) */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA; /* เทาอ่อนมาก */
        border-right: 1px solid #EEEEEE;
    }
    
    /* 4. ตกแต่ง Header ของแอป (Gradient ม่วงเข้ม -> เขียว Lime) */
    .brand-container { 
        display: flex; 
        align-items: center; 
        gap: 12px; 
        margin-bottom: -10px; 
    }
    .app-title {
        font-size: 48px !important;
        font-weight: 800 !important;
        letter-spacing: -2px !important;
        /* Gradient ใหม่: จากม่วงเข้มไปเขียว Lime สว่าง */
        background: linear-gradient(90deg, #311B92 0%, #76FF03 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 !important;
    }
    .custom-icon { font-size: 40px; line-height: 1; }

    /* 5. เปลี่ยนสี Primary ของ Streamlit (ปุ่ม, Link, Active Elements) ให้เป็นม่วงสว่าง */
    .stButton>button {
        background-color: #6200EA;
        color: white;
        border-radius: 8px;
    }
    
    /* 6. แก้สีตารางและ Input ไม่ให้จาง */
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        color: #263238 !important; /* Charcoal */
    }
    
    </style>
    """, unsafe_allow_html=True)

# 3. SET CONSTANTS & NAVIGATION
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/edit?usp=sharing"

with st.sidebar:
    st.markdown("""<div class="brand-container"><span class="custom-icon">👻</span><h1 style="color:white; margin:0;">VELO.</h1></div>""", unsafe_allow_html=True)
    st.write("---")
    # --- [NEW] เพิ่มตัวปรับงบประมาณรายวันแบบ Dynamic ---
    st.subheader("⚙️ Strategic Budgeting")
    # งบกินรายวัน (ตัวเดิม)
    daily_food_target = st.number_input("Daily Food & Treat (฿)", value=300, step=50)
    # งบของเข้าบ้าน (รายเดือน)
    monthly_super_target = st.number_input("Monthly Supermarket (฿)", value=3000, step=500)
    # งบบิลประจำ (รายเดือน)
    monthly_fixed_target = st.number_input("Monthly Fixed Bills (฿)", value=630, step=10)
    menu = st.radio("MAIN MENU", ["💸 Cash Flow", "📈 Wealth Portfolio", "📅 Yearly Planning", "💳 Reward Tracking", "🎯 Goals & Budget"])
    st.write("---")
    st.caption("Strategic Intelligence v2.0")


# --- PAGE 1: CASH FLOW (New Strategic Layout) ---
if menu == "💸 Cash Flow":
    df_raw = get_worksheet_data("Expenses")
    df_portfolio = get_worksheet_data("Portfolio")
    cashflow.show_cashflow(df_raw, df_portfolio, daily_food_target, monthly_super_target, monthly_fixed_target)
   
# --- PAGE 2: WEALTH PORTFOLIO ---
elif menu == "📈 Wealth Portfolio":
    df_portfolio = get_worksheet_data("Portfolio")
    portfolio.show_portfolio(df_portfolio)

# --- PAGE: YEARLY PLANNING [GLOBAL PROFESSIONAL EDITION] ---
elif menu == "📅 Yearly Planning":
    df_fixed_expenses = get_worksheet_data("Fixed_Expenses")
    yearly_planning.show_yearly_planning(df_fixed_expenses)
        
# --- PAGE: REWARD TRACKING (Micro-Minimalist Digital Wallet) ---
elif menu == "💳 Reward Tracking":
    df_raw = get_worksheet_data("Expenses")
    df_master = get_worksheet_data("Cards_Master")
    df_rules = get_worksheet_data("Multiplier_Rules")
    reward_tracking.show_reward_tracking(df_raw, df_master, df_rules)
        
# --- PAGE: GOALS & BUDGET ---
elif menu == "🎯 Goals & Budget":
    goals.show_goals()
