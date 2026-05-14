import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Customer Data Cleaner", layout="wide")

st.title("📂 Customer Data Cleaner")
st.write("อัปโหลดไฟล์ CSV ของคุณเพื่อทำความสะอาดและวิเคราะห์ข้อมูล")

# 1. ส่วนการอัปโหลดไฟล์ (File Uploader)
uploaded_file = st.file_uploader("เลือกไฟล์ CSV ที่ต้องการ", type=["csv"])

if uploaded_file is not None:
    # อ่านข้อมูลจากไฟล์ที่อัปโหลด
    df = pd.read_csv(uploaded_file)
    
    st.success("โหลดไฟล์สำเร็จ!")
    
    # -----------------------------------------
    # Sidebar: การตั้งค่าการ Clean ข้อมูล
    # -----------------------------------------
    st.sidebar.header("Data Cleaning Options")
    
    # ตรวจสอบคอลัมน์ที่มีในไฟล์
    all_columns = df.columns.tolist()
    
    # ให้ผู้ใช้เลือกคอลัมน์ที่จะจัดการ (เพื่อความยืดหยุ่น)
    name_col = st.sidebar.selectbox("เลือกคอลัมน์ 'ชื่อ':", all_columns, index=all_columns.index('Name') if 'Name' in all_columns else 0)
    age_col = st.sidebar.selectbox("เลือกคอลัมน์ 'อายุ':", all_columns, index=all_columns.index('Age') if 'Age' in all_columns else 0)
    phone_col = st.sidebar.selectbox("เลือกคอลัมน์ 'เบอร์โทรศัพท์':", all_columns, index=all_columns.index('Phone') if 'Phone' in all_columns else 0)

    if st.sidebar.button("✨ Clean Data Now"):
        # กระบวนการ Cleaning (ปรับตามชื่อคอลัมน์ที่ผู้ใช้เลือก)
        df[name_col] = df[name_col].fillna('unknown')
        df = df.dropna(subset=[phone_col])
        
        # Clean ชื่อ
        df['Name_Cleaned'] = df[name_col].astype(str).str.strip().str.lower()
        
        # Clean เบอร์โทรด้วย Regex
        df['Phone_Numeric'] = df[phone_col].astype(str).str.replace(r'[-.\s]', '', regex=True)
        
        # ลบข้อมูลซ้ำ
        before_count = len(df)
        df = df.drop_duplicates(subset=['Phone_Numeric']).reset_index(drop=True)
        after_count = len(df)
        
        st.sidebar.info(f"ลบข้อมูลซ้ำออกไป {before_count - after_count} แถว")

    # -----------------------------------------
    # Main Content: แสดงผลข้อมูล
    # -----------------------------------------
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📋 Preview Data")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("📊 Basic Stats")
        st.write(df.describe())

    st.divider()

    # -----------------------------------------
    # Visualization Section
    # -----------------------------------------
    st.subheader("📈 Visualization")
    
    v_col1, v_col2 = st.columns(2)
    
    with v_col1:
        st.write(f"การกระจายตัวของคอลัมน์: {age_col}")
        fig, ax = plt.subplots()
        df[age_col].plot(kind='hist', bins=10, color='teal', edgecolor='white', ax=ax)
        st.pyplot(fig)
        
    with v_col2:
        if 'Name_Cleaned' in df.columns:
            st.write("Top 5 Customers (by frequency)")
            fig2, ax2 = plt.subplots()
            df['Name_Cleaned'].value_counts().head(5).plot(kind='pie', autopct='%1.1f%%', ax=ax2)
            st.pyplot(fig2)

    # ปุ่มดาวน์โหลด
    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Processed CSV",
        data=csv,
        file_name='processed_data.csv',
        mime='text/csv',
    )

else:
    st.info("👆 กรุณาอัปโหลดไฟล์ CSV เพื่อเริ่มต้นใช้งาน")
    # แสดงตัวอย่างหน้าตาไฟล์ที่ควรจะเป็น
    st.write("ตัวอย่างโครงสร้างไฟล์ที่แนะนำ:")
    st.code("Name,Age,Phone\nJohn Doe,30,081-234-5678")


if st.button("🏠 กลับหน้าหลัก"):
    st.switch_page("app.py")
