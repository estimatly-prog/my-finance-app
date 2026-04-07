import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import plotly.express as px

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
    menu = st.radio("MAIN MENU", ["💸 Cash Flow", "📈 Wealth Portfolio", "🎯 Goals & Budget"])
    st.write("---")
    st.caption("Strategic Intelligence v2.0")

# 4. DATA LOADING (Load once for all pages)
try:
    df_raw = load_public_data(SHEET_URL, "0")
    df_portfolio = load_public_data(SHEET_URL, "1218817484")
    df_budget = load_public_data(SHEET_URL, "2055623351")
    df_goals = load_public_data(SHEET_URL, "1271566138")
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

        # --- Calculation Logic ---
        today = datetime.now().date()
        start_of_week = today - pd.Timedelta(days=today.weekday())
        df_filtered['Date_Only'] = df_filtered['Date'].dt.date
        
        total_month = df_filtered['Amount'].sum()
        total_today = df_filtered[df_filtered['Date_Only'] == today]['Amount'].sum()
        total_week = df_filtered[df_filtered['Date_Only'] >= start_of_week]['Amount'].sum()
        
        num_days_passed = datetime.now().day if selected_month == datetime.now().strftime('%Y-%m') else df_filtered['Date'].dt.days_in_month.iloc[0]
        actual_daily_avg = total_month / num_days_passed
        
       # --- [FIXED] Calculation Logic for Survival Buffer ---
        today = datetime.now().date()
        start_of_week = today - pd.Timedelta(days=today.weekday())
        df_filtered['Date_Only'] = df_filtered['Date'].dt.date
        
        total_month = df_filtered['Amount'].sum()
        total_today = df_filtered[df_filtered['Date_Only'] == today]['Amount'].sum()
        total_week = df_filtered[df_filtered['Date_Only'] >= start_of_week]['Amount'].sum()
        
        num_days_passed = datetime.now().day if selected_month == datetime.now().strftime('%Y-%m') else df_filtered['Date'].dt.days_in_month.iloc[0]
        actual_daily_avg = total_month / num_days_passed
        
        # --- จุดที่แก้ไข: คำนวณ Value ก่อนเรียกใช้เพื่อป้องกัน KeyError ---
        if not df_portfolio.empty:
            # คลีนข้อมูลก่อนคำนวณ
            temp_p = df_portfolio.copy()
            temp_p['Units'] = pd.to_numeric(temp_p['Units'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            temp_p['Price_Per_Unit'] = pd.to_numeric(temp_p['Price_Per_Unit'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            temp_p['Value'] = temp_p['Units'] * temp_p['Price_Per_Unit']
            
            # ดึงเฉพาะรายการที่เป็น 'Cash' มาคำนวณ Buffer
            liquid_cash = temp_p[temp_p['Type'] == 'Cash']['Value'].sum()
        else:
            liquid_cash = 0
            
        survival_buffer = (liquid_cash / actual_daily_avg) if actual_daily_avg > 0 else 0

        # --- Display Metrics ---
        st.markdown(f"#### 🚀 Financial Pulse: {selected_month}")
        m1, m2, m3, m4 = st.columns(4)
        
        # ยอดรวมและแนวโน้ม
        m1.metric("Total Spent", f"{total_month:,.0f} ฿", delta=f"Avg {actual_daily_avg:,.0f}/day", delta_color="inverse")
        
        # Survival Buffer: เงินสดที่มีอยู่ได้อีกกี่วัน (Insight สำคัญ)
        m2.metric("Survival Buffer", f"{survival_buffer:,.0f} Days", help="จำนวนวันที่คุณจะอยู่ได้ด้วยเงินสดที่มี ณ อัตราการใช้จ่ายปัจจุบัน")
        
        # Velocity Check: วันนี้ใช้เร็วไปไหม
        velocity_color = "normal" if total_today <= actual_daily_avg else "inverse"
        m3.metric("Today's Velocity", f"{total_today:,.0f} ฿", delta="High Speed" if total_today > actual_daily_avg else "Stable", delta_color=velocity_color)
        
        # Weekly Accumulation
        m4.metric("Spent This Week", f"{total_week:,.0f} ฿")
        
        st.write("---")

    # 2. ➕ QUICK ENTRY (ย้ายลงมาและย่อไว้เพื่อให้ Insight นำหน้า)
    with st.expander("📝 New Transaction"):
        with st.form("entry_form", clear_on_submit=True):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                date = st.date_input("Date", datetime.now())
                category = st.selectbox("Category", ["Food", "Beverage", "Dessert", "7-11", "Transport", "Shopping", "Investment", "Bills", "Movie", "Video Game", "Music", "Others"])
            with col_f2:
                amount_str = st.text_input("Amount (THB)", value="", placeholder="e.g. 1,200")
                payment = st.selectbox("Payment Method", ["PromptPay", "UOB World", "UOB Premier", "UOB Grab", "UOB Mercedes", "KTC Unionpay Diamond", "KTC JCB Ultimate", "Kbank The Passion", "ttb absolute", "Cash"])
            with col_f3:
                note = st.text_input("Note (Optional)")
                submitted = st.form_submit_button("Save Transaction")
            
            if submitted:
                try:
                    amount = float(amount_str.replace(',', '')) if amount_str else 0.0
                    if amount > 0:
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        existing_data = conn.read(worksheet="Expenses", ttl=0)
                        new_entry = pd.DataFrame([{"Date": date.strftime("%Y-%m-%d"), "Category": category, "Amount": amount, "Note": note, "Payment_Method": payment}])
                        updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
                        conn.update(worksheet="Expenses", data=updated_df)
                        st.success("Saved Successfully!")
                        st.rerun()
                except: st.error("Please enter a valid number")

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
        st.markdown("#### 💎 Asset Details")
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

# --- PAGE 3: GOALS & BUDGET ---
elif menu == "🎯 Goals & Budget":
    st.markdown('<h1 class="app-title">TARGETS.</h1>', unsafe_allow_html=True)
    # ใส่โค้ดส่วน Savings Goal และ Budget เดิมของคุณที่นี่ครับ
    st.info("Section นี้ใช้ดู Budget และเป้าหมายการออมครับ")

st.write("---")
st.caption("Strategic Intelligence & Minimalist Design by Your AI Consultant")
