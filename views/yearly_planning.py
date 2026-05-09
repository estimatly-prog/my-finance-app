import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
from datetime import datetime
import time
from src.database import update_fixed_expenses

# --- PAGE: YEARLY PLANNING [GLOBAL PROFESSIONAL EDITION] ---
def show_yearly_planning(df_fixed_expenses):
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
                "Cycle_Month": st.column_config.SelectboxColumn(("Cycle (1-12/ALL)"), options=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "ALL", "0"], help="เลือกเดือนที่บิลจะมา หรือเลือก ALL สำหรับทุกเดือน"),
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
                    # เปลี่ยนมาใช้ฟังก์ชันกลางที่เราแยกไว้
                    if update_fixed_expenses(edited_df):
                        st.success("Cloud Sync Successful!")
                        time.sleep(1)
                        st.rerun()
