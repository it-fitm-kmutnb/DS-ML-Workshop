import streamlit as st
import pandas as pd
import json

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Energy Drink Analyzer", layout="wide")
st.title("⚡ Energy Formula & Sugar Tax Analyzer")
st.markdown("ระบบวิเคราะห์ต้นทุนการผลิตและคำนวณภาษีความหวานสำหรับเครื่องดื่มชูกำลัง")

# --- 2. ส่วนควบคุม (Sidebar) ---
st.sidebar.header("⚙️ การตั้งค่าพารามิเตอร์")

tax_rate = st.sidebar.slider(
    "อัตราภาษีน้ำตาล (บาท/กรัม)", 
    min_value=0.0, max_value=2.0, value=0.5, step=0.1
)

caffeine_limit = st.sidebar.number_input(
    "เกณฑ์ High Stimulant (mg)", 
    min_value=50, max_value=300, value=150
)

# --- 3. การจัดการข้อมูล ---
try:
    with open('energy_formulas.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # แปลงเป็น DataFrame
    df = pd.json_normalize(raw_data)
    df = df.explode('active_ingredients')

    # Data Cleaning & Calculation
    df['formula.cost_per_unit'] = df['formula.cost_per_unit'].fillna(0.0)
    df['Sugar_Tax'] = df['formula.sugar_g'] * tax_rate
    df['Total_Cost'] = df['formula.cost_per_unit'] + df['Sugar_Tax']
    
    df['Category'] = df['formula.caffeine_mg'].apply(
        lambda x: "🔴 High Stimulant" if x > caffeine_limit else "🟢 Standard"
    )

    # ปรับแต่งคอลัมน์เพื่อการแสดงผล
    display_df = df[[
        'brand', 'active_ingredients', 'formula.caffeine_mg', 
        'formula.sugar_g', 'Total_Cost', 'Category'
    ]].rename(columns={
        'brand': 'Brand',
        'active_ingredients': 'Ingredient',
        'formula.caffeine_mg': 'Caffeine (mg)',
        'formula.sugar_g': 'Sugar (g)',
        'Total_Cost': 'Total Cost (฿)'
    })

    # --- 4. การแสดงผลบนหน้าเว็บ ---
    col1, col2 = st.columns(2)
    with col1:
        st.metric("ค่าเฉลี่ยต้นทุนรวม", f"{display_df['Total Cost (฿)'].mean():.2f} ฿")
    with col2:
        high_stim_count = len(display_df[display_df['Category'] == "🔴 High Stimulant"].Brand.unique())
        st.metric("จำนวนแบรนด์คาเฟอีนสูง", high_stim_count)

    st.subheader("📊 ตารางสรุปข้อมูลการผลิต")
    st.dataframe(display_df, use_container_width=True)

    # ปุ่มดาวน์โหลด CSV
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 ดาวน์โหลดรายงาน (CSV)",
        data=csv,
        file_name='energy_report_streamlit.csv',
        mime='text/csv',
    )

except FileNotFoundError:
    st.error("❌ ไม่พบไฟล์ energy_formulas.json กรุณาตรวจสอบตำแหน่งไฟล์")


if st.button("🏠 กลับหน้าหลัก"):
    st.switch_page("app.py")

