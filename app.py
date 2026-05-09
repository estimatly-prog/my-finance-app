import streamlit as st
import pandas as pd
from src.database import get_worksheet_data
from views import portfolio, cashflow, yearly_planning, reward_tracking, goals
from streamlit_option_menu import option_menu

# 1. Page Configuration
st.set_page_config(page_title="VELO. | Money Intelligence", page_icon="👻", layout="wide")

# --- CUSTOM CSS ---
# ผมเลือก Option 1 (ม่วงเข้ม + เขียว Lime) มาเป็นต้นแบบนะครับ อ่านง่ายและ Professional
# --- CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    /* 1. บังคับพื้นหลังให้เป็นสีเทาเข้มแบบ Slate (ไม่ดำสนิทจนหมอง) */
    .stApp {
        background-color: #0E1117;
    }

    /* 2. บังคับสีฟอนต์พื้นฐานให้เป็นสีขาว/เทาอ่อน (แก้ปัญหาตัวหนังสือหาย) */
    html, body, [class*="css"], [data-testid="stWidgetLabel"], p, li { 
        font-family: 'Inter', sans-serif; 
        color: #E0E0E0 !important; 
    }

    /* 3. Sidebar ให้เข้มกว่าหน้าจอหลักเล็กน้อย */
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #1E1E1E;
    }
    
    /* 4. หัวข้อหลัก (ม่วง Electric Purple -> เขียว Lime สว่าง) */
    .app-title {
        font-size: 48px !important;
        font-weight: 800 !important;
        letter-spacing: -2px !important;
        background: linear-gradient(90deg, #9D50BB 0%, #76FF03 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 !important;
    }

    /* 5. ปรับสี Metric (สีม่วงสำหรับหัวข้อ และสีเขียว Lime สำหรับค่าตัวเลข) */
    [data-testid="stMetricLabel"] p {
        color: #9D50BB !important; /* Label สีม่วง */
        font-weight: 700 !important;
    }
    [data-testid="stMetricValue"] div {
        color: #76FF03 !important; /* Value สีเขียว Lime */
    }

    /* 6. ปรับสไตล์ตาราง (Dataframe) ไม่ให้ขาวโพลน */
    [data-testid="stDataFrame"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D;
        border-radius: 8px;
    }
    
    /* 7. ปรับสีปุ่มเป็นสีเขียว Lime ตัวหนังสือดำ (Cyberpunk Style) */
    .stButton>button {
        background-color: #8BC34A; /* สีเขียวหม่นที่ดูนุ่มนวลขึ้น */
        color: #FFFFFF !important;  /* เปลี่ยนตัวหนังสือบนปุ่มเป็นสีขาวให้อ่านง่าย */
        border-radius: 8px;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.2); /* ลดเงาฟุ้งให้ดูคลีนขึ้น */
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #7CB342; /* เข้มขึ้นเล็กน้อยตอน Hover */
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    /* แถม: ปรับสี Metric Value ให้เป็นสีเขียวโทนเดียวกัน */
    [data-testid="stMetricValue"] div {
        color: #8BC34A !important; 
    }

    .brand-container { 
        display: flex; 
        align-items: center; 
        gap: 15px;      /* เพิ่มช่องว่างระหว่างผีกับตัวหนังสือ */
        margin-bottom: 5px; 
        padding: 10px 0; /* เพิ่มพื้นที่ให้ดูไม่อึดอัด */
    }

    .custom-icon { 
        font-size: 55px !important; /* ขยายขนาดเจ้าผี 👻 ให้ใหญ่ขึ้น */
        line-height: 1; 
    }

    /* บังคับชื่อ VELO ใน Sidebar ให้ใหญ่และหนา */
    .brand-container h1 {
        font-size: 42px !important; 
        font-weight: 800 !important;
        letter-spacing: -2px !important;
        margin: 0 !important;
    }

    /* 8. ปรับสี Expander */
    .streamlit-expanderHeader {
        background-color: #161B22 !important;
        border-radius: 8px !important;
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
    menu = option_menu(
        menu_title=None, # ไม่เอาหัวข้อเมนู
        options=["💸 Cash Flow", "📈 Wealth Portfolio", "📅 Yearly Planning", "💳 Reward Tracking", "🎯 Goals & Budget"],
        icons=["wallet2", "graph-up", "calendar-date", "credit-card-2-front", "target"], 
        menu_icon="cast", 
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#8BC34A", "font-size": "20px"}, # สีเขียว Muted Lime
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin": "5px", 
                "color": "#E0E0E0",
                "--hover-color": "#1E1E1E" # สีตอนเอาเม้าส์ไปวาง
            },
            "nav-link-selected": {
                "background-color": "#311B92", # สีม่วงเข้ม (ธีมหลักของเรา)
                "color": "white",
                "font-weight": "600"
            },
        }
    )
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
