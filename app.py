import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import calendar
import time
import plotly.graph_objects as go

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

# 4. DATA LOADING (Load once for all pages)
try:
    df_raw = load_public_data(SHEET_URL, "0")
    df_portfolio = load_public_data(SHEET_URL, "1218817484")
    df_budget = load_public_data(SHEET_URL, "2055623351")
    df_goals = load_public_data(SHEET_URL, "1271566138")
    df_master = load_public_data(SHEET_URL, "687236707")
    df_rules = load_public_data(SHEET_URL, "700317739")
    df_fixed_expenses = load_public_data(SHEET_URL, "2141043717")
except:
    st.error("Connection Error")

# --- PAGE 1: CASH FLOW (New Strategic Layout) ---
if menu == "💸 Cash Flow":
    st.markdown('<h1 class="app-title">CASH FLOW.</h1>', unsafe_allow_html=True)
    
    # 1. 📊 ADVANCED INSIGHTS (The Pilot's Cockpit)
    if not df_raw.empty:
        df_raw['Date'] = pd.to_datetime(df_raw['Date'])
        df_raw['Amount'] = pd.to_numeric(df_raw['Amount'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        
        month_list = df_raw['Date'].dt.strftime('%Y-%m').unique().tolist()
        month_list.sort(reverse=True)
        selected_month = st.selectbox("📅 Reviewing Month", month_list, label_visibility="collapsed")
        df_filtered = df_raw[df_raw['Date'].dt.strftime('%Y-%m') == selected_month]

        # --- [STEP 1] CONFIG: ความเร็วเป้าหมาย ---
        # --- [STEP 1] CONFIG: เชื่อมโยงงบประมาณจาก Sidebar ---
        BUDGET_PLAN = {
            "DAILY_LIMIT": daily_food_target,    # ใช้ชื่อใหม่จาก Sidebar
            "MONTHLY_SUPER": monthly_super_target, 
            "FIXED_BILLS": monthly_fixed_target
        }

        # 1. ตะกร้าของกินรายวัน (Daily Rhythm)
        daily_mask = df_raw['Category'].isin(['Food', 'Beverage', 'Dessert', '7-11'])
        df_daily = df_raw[daily_mask]
        
        # 2. ตะกร้าซุปเปอร์มาร์เก็ต (Monthly Inventory)
        super_mask = df_raw['Category'].isin(['Supermarket', 'Groceries'])
        df_super = df_raw[super_mask]
        
        # 3. ตะกร้าบิลคงที่ (Fixed Bills)
        fixed_mask = df_raw['Category'].isin(['Internet Bill', 'Music'])
        df_fixed = df_raw[fixed_mask]

        # --- [STEP 2] CALCULATION LOGIC: ต้องคำนวณให้เสร็จก่อนแสดงผล ---
        today = datetime.now().date()
        df_filtered['Date_Only'] = df_filtered['Date'].dt.date
        
        # กรองเฉพาะรายการที่เป็น "ของกินรายวัน" สำหรับคำนวณ Pace
        daily_items = df_filtered[df_filtered['Category'].isin(['Food', 'Beverage', 'Dessert', '7-11'])]
        total_daily_food = daily_items['Amount'].sum()
        
        # หาจำนวนวันที่ผ่านมาแล้ว
        num_days_passed = datetime.now().day if selected_month == datetime.now().strftime('%Y-%m') else df_filtered['Date'].dt.days_in_month.iloc[0]
        
        # ความเร็วการกินจริง (Pace) เทียบกับงบ 300.-
        actual_food_pace = total_daily_food / num_days_passed

        # คำนวณ Survival Buffer (ดึงจากหน้า Wealth มาหาร)
        if not df_portfolio.empty:
            temp_p = df_portfolio.copy()
            temp_p['Units'] = pd.to_numeric(temp_p['Units'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            temp_p['Price_Per_Unit'] = pd.to_numeric(temp_p['Price_Per_Unit'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            temp_p['Value'] = temp_p['Units'] * temp_p['Price_Per_Unit']
            liquid_cash = temp_p[temp_p['Type'] == 'Cash']['Value'].sum()
        else:
            liquid_cash = 0
            
        # สร้างตัวแปร survival_buffer เตรียมไว้
        survival_buffer = (liquid_cash / actual_food_pace) if actual_food_pace > 0 else 0

        # ยอดรวมเฉพาะของกินดื่มในเดือนนี้
        total_food_month = daily_items['Amount'].sum()

        # --- [STEP 3] DISPLAY METRICS: แสดงผลหน้าปัด ---
        # --- คำนวณยอดรวมทุกหมวดหมู่ในเดือนนี้ ---
        absolute_total_month = df_filtered['Amount'].sum()
        # แสดงยอดรวมสุทธิแบบเด่นๆ
        st.markdown(f"### 💰 Total Monthly Spend: `{absolute_total_month:,.2f} ฿`") 
        st.markdown(f"#### 🚀 Daily Rhythm: Food & Treats")
        m1, m2, m3, m4 = st.columns(4)

        # คำนวณความแม่นยำของงบกินดื่ม (ใช้อ้างอิง BUDGET_PLAN["DAILY_LIMIT"])
        target_so_far = BUDGET_PLAN["DAILY_LIMIT"] * num_days_passed
        diff_total = target_so_far - total_food_month
        
        m1.metric("Total Food Spent", f"{total_food_month:,.0f} ฿", 
                  delta=f"{diff_total:,.0f} ฿ from budget")
        
        m2.metric("Survival Buffer", f"{survival_buffer:,.0f} Days")

        # ยอดกินของวันนี้
        today_food_spent = daily_items[daily_items['Date_Only'] == today]['Amount'].sum()
        diff_today = BUDGET_PLAN["DAILY_LIMIT"] - today_food_spent
        m3.metric("Today's Food Spent", f"{today_food_spent:,.0f} ฿", 
                  delta=f"{diff_today:,.0f} ฿ left")
        
        # ความเร็วการกินจริง (Pace)
        diff_avg = BUDGET_PLAN["DAILY_LIMIT"] - actual_food_pace
        m4.metric("Avg Food Pace", f"{actual_food_pace:,.0f} / {BUDGET_PLAN['DAILY_LIMIT']}", 
                  delta=f"{diff_avg:,.0f} ฿ room")

        st.write("---")
        st.markdown("##### 📈 Food & Treats Spending Trend")
        
        # 1. เตรียมข้อมูล Cumulative (เน้นเฉพาะ "สายกิน")
        last_day = df_filtered['Date'].dt.days_in_month.iloc[0]
        date_range = pd.date_range(start=df_filtered['Date'].min().replace(day=1), 
                                  periods=last_day, freq='D')
        daily_df = pd.DataFrame({'Date': date_range, 'Date_Only': date_range.date})
        
        # --- กรองเฉพาะรายการของกินดื่ม ---
        food_daily = daily_items.groupby('Date_Only')['Amount'].sum().reset_index()
        
        # Merge และทำยอดสะสมเฉพาะค่ากิน
        chart_data = pd.merge(daily_df, food_daily, on='Date_Only', how='left').fillna(0)
        chart_data['Cumulative_Food'] = chart_data['Amount'].cumsum()
        
        # เส้นงบประมาณสะสม (300.- x วัน)
        chart_data['Cumulative_Budget'] = (chart_data.index + 1) * BUDGET_PLAN["DAILY_LIMIT"]

        # 2. สร้างกราฟ
        fig_trend = go.Figure()

        # เส้นยอดกินจริง (สีฟ้า)
        fig_trend.add_trace(go.Scatter(
            x=chart_data['Date'], y=chart_data['Cumulative_Food'],
            fill='tozeroy', name='Actual Food Spend',
            line=dict(color='#00D1FF', width=3),
            fillcolor='rgba(0, 209, 255, 0.1)'
        ))

        # เส้นงบกินเป้าหมาย (เส้นประสีแดง/ขาว)
        fig_trend.add_trace(go.Scatter(
            x=chart_data['Date'], y=chart_data['Cumulative_Budget'],
            name='Daily Food Target',
            line=dict(color='#FF4B4B', width=2, dash='dot')
        ))

        fig_trend.update_layout(
            hovermode="x unified",
            template="plotly_dark",
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(showgrid=False), xaxis=dict(showgrid=False)
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        st.write("---")
# 2. ➕ STRATEGIC ENTRY (อัปเกรดระบบปั่นแต้มและระบบหารจ่าย)
    with st.expander("📝 New Transaction"):
        with st.form("entry_form", clear_on_submit=True):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                date = st.date_input("Date", datetime.now())
                # เพิ่ม Category ให้ครบตามที่คุณต้องการ
                category = st.selectbox("Category", [
                    "Food", "Beverage", "Dessert", "7-11", "Gas", 
                    "E-commerce (Lazada, Shopee)", "Food/Transport (Grab)", 
                    "LINE Man", "Internet Bill", "Transport", "Barber",
                    "Shopping (Department Store)", "Supermarket", "Groceries", "Foreign Currencies", 
                    "Investment", "Bills", "Movie", "Video Game (stream,origin)", 
                    "Music", "Others"
                ])
                # --- เพิ่มช่องระบุความสัมพันธ์ ---
                relationship = st.selectbox("With Whom?", ["Self", "Partner (Gift)", "Family", "Friends", "Colleague"])
                
            with col_f2:
                # แยกยอดเต็ม กับ ยอดเพื่อนคืน
                total_bill_str = st.text_input("Total Bill (ยอดรูดเต็มหน้าสลิป)", placeholder="e.g. 500")
                refund_str = st.text_input("Refund / Split (ยอดเพื่อนคืน)", value="0")
                payment = st.selectbox("Payment Method", ["PromptPay", "UOB World", "UOB Premier", "UOB Grab", "UOB Mercedes", "KTC Unionpay Diamond", "KTC JCB Ultimate", "Kbank The Passion", "ttb absolute", "Central The 1 REDZ", "Cash"])
                
            with col_f3:
                note = st.text_input("Note (Optional)", placeholder="เช่น x5, มื้อพิเศษ")
                submitted = st.form_submit_button("Save Transaction")
            
            if submitted:
                try:
                    # Logic การคำนวณเบื้องหลัง
                    t_bill = float(total_bill_str.replace(',', '')) if total_bill_str else 0.0
                    refund = float(refund_str.replace(',', '')) if refund_str else 0.0
                    # ยอดที่เราจ่ายจริง (นี่คือยอดที่ระบบจะนำไปคิด Cash Flow)
                    actual_paid = t_bill - refund 
                    
                    if t_bill > 0:
                        with st.status("🚀 Processing Strategic Entry...", expanded=False) as status:
                            conn = st.connection("gsheets", type=GSheetsConnection)
                            existing_data = conn.read(worksheet="Expenses", ttl=0)
                            
                            new_entry = pd.DataFrame([{
                                "Date": date.strftime("%Y-%m-%d"), 
                                "Category": category, 
                                "Total_Bill": t_bill,       # บันทึกยอดเต็มเพื่อคิดแต้ม
                                "Refund_Amount": refund,     # บันทึกยอดที่ได้คืน
                                "Amount": actual_paid,       # ยอดรายจ่ายจริง
                                "Note": note, 
                                "Payment_Method": payment,
                                "Relationship": relationship # บันทึกความสัมพันธ์
                            }])
                            
                            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
                            conn.update(worksheet="Expenses", data=updated_df)
                            status.update(label="✅ Data Synced Successfully!", state="complete", expanded=False)
                        
                        # แจ้งเตือนให้เห็นภาพรวม
                        st.toast(f"บันทึกแล้ว! จ่ายจริง {actual_paid:,.2f} ฿ (สะสมแต้มจากยอด {t_bill:,.0f} ฿)", icon='💳')
                        time.sleep(1.2)
                        st.rerun()
                        
                    else:
                        st.warning("⚠️ กรุณาใส่ยอดเงินในช่อง Total Bill")
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
    # 3. 📊 VISUAL ANALYTICS & HISTORY
    if not df_raw.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Methods Breakdown")
            pay_sum = df_filtered.groupby('Payment_Method')['Amount'].sum().reset_index()
            fig_bar = px.bar(pay_sum, x='Payment_Method', y='Amount', color='Payment_Method', template="plotly_dark", height=300)
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            st.markdown("##### Category Distribution")
            cat_sum = df_filtered.groupby('Category')['Amount'].sum().reset_index()
            fig_pie = px.pie(cat_sum, values='Amount', names='Category', hole=0.4, template="plotly_dark", height=300)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.write("---")
        st.markdown("#### 📜 Recent Transactions")
        st.dataframe(
            df_filtered.sort_values('Date', ascending=False),
            column_config={
                "Amount": st.column_config.NumberColumn(format="฿%,.2f"),
                "Date": st.column_config.DateColumn(format="DD/MM/YYYY")
            },
            use_container_width=True, 
            hide_index=True
        )

# --- CASH FLOW FORECASTING SECTION (Hybrid Strategic) ---
        st.write("---")
        st.markdown("### 🔮 Cash Flow Forecasting")
        
        if not df_filtered.empty:
            # เตรียมข้อมูลพื้นฐาน
            days_in_month = calendar.monthrange(datetime.now().year, datetime.now().month)[1]
            days_passed = num_days_passed
            days_remaining = days_in_month - days_passed
            
            # 1. พยากรณ์ "เฉพาะค่ากิน" (Food Pace)
            projected_food = actual_food_pace * days_in_month
            food_budget_gap = (BUDGET_PLAN["DAILY_LIMIT"] * days_in_month) - projected_food
            
            # 2. ยอดใช้จ่าย "หมวดอื่นๆ" ที่จ่ายไปแล้วจริง (Supermarket, Bills, etc.)
            other_spent = df_filtered[~df_filtered['Category'].isin(['Food', 'Beverage', 'Dessert', '7-11'])]['Amount'].sum()
            
            # 3. ยอดรวมพยากรณ์สิ้นเดือน (Total projected everything)
            total_projected_all = projected_food + other_spent
            
            c1, c2, c3 = st.columns(3)
            
            with c1:
                # ตัวนี้จะบอกว่า สิ้นเดือนนี้เงินจะออกจากกระเป๋ารวมกี่บาท
                st.metric("Total Month-End Forecast", f"{total_projected_all:,.0f} ฿")
                st.caption(f"Estimate of EVERY expenditure (Food pace + Fixed costs)")
        
            with c2:
                # Safe-to-Spend: ยังคงคุมเฉพาะ "ค่ากิน" เพื่อไม่ให้วินัย President Kaphrao หลุด
                safe_to_spend = (target_so_far + (days_remaining * BUDGET_PLAN["DAILY_LIMIT"]) - total_food_month) / days_remaining if days_remaining > 0 else 0
                st.metric("Safe-to-Spend Today (Food)", f"{safe_to_spend:,.0f} ฿")
                st.caption(f"Max food budget for today to stay under {BUDGET_PLAN['DAILY_LIMIT']} ฿ avg.")
                
            with c3:
                # แสดงสถานะวินัยการกิน (Healthy หรือ Over-pacing)
                status_color = "🟢 Healthy" if food_budget_gap > 0 else "🔴 Over-pacing"
                st.subheader(status_color)
                # แถบ Progress เฉพาะงบกิน
                food_progress = min(max(total_food_month / (BUDGET_PLAN["DAILY_LIMIT"] * days_in_month), 0.0), 1.0)
                st.progress(food_progress)
                st.caption(f"Food Budget Used: {food_progress*100:.1f}%")
                
        # --- STRATEGIC BUCKET MONITORING ---
        st.write("---")
        st.markdown("### 📦 Strategic Budget Inventory")
        
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            # คำนวณยอด Supermarket (3,000)
            spent_super = df_filtered[df_filtered['Category'].isin(['Supermarket', 'Groceries'])]['Amount'].sum()
            rem_super = BUDGET_PLAN["MONTHLY_SUPER"] - spent_super
            st.metric("Supermarket Inventory", f"{rem_super:,.0f} ฿ Left", delta=f"Spent: {spent_super:,.0f}")
            st.progress(min(max(spent_super / BUDGET_PLAN["MONTHLY_SUPER"], 0.0), 1.0))
            st.caption(f"Monthly limit: {BUDGET_PLAN['MONTHLY_SUPER']:,} ฿")

        with col_s2:
            # คำนวณ Fixed Bills (630)
            spent_fixed = df_filtered[df_filtered['Category'].isin(['Internet Bill', 'Music'])]['Amount'].sum()
            rem_fixed = BUDGET_PLAN["FIXED_BILLS"] - spent_fixed
            st.metric("Fixed Bills Remaining", f"{rem_fixed:,.0f} ฿", delta=f"Paid: {spent_fixed:,.0f}")
            st.progress(min(max(spent_fixed / BUDGET_PLAN["FIXED_BILLS"], 0.0), 1.0))
            st.caption(f"Monthly target: {BUDGET_PLAN['FIXED_BILLS']:,} ฿")
            
        # --- LIFESTYLE & CONNECTION INSIGHT (Fixed Version) ---
        st.write("---")
        st.markdown("### Lifestyle & Connection Insight")
        
        # แก้จุดที่ 1: ใช้ df_filtered แทน df_raw เพื่อให้ข้อมูลเปลี่ยนตามเดือนที่เลือก
        analysis_df = df_filtered.copy() 
        
        # แก้จุดที่ 2: คำนวณ Actual_Paid จากคอลัมน์ใหม่ที่เราออกแบบไว้ (ถ้ายังไม่มีใน df)
        if 'Total_Bill' in analysis_df.columns and 'Refund_Amount' in analysis_df.columns:
            analysis_df['Actual_Paid'] = analysis_df['Total_Bill'] - analysis_df['Refund_Amount']
        else:
            # fallback กรณีข้อมูลแถวเก่าๆ ไม่มีคอลัมน์ใหม่ ให้ใช้ Amount ปกติ
            analysis_df['Actual_Paid'] = analysis_df['Amount']
        
        if 'Relationship' in analysis_df.columns and not analysis_df.empty:
            # 1. สร้างตัวเลือกความสัมพันธ์ (ดึงเฉพาะที่มีในเดือนนั้นๆ)
            all_relations = sorted(analysis_df['Relationship'].unique().tolist())
            selected_rel = st.selectbox("Select Relationship to Inspect:", all_relations)
            
            # 2. คำนวณยอดตามคนที่เลือก (ใช้ข้อมูลที่กรองเดือนแล้ว)
            lifestyle_df = analysis_df.groupby('Relationship')['Actual_Paid'].sum().reset_index()
            specific_spend = lifestyle_df[lifestyle_df['Relationship'] == selected_rel]['Actual_Paid'].sum()
            total_actual = lifestyle_df['Actual_Paid'].sum()
            
            lc1, lc2 = st.columns([1, 2])
            with lc1:
                st.markdown(f"##### Details for: {selected_rel}")
                st.metric(f"Total Spent with {selected_rel}", f"{specific_spend:,.0f} THB")
                st.caption(f"Net spending in {selected_month} (after refunds).")
                
                if total_actual > 0:
                    ratio = (specific_spend / total_actual) * 100
                    st.write(f"**{ratio:.1f}%** of monthly spend")
            
            with lc2:
                fig_life = px.pie(lifestyle_df, values='Actual_Paid', names='Relationship', 
                                  hole=0.6, color_discrete_sequence=px.colors.sequential.Mint_r,
                                  template="plotly_dark", title=f"Connection Mix: {selected_month}")
                fig_life.update_layout(margin=dict(l=0, r=0, t=30, b=0), showlegend=True)
                st.plotly_chart(fig_life, use_container_width=True)
        else:
            st.info(f"📅 No relationship data found for {selected_month}")

# --- PAGE 2: WEALTH PORTFOLIO ---
elif menu == "📈 Wealth Portfolio":
    st.markdown('<h1 class="app-title">WEALTH.</h1>', unsafe_allow_html=True)
    
    if not df_portfolio.empty:
        # 1. Calculation
        df_portfolio['Units'] = pd.to_numeric(df_portfolio['Units'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        df_portfolio['Price_Per_Unit'] = pd.to_numeric(df_portfolio['Price_Per_Unit'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        df_portfolio['Value'] = df_portfolio['Units'] * df_portfolio['Price_Per_Unit']
        
        total_v = df_portfolio['Value'].sum()
        st.metric("Total Net Worth", f"{total_v:,.2f} THB")

        # 2. Advanced Table View
        st.markdown("Asset Details")
        st.dataframe(
            df_portfolio,
            column_config={
                "Units": st.column_config.NumberColumn(format="%d"),
                "Price_Per_Unit": st.column_config.NumberColumn(format="฿%,.2f"),
                "Value": st.column_config.NumberColumn(format="฿%,.2f"),
                "Note": st.column_config.TextColumn("Note", width="large") # ขยายช่อง Note ให้กว้างขึ้น
            },
            use_container_width=True,
            hide_index=True
        )

        # 3. Charts
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(df_portfolio, values='Value', names='Asset_Name', hole=0.5, template="plotly_dark", title="Asset Allocation")
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            fig_type = px.bar(df_portfolio.groupby('Type')['Value'].sum().reset_index(), x='Type', y='Value', color='Type', template="plotly_dark", title="By Category")
            st.plotly_chart(fig_type, use_container_width=True)

    # 4. Management System
    with st.expander("🛠️ Manage Assets (Add/Edit/Delete)"):
        with st.form("asset_mgmt"):
            a1, a2, a3, a4 = st.columns(4)
            name = a1.text_input("Asset Name")
            atype = a2.selectbox("Type", ["Stock", "Crypto", "Cash", "Gold", "Real Estate"])
            unit = a3.number_input("Units", min_value=0, step=1)
            price = a4.number_input("Price/Unit", min_value=0, step=1)
            anote = st.text_input("Note")
            if st.form_submit_button("Save to Portfolio"):
                conn = st.connection("gsheets", type=GSheetsConnection)
                curr = conn.read(worksheet="Portfolio", ttl=0)
                new_a = pd.DataFrame([{"Asset_Name": name, "Type": atype, "Units": unit, "Price_Per_Unit": price, "Note": anote}])
                updated = pd.concat([curr[curr['Asset_Name']!=name], new_a], ignore_index=True)
                conn.update(worksheet="Portfolio", data=updated)
                st.rerun()
        
        st.write("---")
        to_del = st.selectbox("Select Asset to Remove", df_portfolio['Asset_Name'].unique())
        if st.button("🗑️ Confirm Delete"):
            if delete_asset(to_del): st.rerun()

# --- PAGE: YEARLY PLANNING [GLOBAL PROFESSIONAL EDITION] ---
elif menu == "📅 Yearly Planning":
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
