import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import calendar
import time
import plotly.graph_objects as go
from src.database import get_worksheet_data
from views import portfolio, cashflow

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
    # Using English for International Standards
    st.markdown('<h1 class="app-title">YEARLY STRATEGY.</h1>', unsafe_allow_html=True)
    
    if not df_fixed_expenses.empty:
        # 1. DATA PREPARATION & NORMALIZATION
        # Clean numeric data
        df_fixed_expenses['Amount'] = pd.to_numeric(df_fixed_expenses['Amount'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        
        # Calculate annual value based on frequency
        def get_annual_value(row):
            f = str(row['Frequency']).lower()
            val = row['Amount']
            if f == 'daily': return val * 365
            elif f == 'monthly': return val * 12
            elif f == 'yearly': return val
            return 0

        df_fixed_expenses['Yearly_Amount'] = df_fixed_expenses.apply(get_annual_value, axis=1)
        total_yearly = df_fixed_expenses['Yearly_Amount'].sum()
        total_monthly_eff = total_yearly / 12
        
        # 2. STRATEGIC KPI CARDS
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Total Yearly Commitment", f"฿{total_yearly:,.2f}")
            st.caption("Total projected expenditure per annum")
        with k2:
            st.metric("Monthly Provision", f"฿{total_monthly_eff:,.2f}")
            st.caption("Average monthly reserve required")
        with k3:
            st.metric("Expense Intensity", f"{len(df_fixed_expenses)} Items")
            st.caption("Number of active fixed obligations")
        
        st.write("---")
        
        # 3. MONTHLY CASH-OUT PROJECTION (WITH SMART GRADIENT)
        months_idx = [str(i) for i in range(1, 13)]
        projection = {m: 0 for m in months_idx}

        for _, row in df_fixed_expenses.iterrows():
            f, c, amt = str(row['Frequency']).lower(), str(row['Cycle_Month']).upper(), row['Amount']
            if f == 'daily':
                for m in months_idx: projection[m] += (amt * 30.42)
            elif f == 'monthly' or c == 'ALL' or c == '0':
                for m in months_idx: projection[m] += amt
            elif f == 'yearly' and c in projection:
                projection[c] += amt

        proj_df = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'Amount': list(projection.values())
        })

        st.markdown("#### 🔮 Monthly Cash-Out Projection")
        
        # Create chart with gradient color based on outflow intensity
        fig_proj = px.bar(
            proj_df, x='Month', y='Amount', text_auto='.2s',
            color='Amount', 
            color_continuous_scale=['#1E293B', '#00D1FF'], # Slate to VELO Blue
            template="plotly_dark"
        )
        
        # Professional Dashboard UI Polish
        fig_proj.update_layout(
            height=380,
            margin=dict(l=0, r=0, t=20, b=0),
            coloraxis_showscale=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            xaxis=dict(showgrid=False)
        )
        
        # Standard Provision Line
        fig_proj.add_hline(
            y=total_monthly_eff, 
            line_dash="dot", 
            line_color="#FF4B4B", 
            annotation_text="Provision Target", 
            annotation_position="top right"
        )
        
        st.plotly_chart(fig_proj, use_container_width=True)
        
# --- [NEW] SECTION: UPCOMING STRATEGIC ACTIONS ---
        st.write("---")
        # คำนวณหาเดือนหน้า
        current_month_num = datetime.now().month
        next_month_num = 1 if current_month_num == 12 else current_month_num + 1
        next_month_str = str(next_month_num)
        
        # กรองรายการที่จะเกิดขึ้นในเดือนหน้า ( Yearly ที่ระบุเดือนหน้า หรือรายการ Monthly ทั้งหมด)
        upcoming_items = df_fixed_expenses[
            (df_fixed_expenses['Cycle_Month'].astype(str) == next_month_str) | 
            (df_fixed_expenses['Cycle_Month'].astype(str).str.upper().isin(['ALL', '0']))
        ]

        st.markdown(f"#### 🔔 Next Month's Focus: {calendar.month_name[next_month_num]}")
        
        if not upcoming_items.empty:
            # แสดงเฉพาะรายการที่เป็น Yearly บิลใหญ่ก่อน เพื่อให้ความสำคัญ
            yearly_alerts = upcoming_items[upcoming_items['Frequency'].astype(str).str.lower() == 'yearly']
            
            if not yearly_alerts.empty:
                for _, alert in yearly_alerts.iterrows():
                    st.warning(f"**Annual Renewal:** {alert['Item']} (฿{alert['Amount']:,.2f}) is due next month! \n\n *Note: {alert['Note']}*")
            
            # ทำเป็นสรุปยอดรวมที่ต้องเตรียมสำหรับเดือนหน้า
            next_month_total = projection[next_month_str]
            st.success(f"**Liquidity Requirement:** You need to prepare approximately **฿{next_month_total:,.2f}** for next month's fixed obligations.")
        else:
            st.info("No major renewals scheduled for next month.")
            
# 4. STRATEGIC INVENTORY (LIVE EDITOR)
        st.write("---")
        st.markdown("#### 📋 Live Inventory Management")
        st.caption("You can edit, add, or delete items directly in the table below. Click 'Sync to Cloud' to save changes.")

        # ใช้ st.data_editor เพื่อให้ตารางแก้ไขได้แบบ Excel
        edited_df = st.data_editor(
            df_fixed_expenses[['Item', 'Amount', 'Frequency', 'Cycle_Month', 'Category', 'Note']],
            column_config={
                "Amount": st.column_config.NumberColumn("Cost (฿)", format="%.2f", min_value=0),
                "Frequency": st.column_config.SelectboxColumn("Billing", options=["Daily", "Monthly", "Yearly"]),
                "Cycle_Month": st.column_config.TextColumn("Cycle (1-12/ALL)"),
                "Category": st.column_config.SelectboxColumn("Category", options=["Food", "Mobile Internet", "Services", "Internet", "Sports Streaming", "Supermarket", "Gas", "Electricity Bill", "Water Bill", "Common area maintenance charges", "Youtube Premium", "Music Streaming", "Entertainment", "Groceries", "Transport", "Other"]),
                "Note": st.column_config.TextColumn("Context", width="large")
            },
            num_rows="dynamic", # ยอมให้กดเพิ่ม/ลบแถวได้เอง
            use_container_width=True,
            hide_index=True,
            key="fixed_expense_editor"
        )

        # ปุ่มบันทึกข้อมูล
        if st.button("🚀 Sync Changes to Cloud", use_container_width=True):
            try:
                with st.spinner("Updating Google Sheets..."):
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    # อัปเดตข้อมูลทั้งหมดกลับไปยัง Worksheet ชื่อ Fixed_Expenses
                    conn.update(worksheet="Fixed_Expenses", data=edited_df)
                    st.success("Cloud Sync Successful!")
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Sync Failed: {e}")
        
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
