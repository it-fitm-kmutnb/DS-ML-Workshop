import streamlit as st

st.set_page_config(page_title="MyApp", layout="wide")

st.title("🏠 หน้าหลัก")
st.write("### Boot Camp: Data Science and Machine Learning")
st.info("7 Day Intensive Hands-on Workshop")
st.write("##### Module 1: การจัดการข้อมูลพื้นฐานและโครงสร้างข้อมูลด้วย Python")

if st.button("💰 ระบบคำนวณส่วนลดตามยอดซื้อ"):
    st.switch_page("pages/app1_discount_calc.py")

st.write("##### Module 2: การควบคุมการไหลของข้อมูล ฟังก์ชัน และเครื่องมือ")

if st.button("⚡ ระบบวิเคราะห์ต้นทุนการผลิตและคำนวณภาษีความหวานสำหรับเครื่องดื่มชูกำลัง"):
    st.switch_page("pages/energy_drink_analyzer.py")

st.write("##### Module 3: Data Wrangling ด้วย Python")

if st.button("📊 แอปพลิเคชันวิเคราะห์ข้อมูลคลังสินค้า"):
    st.switch_page("pages/energy_inventory.py")
