# ... (โค้ดส่วนบนเหมือนเดิม) ...

st.title("🧠 Financial Brain Pro")

try:
    # 4. Data Loading - สังเกตการย่อหน้า (ต้องมี Space ข้างหน้า)
    df_expense = conn.read(worksheet="Expenses", ttl="5s") 
    df_portfolio = conn.read(worksheet="Portfolio", ttl="1m")

    # Data Cleaning Logic - ต้องย่อหน้าให้ตรงกัน
    for df in [df_expense, df_portfolio]:
        if not df.empty:
            target_col = 'Amount' if 'Amount' in df.columns else 'Value'
            if target_col in df.columns:
                df[target_col] = df[target_col].astype(str).str.replace(',', '').str.strip()
                df[target_col] = pd.to_numeric(df[target_col], errors='coerce').fillna(0)

    # --- SECTION 1: QUICK TRANSACTION ENTRY ---
    with st.expander("➕ Quick Transaction Entry", expanded=True):
        # ... (โค้ดส่วน Form ทั้งหมดต้องย่อหน้าเข้ามา) ...
        with st.form("entry_form", clear_on_submit=True):
            # โค้ดภายใน Form...
            # (ผมแนะนำให้ก๊อปปี้จากไฟล์เต็มด้านล่างครับ)
