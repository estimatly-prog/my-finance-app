import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import calendar
import time
import plotly.graph_objects as go
from src.database import get_worksheet_data
from views import portfolio, cashflow, yearly_planning

# 1. Page Configuration
st.set_page_config(page_title="VELO. | Money Intelligence", page_icon="👻", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    .brand-container { display: flex; align-items: center; gap: 12px; margin-bottom: -10px; }
    .app-title {
        font-size: 48px !important;
        font-weight: 800 !important;
        letter-spacing: -2px !important;
        background: linear-gradient(90deg, #FFFFFF 0%, #00D1FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 !important;
    }
    .custom-icon { font-size: 40px; line-height: 1; }
    </style>
    """, unsafe_allow_html=True)

# 2. DEFINE FUNCTIONS
def load_public_data(url, gid):
    try:
        base_url = url.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid={gid}"
        return pd.read_csv(csv_url)
    except: return pd.DataFrame()

def delete_asset(asset_name):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Portfolio", ttl=0)
        df = df[df['Asset_Name'] != asset_name]
        conn.update(worksheet="Portfolio", data=df)
        return True
    except: return False

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
    yearly_planning.show_yearly_planning(df_fixed)
        
# --- PAGE: REWARD TRACKING (Micro-Minimalist Digital Wallet) ---
elif menu == "💳 Reward Tracking":
    df_raw = get_worksheet_data("Expenses")
    df_master = get_worksheet_data("Cards_Master")
    df_rules = get_worksheet_data("Multiplier_Rules")
    
    st.markdown('<h1 class="app-title">MY WALLET.</h1>', unsafe_allow_html=True)
    
    if not df_master.empty and not df_raw.empty:
        # 1. Calculation Logic
        points_summary = []
        for _, card in df_master.iterrows():
            card_name = card['Card_Name']
            base_ratio = card['Point_Ratio'] if card['Point_Ratio'] > 0 else 25
            starting_pts = card['Starting_Points']
            img_url = card.get('Card_Image', 'https://via.placeholder.com/300x190?text=VELO.')
            
            card_tx = df_raw[df_raw['Payment_Method'] == card_name].copy()
            new_points = 0
            for _, tx in card_tx.iterrows():
                amt = tx.get('Total_Bill', 0)
                cat = tx.get('Category', 'Others')
                note = str(tx.get('Note', '')).lower()
                
                multiplier = 1
                import re
                match = re.search(r'x(\d+)', note)
                if match:
                    multiplier = int(match.group(1))
                elif 'df_rules' in locals():
                    rules = df_rules[df_rules['Card_Name'] == card_name]
                    cat_rule = rules[rules['Category'] == cat]
                    if not cat_rule.empty:
                        multiplier = cat_rule['Multiplier'].iloc[0]
                    else:
                        all_rule = rules[rules['Category'] == 'ALL']
                        if not all_rule.empty:
                            multiplier = all_rule['Multiplier'].iloc[0]
                
                new_points += (amt / base_ratio) * multiplier
            
            points_summary.append({
                "Card": card_name, "Total": starting_pts + new_points, 
                "New": new_points, "Image": img_url
            })

        # 2. Display Section
        st.markdown("#### 💎 Card Inventory")
        cards_per_row = 2
        for i in range(0, len(points_summary), cards_per_row):
            cols = st.columns(cards_per_row)
            for idx, p in enumerate(points_summary[i:i+cards_per_row]):
                with cols[idx]:
                    # ใช้ f-string ประกอบร่าง HTML แบบระมัดระวัง Tag
                    html_code = f"""
                    <div style="background-color: #121212; border-radius: 12px; padding: 12px; margin-bottom: 15px; border: 1px solid #222; display: flex; align-items: center; min-height: 90px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                        <div style="width: 40%; margin-right: 12px;">
                            <img src="{p['Image']}" style="width: 100%; border-radius: 6px; aspect-ratio: 1.58/1; object-fit: cover;">
                        </div>
                        <div style="width: 60%; overflow: hidden;">
                            <p style="color: #888; margin: 0; font-size: 0.7rem; font-weight: 500; text-transform: uppercase;">{p['Card']}</p>
                            <h3 style="color: white; margin: 2px 0; font-size: 1.4rem; font-weight: 700;">
                                {p['Total']:,.0f} <span style="font-size: 0.7rem; color: #00D1FF;">PTS</span>
                            </h3>
                            <p style="color: #00D1FF; margin: 0; font-size: 0.7rem;">▲ +{p['New']:,.0f}</p>
                        </div>
                    </div>
                    """
                    st.markdown(html_code, unsafe_allow_html=True)

        # 3. Insights
        st.write("---")
        st.markdown("#### 🤝 Relationship Strategy")
        c1, c2 = st.columns(2)
        with c1:
            if 'Relationship' in df_raw.columns:
                rel_sum = df_raw.groupby('Relationship')['Total_Bill'].sum().reset_index()
                fig_rel = px.pie(rel_sum, values='Total_Bill', names='Relationship', hole=0.6, template="plotly_dark")
                fig_rel.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
                st.plotly_chart(fig_rel, use_container_width=True)
        with c2:
            if 'Refund_Amount' in df_raw.columns:
                refund_df = df_raw[df_raw['Refund_Amount'] > 0].groupby('Relationship')[['Total_Bill', 'Refund_Amount']].sum().reset_index()
                st.dataframe(refund_df, use_container_width=True, hide_index=True)
    else:
        st.info("ไม่พบข้อมูลในระบบ")
        
# --- PAGE: GOALS & BUDGET ---
elif menu == "🎯 Goals & Budget":
    st.markdown('<h1 class="app-title">TARGETS.</h1>', unsafe_allow_html=True)
    # ใส่โค้ดส่วน Savings Goal และ Budget ของคุณต่อได้เลยครับ
    st.info("Section นี้ใช้ดู Budget และเป้าหมายการออมครับ")
