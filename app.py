import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="VELO. | Money Intelligence", page_icon="👻", layout="wide")

# --- CUSTOM CSS (แก้ให้แยกส่วนไอคอนกับตัวหนังสือ) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    
    /* สร้าง Container สำหรับจัดวางไอคอนและชื่อแอป */
    .brand-container {
        display: flex;
        align-items: center;
        gap: 12px; /* ระยะห่างระหว่างผีกับชื่อ */
        margin-bottom: -10px;
    }

    .app-title {
        font-size: 48px !important;
        font-weight: 800 !important;
        letter-spacing: -2px !important;
        background: linear-gradient(90deg, #FFFFFF 0%, #00D1FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 !important; /* ลบ margin เพื่อให้ Flexbox คุมได้แม่นยำ */
    }

    .custom-icon {
        font-size: 40px; /* ขนาดของเจ้าผี */
        line-height: 1;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DEFINE FUNCTIONS (ต้องวางไว้ตรงนี้เพื่อให้ข้างล่างรู้จัก)
def load_public_data(url, gid):
    try:
        base_url = url.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid={gid}"
        return pd.read_csv(csv_url)
    except:
        return pd.DataFrame()

# [ตำแหน่ง 2: FUNCTIONS] - เพิ่มฟังก์ชันสำหรับลบสินทรัพย์
def delete_asset(asset_name):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Portfolio", ttl=0)
        # กรองเอาทุกอย่าง ยกเว้นตัวที่จะลบ
        df = df[df['Asset_Name'] != asset_name]
        conn.update(worksheet="Portfolio", data=df)
        return True
    except:
        return False

# 3. SET CONSTANTS
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysf3IANQsMJkttsGOUy9PSKO69D5TrsoWDdkpCTjid4/edit?usp=sharing"

# --- 4. START UI (ใช้โครงสร้างใหม่ที่เห็นไอคอนชัดเจน 100%) ---
st.markdown("""
    <div class="brand-container">
        <span class="custom-icon">👻</span>
        <h1 class="app-title">VELO.</h1>
    </div>
    """, unsafe_allow_html=True)
st.caption("STRATEGIC INTELLIGENCE & SPENDING VELOCITY")

# --- หลังจากนี้ค่อยเป็น Section 1 (Form) และ Section 2 (Data Loading) ---
# โดยใน Section 2 คุณจะเรียกใช้ load_public_data ได้ปกติแล้ว เพราะเราประกาศไว้ที่ข้อ 2 แล้วครับ

# --- SECTION 1: QUICK TRANSACTION ENTRY ---
with st.expander("➕ Quick Transaction Entry", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            date = st.date_input("Date", datetime.now())
            category = st.selectbox("Category", ["Food", "Beverage", "Dessert", "Transport", "Shopping", "Investment", "Bills", "Movie", "Video Game", "Music", "Others"])
        with col_f2:
            # เปลี่ยนเป็น text_input เพื่อให้เป็นช่องว่างได้
            amount_str = st.text_input("Amount (THB)", value="", placeholder="fill amount...")
            
            # แปลงค่าจาก String เป็น Float เพื่อเอาไปคำนวณหรือบันทึก
            try:
                amount = float(amount_str.replace(',', '')) if amount_str else 0.0
            except ValueError:
                amount = 0.0
                if amount_str: # ถ้าพิมพ์อะไรที่ไม่ใช่ตัวเลข
                    st.warning("⚠️ กรุณากรอกเฉพาะตัวเลขครับ")

            payment = st.selectbox("Payment Method", ["PromptPay", "UOB World", "UOB Premier", "UOB Grab", "UOB Mercedes", "KTC Unionpay Diamond", "KTC JCB Ultimate", "Kbank The Passion", "ttb absolute", "Cash"])
        with col_f3:
            note = st.text_input("Note (Optional)")
            submitted = st.form_submit_button("Save Transaction")
            
        if submitted:
            if amount > 0:
                try:
                    # 1. เชื่อมต่อ GSheets
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    
                    # 2. อ่านข้อมูล "ทั้งหมด" ที่มีอยู่ใน Sheets ตอนนี้ออกมาก่อน
                    # บรรทัดนี้สำคัญมาก เพื่อให้เรารู้ว่าบรรทัดล่าสุดอยู่ที่ไหน
                    existing_data = conn.read(worksheet="Expenses", ttl=0) # ttl=0 เพื่อไม่ให้ใช้แคชเก่า
                    
                    # 3. เตรียมข้อมูลใหม่
                    new_entry = pd.DataFrame([{
                        "Date": date.strftime("%Y-%m-%d"),
                        "Category": category,
                        "Amount": amount,
                        "Note": note,
                        "Payment_Method": payment
                    }])
                    
                    # 4. เอาข้อมูลใหม่ไป "ต่อตูด" ข้อมูลเก่า (Concat)
                    # ใช้ ignore_index=True เพื่อป้องกัน Index ซ้ำจนมันเขียนทับที่เดิม
                    updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
                    
                    # 5. เขียนกลับไปทั้งหมด (คราวนี้มันจะยาวขึ้นเรื่อยๆ ไม่ทับที่เดิม)
                    conn.update(worksheet="Expenses", data=updated_df)
                    
                    st.success("บันทึกสำเร็จ! ข้อมูลถูกต่อท้ายเรียบร้อย")
                    st.balloons()
                    st.rerun()
                except Exception as save_error:
                    st.error(f"เกิดข้อผิดพลาดในการบันทึก: {save_error}")
            else:
                st.error("กรุณาใส่จำนวนเงินด้วยครับ")

st.markdown("---")

# --- SECTION 2: DATA LOADING ---
try:
    df_raw = load_public_data(SHEET_URL, "0")          # Expenses
    df_portfolio = load_public_data(SHEET_URL, "1218817484") # Portfolio
    df_budget = load_public_data(SHEET_URL, "2055623351") # Budget
    df_goals = load_public_data(SHEET_URL, "1271566138")  # Goals
    
    # --- ANALYTICS DASHBOARD ---
    if not df_raw.empty:
        df_raw['Date'] = pd.to_datetime(df_raw['Date'])
        df_raw['Amount'] = pd.to_numeric(df_raw['Amount'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

        month_list = df_raw['Date'].dt.strftime('%Y-%m').unique().tolist()
        month_list.sort(reverse=True)
        selected_month = st.sidebar.selectbox("📅 Select Month", month_list)
        df_filtered = df_raw[df_raw['Date'].dt.strftime('%Y-%m') == selected_month]
        
        # 1. Budget Tracker Visuals
        st.subheader(f"📊 Monthly Budget Status: {selected_month}")
        if not df_budget.empty:
            actual_spending = df_filtered.groupby('Category')['Amount'].sum().reset_index()
            budget_comparison = pd.merge(df_budget, actual_spending, on='Category', how='left').fillna(0)
            
            b_cols = st.columns(len(budget_comparison))
            for i, row in budget_comparison.iterrows():
                with b_cols[i % len(b_cols)]:
                    actual = row['Amount']
                    budget = float(str(row['Monthly_Budget']).replace(',', ''))
                    p = min(actual / budget, 1.0) if budget > 0 else 0
                    st.metric(row['Category'], f"{actual:,.0f}", f"{p*100:.0f}% used", delta_color="inverse")
                    st.progress(p)

        st.markdown("---")
        
        # 2. Spending Detail Charts
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Methods Breakdown")
            pay_sum = df_filtered.groupby('Payment_Method')['Amount'].sum().reset_index()
            fig_bar = px.bar(pay_sum, x='Payment_Method', y='Amount', color='Payment_Method', template="plotly_dark", height=300)
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            st.markdown("#### Category Distribution")
            cat_sum = df_filtered.groupby('Category')['Amount'].sum().reset_index()
            fig_pie = px.pie(cat_sum, values='Amount', names='Category', hole=0.4, template="plotly_dark", height=300)
            st.plotly_chart(fig_pie, use_container_width=True)

        # 3. Dashboard Metrics
        st.subheader(f"💳 Spending Analysis: {selected_month}")
        total_ex = float(df_filtered['Amount'].sum())
        
        # คำนวณค่าเฉลี่ยรายวัน (หารด้วยจำนวนวันในเดือนนั้นๆ หรือ 30 วันมาตรฐาน)
        daily_avg = total_ex / 30 
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Monthly Amount", f"{total_ex:,.2f} THB")
        with c2:
            st.metric("Daily Average", f"{daily_avg:,.2f} THB")
        with c3:
            if total_ex > 0:
                # หาหมวดหมู่ที่มียอดรวมสูงสุด
                top_cat = df_filtered.groupby('Category')['Amount'].sum().idxmax()
                top_val = df_filtered.groupby('Category')['Amount'].sum().max()
                st.metric("Top Spending Categories", str(top_cat), f"{top_val:,.0f} THB")
                
        # 4. Recent Transactions (นำกลับมาให้แล้วครับ)
        st.markdown("---")
        st.subheader(f"📜 Recent Transactions ({selected_month})")
        recent_df = df_filtered.sort_values(by='Date', ascending=False)
        st.dataframe(
            recent_df[['Date', 'Category', 'Amount', 'Payment_Method', 'Note']], 
            use_container_width=True,
            hide_index=True
        )

    # --- [NEW] SECTION: SAVINGS GOAL TRACKER ---
    if not df_goals.empty:
        st.subheader("🎯 Savings & Financial Goals")
        goal_cols = st.columns(len(df_goals))
        
        for i, row in df_goals.iterrows():
            with goal_cols[i % len(df_goals)]:
                name = row['Goal_Name']
                target = float(str(row['Target_Amount']).replace(',', ''))
                current = float(str(row['Current_Saved']).replace(',', ''))
                progress = min(current / target, 1.0) if target > 0 else 0
                
                st.metric(name, f"{current:,.0f} / {target:,.0f} THB", f"{progress*100:.1f}%")
                st.progress(progress)
        st.markdown("---")
        
    # --- PORTFOLIO WEALTH SECTION (Updated Logic) ---
    st.markdown("---")
    st.subheader("📈 Portfolio Wealth")

    if not df_portfolio.empty:
        # 1. คลีนข้อมูล (แปลง Units และ Price เป็นตัวเลข)
        df_portfolio['Units'] = pd.to_numeric(df_portfolio['Units'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        df_portfolio['Price_Per_Unit'] = pd.to_numeric(df_portfolio['Price_Per_Unit'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    
        # 2. คำนวณ Value ใหม่ (Units * Price)
        df_portfolio['Value'] = df_portfolio['Units'] * df_portfolio['Price_Per_Unit']
    
        total_v = float(df_portfolio['Value'].sum())
    
        p_col1, p_col2 = st.columns([1, 2])
            with p_col1:
            st.metric("Total Net Worth", f"{total_v:,.2f} THB")
            # แสดงตารางแบบใหม่ที่มี Units และ Price ด้วย
            st.dataframe(
            df_portfolio[['Asset_Name', 'Type', 'Units', 'Price_Per_Unit', 'Value', 'Note']], 
            use_container_width=True, 
            hide_index=True
            )
    
            with p_col2:
            # กราฟวงกลมแบ่งสัดส่วนสินทรัพย์ (เพื่อให้ดูคูลเหมือนแอปธนาคาร)
            fig_portfolio = px.pie(
            df_portfolio, values='Value', names='Asset_Name', 
            hole=0.5, template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_portfolio.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_portfolio, use_container_width=True)

except Exception as e:
    st.error(f"Dashboard Error: {e}")

st.markdown("---")
st.caption("Strategic Intelligence & Minimalist Design by Your AI Consultant")

# [ตำแหน่ง 7: BOTTOM] - ASSET MANAGEMENT SYSTEM
st.markdown("---")
st.subheader("🛠️ Asset Management (Add/Edit/Delete)")

with st.expander("📝 Manage Your Assets", expanded=False):
    # ส่วนที่ 1: ฟอร์มเพิ่ม/แก้ไข
    with st.form("asset_form", clear_on_submit=True):
        col_a1, col_a2, col_a3, col_a4 = st.columns(4)
        with col_a1:
            a_name = st.text_input("Asset Name", placeholder="e.g. TISCO, BTC")
        with col_a2:
            a_type = st.selectbox("Type", ["Stock", "Crypto", "Cash", "Gold", "Real Estate"])
        with col_a3:
            a_units = st.number_input("Units", min_value=0.0, step=0.01)
        with col_a4:
            a_price = st.number_input("Price per Unit", min_value=0.0, step=0.1)
        
        a_note = st.text_input("Note (Optional)")
        a_submitted = st.form_submit_button("Save Asset")

        if a_submitted and a_name:
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                curr_p = conn.read(worksheet="Portfolio", ttl=0)
                
                new_asset = pd.DataFrame([{
                    "Asset_Name": a_name,
                    "Type": a_type,
                    "Units": a_units,
                    "Price_Per_Unit": a_price,
                    "Note": a_note
                }])
                
                # ถ้าชื่อซ้ำ ให้ลบของเก่าออกก่อน (เป็นการ Update ในตัว)
                curr_p = curr_p[curr_p['Asset_Name'] != a_name]
                updated_p = pd.concat([curr_p, new_asset], ignore_index=True)
                
                conn.update(worksheet="Portfolio", data=updated_p)
                st.success(f"Asset '{a_name}' saved!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # ส่วนที่ 2: ปุ่มลบข้อมูล
    st.markdown("---")
    st.write("🗑️ **Delete Asset**")
    if not df_portfolio.empty:
        asset_to_delete = st.selectbox("Select Asset to Remove", df_portfolio['Asset_Name'].unique())
        if st.button("Confirm Delete", type="primary"):
            if delete_asset(asset_to_delete):
                st.success(f"Deleted {asset_to_delete}")
                st.rerun()
