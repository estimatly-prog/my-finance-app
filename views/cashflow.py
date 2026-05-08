import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar
import time
from src.database import save_transaction # นำเข้าฟังก์ชันบันทึกที่เราเพิ่งสร้าง

def show_cashflow(df_raw, df_portfolio, daily_food_target, monthly_super_target, monthly_fixed_target):
    # ไม่ต้องมี st.set_page_config และ CSS ตรงนี้แล้ว (เพราะอยู่ที่ app.py)
    
    st.markdown('<h1 class="app-title">CASH FLOW.</h1>', unsafe_allow_html=True)
    
    if not df_raw.empty:
        # --- [STEP 1] DATA PREPARATION ---
        df_raw['Date'] = pd.to_datetime(df_raw['Date'])
        df_raw['Amount'] = pd.to_numeric(df_raw['Amount'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        
        month_list = df_raw['Date'].dt.strftime('%Y-%m').unique().tolist()
        month_list.sort(reverse=True)
        selected_month = st.selectbox("📅 Reviewing Month", month_list, label_visibility="collapsed")
        df_filtered = df_raw[df_raw['Date'].dt.strftime('%Y-%m') == selected_month].copy()

        BUDGET_PLAN = {
            "DAILY_LIMIT": daily_food_target,
            "MONTHLY_SUPER": monthly_super_target, 
            "FIXED_BILLS": monthly_fixed_target
        }

        # --- [STEP 2] CALCULATION LOGIC (ยกมาจากต้นฉบับคุณ) ---
        today = datetime.now().date()
        df_filtered['Date_Only'] = df_filtered['Date'].dt.date
        
        daily_items = df_filtered[df_filtered['Category'].isin(['Food', 'Beverage', 'Dessert', '7-11', 'Snack'])]
        total_daily_food = daily_items['Amount'].sum()
        
        num_days_passed = datetime.now().day if selected_month == datetime.now().strftime('%Y-%m') else df_filtered['Date'].dt.days_in_month.iloc[0]
        actual_food_pace = total_daily_food / num_days_passed if num_days_passed > 0 else 0

        total_food_month = daily_items['Amount'].sum()
        
        # Survival Buffer Logic
        if not df_portfolio.empty:
            temp_p = df_portfolio.copy()
            temp_p['Units'] = pd.to_numeric(temp_p['Units'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            temp_p['Price_Per_Unit'] = pd.to_numeric(temp_p['Price_Per_Unit'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            temp_p['Value'] = temp_p['Units'] * temp_p['Price_Per_Unit']
            liquid_cash = temp_p[temp_p['Type'] == 'Cash']['Value'].sum()
        else:
            liquid_cash = 0
            
        survival_buffer = (liquid_cash / actual_food_pace) if actual_food_pace > 0 else 0

        # --- [STEP 3] METRICS DISPLAY ---
        absolute_total_month = df_filtered['Amount'].sum()
        st.markdown(f"### 💰 Total Monthly Spend: `{absolute_total_month:,.2f} ฿`") 
        st.markdown(f"#### 🚀 Daily Rhythm: Food & Treats")
        
        m1, m2, m3, m4 = st.columns(4)
        target_so_far = BUDGET_PLAN["DAILY_LIMIT"] * num_days_passed
        diff_total = target_so_far - total_daily_food
        
        m1.metric("Total Food Spent", f"{total_daily_food:,.0f} ฿", delta=f"{diff_total:,.0f} ฿ from budget")
        m2.metric("Survival Buffer", f"{survival_buffer:,.0f} Days")
        
        today_food_spent = daily_items[daily_items['Date_Only'] == today]['Amount'].sum()
        diff_today = BUDGET_PLAN["DAILY_LIMIT"] - today_food_spent
        m3.metric("Today's Spent", f"{today_food_spent:,.0f} ฿", delta=f"{diff_today:,.0f} ฿ left")
        
        diff_avg = BUDGET_PLAN["DAILY_LIMIT"] - actual_food_pace
        m4.metric("Avg Food Pace", f"{actual_food_pace:,.0f}", delta=f"{diff_avg:,.0f} ฿ room")

        # --- [STEP 4] TREND CHART (Plotly) ---
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

        # --- [STEP 5] NEW TRANSACTION FORM ---
        st.write("---")
        with st.expander("📝 New Transaction"):
            with st.form("entry_form", clear_on_submit=True):
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    date = st.date_input("Date", datetime.now())
                    category = st.selectbox("Category", [
                    "Food", "Beverage", "Dessert", "Snack", "7-11", "Gas", 
                    "E-commerce (Lazada, Shopee)", "Food/Transport (Grab)", 
                    "LINE Man", "Internet Bill", "Transport", "Barber",
                    "Shopping (Department Store)", "Supermarket", "Groceries", "Foreign Currencies", 
                    "Investment", "Bills", "Movie", "Video Game (stream,origin)", 
                    "Music", "Others"
                ])
                    relationship = st.selectbox("With Whom?", ["Self", "Partner (Gift)", "Family", "Friends"])
                with col_f2:
                    total_bill_str = st.text_input("Total Bill", placeholder="500")
                    refund_str = st.text_input("Refund / Split", value="0")
                    payment = st.selectbox("Payment Method", ["PromptPay", "UOB World", "UOB Premier", "UOB Grab", "UOB Mercedes", "KTC Unionpay Diamond", "KTC JCB Ultimate", "Kbank The Passion", "ttb absolute", "Central The 1 REDZ", "Cash"])
                with col_f3:
                    note = st.text_input("Note")
                    submitted = st.form_submit_button("Save Transaction")
                
                if submitted:
                    t_bill = float(total_bill_str.replace(',', '')) if total_bill_str else 0.0
                    refund = float(refund_str.replace(',', '')) if refund_str else 0.0
                    actual_paid = t_bill - refund
                    
                    if t_bill > 0:
                        new_entry = pd.DataFrame([{
                            "Date": date.strftime("%Y-%m-%d"), 
                            "Category": category, 
                            "Total_Bill": t_bill, 
                            "Refund_Amount": refund, 
                            "Amount": actual_paid, 
                            "Note": note, 
                            "Payment_Method": payment,
                            "Relationship": relationship
                        }])
                        # เรียกใช้ฟังก์ชันที่เราสร้างใน database.py
                        if save_transaction(new_entry):
                            st.toast("✅ Data Synced Successfully!", icon='💳')
                            time.sleep(1)
                            st.rerun()
        
        # --- [STEP 6] DATA TABLES & FORECASTING ---
        # 3. 📊 VISUAL ANALYTICS & HISTORY
        st.write("---")
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
