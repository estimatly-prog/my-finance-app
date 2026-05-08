import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
# ดึงฟังก์ชันที่เราเพิ่งสร้างใน database.py มาใช้
from src.database import delete_asset, save_new_asset 

def show_portfolio(df_portfolio):
    st.markdown('<h1 class="app-title">WEALTH.</h1>', unsafe_allow_html=True)
    
    if not df_portfolio.empty:
        # 1. Calculation (เหมือนเดิมเป๊ะ)
        df_portfolio['Units'] = pd.to_numeric(df_portfolio['Units'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        df_portfolio['Price_Per_Unit'] = pd.to_numeric(df_portfolio['Price_Per_Unit'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        df_portfolio['Value'] = df_portfolio['Units'] * df_portfolio['Price_Per_Unit']
        
        total_v = df_portfolio['Value'].sum()
        st.metric("Total Net Worth", f"{total_v:,.2f} THB")

        # 2. Advanced Table View (เหมือนเดิมเป๊ะ)
        st.markdown("### Asset Details") 
        cols_to_show = ["Asset_Name", "Type", "Units", "Price_Per_Unit", "Value", "Note"]
        df_display = df_portfolio[cols_to_show].copy() 

        st.dataframe(
            df_display, 
            column_config={
                "Asset_Name": st.column_config.TextColumn("Asset Name", width="medium"),
                "Type": st.column_config.TextColumn("Category", width="small"),
                "Units": st.column_config.NumberColumn("Units", format="%d"),
                "Price_Per_Unit": st.column_config.NumberColumn("Price/Unit", format="฿%,.2f"),
                "Value": st.column_config.NumberColumn("Total Value", format="฿%,.2f"),
                "Note": st.column_config.TextColumn("Note", width="large")
            },
            use_container_width=True,
            hide_index=True
        )

        # 3. Charts (เหมือนเดิมเป๊ะ)
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(df_portfolio, values='Value', names='Asset_Name', hole=0.5, template="plotly_dark", title="Asset Allocation")
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            fig_type = px.bar(df_portfolio.groupby('Type')['Value'].sum().reset_index(), x='Type', y='Value', color='Type', template="plotly_dark", title="By Category")
            st.plotly_chart(fig_type, use_container_width=True)

    # 4. Management System (เหมือนเดิมเป๊ะ แค่เปลี่ยนวิธีบันทึกไปใช้ฟังก์ชันที่เราแยกไว้)
    with st.expander("🛠️ Manage Assets (Add/Edit/Delete)"):
        with st.form("asset_mgmt"):
            a1, a2, a3, a4 = st.columns(4)
            name = a1.text_input("Asset Name")
            atype = a2.selectbox("Type", ["Stock", "Crypto", "Cash", "Gold", "Real Estate"])
            unit = a3.number_input("Units", min_value=0, step=1)
            price = a4.number_input("Price/Unit", min_value=0, step=1)
            anote = st.text_input("Note")
            
            if st.form_submit_button("Save to Portfolio"):
                new_a = pd.DataFrame([{"Asset_Name": name, "Type": atype, "Units": unit, "Price_Per_Unit": price, "Note": anote}])
                # เรียกใช้ฟังก์ชันบันทึกที่เราแยกไว้ใน database.py
                if save_new_asset(new_a):
                    st.rerun()
        
            st.write("---")
                
                # 1. เช็คก่อนว่า df_portfolio มีข้อมูลและมีคอลัมน์ที่ต้องการไหม
                if not df_portfolio.empty and 'Asset_Name' in df_portfolio.columns:
                    # ดึงรายชื่อมาทำ List และเอาค่าซ้ำออก
                    asset_list = df_portfolio['Asset_Name'].unique().tolist()
                    
                    if asset_list:
                        to_del = st.selectbox("Select Asset to Remove", asset_list)
                        
                        if st.button("🗑️ Confirm Delete"):
                            # เรียกใช้ฟังก์ชันลบที่เราแยกไว้ใน src/database.py
                            if delete_asset(to_del): 
                                st.success(f"ลบ {to_del} เรียบร้อยแล้ว!")
                                time.sleep(1) # ให้ User เห็นข้อความก่อน
                                st.rerun()
                    else:
                        st.info("ไม่มีรายการสินทรัพย์ให้ลบ")
                else:
                    st.warning("⚠️ ไม่สามารถโหลดรายชื่อสินทรัพย์เพื่อลบได้ (Check Data Connection)")
