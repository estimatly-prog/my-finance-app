import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import time

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
    st.subheader("⚙️ Settings")
    daily_target = st.number_input(
        "Daily Budget Target (฿)", 
        min_value=100, 
        max_value=2000, 
        value=300, 
        step=50,
        help="กำหนดเพดานรายจ่ายต่อวันที่คุณต้องการควบคุม"
    )
    menu = st.radio("MAIN MENU", ["💸 Cash Flow", "📈 Wealth Portfolio", "💳 Reward Tracking", "🎯 Goals & Budget"])
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
        DAILY_BUDGET_TARGET = daily_target 
        
        # --- [STEP 2] CALCULATION LOGIC: ต้องคำนวณให้เสร็จก่อนแสดงผล ---
        today = datetime.now().date()
        df_filtered['Date_Only'] = df_filtered['Date'].dt.date
        
        total_month = df_filtered['Amount'].sum()
        total_today = df_filtered[df_filtered['Date_Only'] == today]['Amount'].sum()
        
        # หาจำนวนวันที่ผ่านมาแล้ว
        num_days_passed = datetime.now().day if selected_month == datetime.now().strftime('%Y-%m') else df_filtered['Date'].dt.days_in_month.iloc[0]
        actual_daily_avg = total_month / num_days_passed

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
        survival_buffer = (liquid_cash / actual_daily_avg) if actual_daily_avg > 0 else 0

        # --- [STEP 3] DISPLAY METRICS: แสดงผลหน้าปัด ---
        st.markdown(f"#### 🚀 Financial Pulse: {selected_month}")
        m1, m2, m3, m4 = st.columns(4)

        st.write("---")
        st.markdown("##### 📈 Spending Trend vs Budget")
        
        # 1. เตรียมข้อมูล Cumulative Data
        # สร้าง DataFrame ของทุกวันในเดือนนี้
        last_day = df_filtered['Date'].dt.days_in_month.iloc[0]
        date_range = pd.date_range(start=df_filtered['Date'].min().replace(day=1), 
                                  periods=last_day, freq='D')
        
        daily_df = pd.DataFrame({'Date': date_range})
        daily_df['Date_Only'] = daily_df['Date'].dt.date
        
        # รวมยอดใช้จ่ายรายวันจริง
        actual_daily = df_filtered.groupby('Date_Only')['Amount'].sum().reset_index()
        
        # Merge และคำนวณยอดสะสม
        chart_data = pd.merge(daily_df, actual_daily, on='Date_Only', how='left').fillna(0)
        chart_data['Cumulative_Actual'] = chart_data['Amount'].cumsum()
        
        # คำนวณเส้นงบประมาณสะสม (Dynamic ตาม DAILY_BUDGET_TARGET)
        chart_data['Cumulative_Budget'] = (chart_data.index + 1) * DAILY_BUDGET_TARGET
        
        # 2. สร้างกราฟด้วย Plotly แบบมินิมอล
        import plotly.graph_objects as go
        
        fig_trend = go.Figure()
        
        # พื้นที่ยอดใช้จริง
        fig_trend.add_trace(go.Scatter(
            x=chart_data['Date'], y=chart_data['Cumulative_Actual'],
            fill='tozeroy', name='Actual Spend',
            line=dict(color='#00D1FF', width=3),
            fillcolor='rgba(0, 209, 255, 0.1)'
        ))
        
        # เส้นงบประมาณ
        fig_trend.add_trace(go.Scatter(
            x=chart_data['Date'], y=chart_data['Cumulative_Budget'],
            name='Budget Limit',
            line=dict(color='rgba(255, 255, 255, 0.3)', width=2, dash='dot')
        ))
        
        fig_trend.update_layout(
            hovermode="x unified",
            template="plotly_dark",
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(showgrid=False),
            xaxis=dict(showgrid=False)
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Total Spent: เทียบกับงบสะสม
        target_so_far = DAILY_BUDGET_TARGET * num_days_passed
        diff_total = target_so_far - total_month
        m1.metric("Total Spent", f"{total_month:,.0f} ฿", delta=f"{diff_total:,.0f} ฿ from budget", delta_color="normal")
        
        # Survival Buffer: โชว์จำนวนวัน (ใช้ตัวแปรที่คำนวณไว้ข้างบน)
        m2.metric("Survival Buffer", f"{survival_buffer:,.0f} Days")
        
        # Today's Velocity: วันนี้ใช้ไปเท่าไหร่ เหลือเท่าไหร่
        diff_today = DAILY_BUDGET_TARGET - total_today
        m3.metric("Today's Spent", f"{total_today:,.0f} ฿", delta=f"{diff_today:,.0f} ฿ left", delta_color="normal")
        
        # Avg Speed: ความเร็วเฉลี่ยเทียบกับเป้าหมาย 350
        diff_avg = DAILY_BUDGET_TARGET - actual_daily_avg
        m4.metric("Avg Speed", f"{actual_daily_avg:,.0f} / {DAILY_BUDGET_TARGET}", delta=f"{diff_avg:,.0f} ฿ room", delta_color="normal")
        
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
                    "LINE Man", "Internet Bill", "Transport", 
                    "Shopping (Department Store)", "Foreign Currencies", 
                    "Investment", "Bills", "Movie", "Video Game (stream,origin)", 
                    "Music", "Others"
                ])
                # --- เพิ่มช่องระบุความสัมพันธ์ ---
                relationship = st.selectbox("With Whom?", ["Self", "Partner (Gift)", "Family", "Friends", "Colleague"])
                
            with col_f2:
                # แยกยอดเต็ม กับ ยอดเพื่อนคืน
                total_bill_str = st.text_input("Total Bill (ยอดรูดเต็มหน้าสลิป)", placeholder="e.g. 500")
                refund_str = st.text_input("Refund / Split (ยอดเพื่อนคืน)", value="0")
                payment = st.selectbox("Payment Method", ["PromptPay", "UOB World", "UOB Premier", "UOB Grab", "UOB Mercedes", "KTC Unionpay Diamond", "KTC JCB Ultimate", "Kbank The Passion", "ttb absolute", "Cash"])
                
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


# --- หลังจากจบเงื่อนไขหน้า Cash Flow (ไม่มี Else คั่นกลางแล้ว) หน้าถัดไปถึงจะใช้ ELIF ได้ ---
elif menu == "📈 Wealth Portfolio":
    st.markdown('<h1 class="app-title">WEALTH.</h1>', unsafe_allow_html=True)
    # ... โค้ดส่วนที่เหลือของคุณ ...
    
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
