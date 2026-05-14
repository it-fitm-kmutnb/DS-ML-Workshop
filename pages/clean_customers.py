import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Customer Data Cleaning & Analytics Dashboard", layout="wide")

st.title("🧼 Customer Data Cleaning & Analytics Dashboard")
st.write("อัปโหลดไฟล์ CSV เพื่อทำความสะอาดข้อมูลและดูสรุปผลสถิติแบบกราฟ")

# 2. ฟังก์ชันสำหรับทำความสะอาดข้อมูล
def clean_data(df, name_col, age_col, phone_col):
    df_cleaned = df.copy()
    
    # จัดการค่าว่าง
    df_cleaned[name_col] = df_cleaned[name_col].fillna('unknown')
    df_cleaned = df_cleaned.dropna(subset=[phone_col])
    
    # ล้างข้อมูลชื่อ
    df_cleaned['Name_Cleaned'] = df_cleaned[name_col].astype(str).str.strip().str.lower()
    df_cleaned.loc[df_cleaned['Name_Cleaned'] == '', 'Name_Cleaned'] = 'unknown'
    
    # ล้างเบอร์โทรศัพท์ (Regex)
    df_cleaned['Phone_Numeric'] = df_cleaned[phone_col].astype(str).str.replace(r'[-.\s]', '', regex=True)
    
    # ลบข้อมูลซ้ำ
    df_cleaned = df_cleaned.drop_duplicates(subset=['Phone_Numeric']).reset_index(drop=True)
    
    # สร้างกลุ่มช่วงอายุ (สำหรับ Pie Chart)
    bins = [0, 20, 30, 40, 50, 100]
    labels = ['Under 20', '21-30', '31-40', '41-50', 'Over 50']
    df_cleaned['Age_Group'] = pd.cut(df_cleaned[age_col], bins=bins, labels=labels)
    
    return df_cleaned

# 3. ส่วนการอัปโหลดไฟล์
uploaded_file = st.file_uploader("เลือกไฟล์ CSV ของคุณ", type=["csv"])

if uploaded_file:
    raw_df = pd.read_csv(uploaded_file)
    
    # ส่วน Sidebar สำหรับเลือกคอลัมน์
    st.sidebar.header("⚙️ Settings")
    cols = raw_df.columns.tolist()
    name_c = st.sidebar.selectbox("เลือกคอลัมน์ Name", cols, index=cols.index('Name') if 'Name' in cols else 0)
    age_c = st.sidebar.selectbox("เลือกคอลัมน์ Age", cols, index=cols.index('Age') if 'Age' in cols else 0)
    phone_c = st.sidebar.selectbox("เลือกคอลัมน์ Phone", cols, index=cols.index('Phone') if 'Phone' in cols else 0)

    # ปุ่มสำหรับเริ่มทำความสะอาด
    if st.sidebar.button("✨ Start Cleaning"):
        st.session_state['cleaned_df'] = clean_data(raw_df, name_c, age_c, phone_c)
        st.sidebar.success("Cleaning Completed!")

    # --- ส่วนการแสดงผล ---
    tab1, tab2, tab3 = st.tabs(["📊 Data Preview", "📈 Age Analysis", "🥧 Proportions"])

    with tab1:
        col_raw, col_clean = st.columns(2)
        with col_raw:
            st.subheader("Raw Data (Before)")
            st.dataframe(raw_df, use_container_width=True)
        
        with col_clean:
            st.subheader("Cleaned Data (After)")
            if 'cleaned_df' in st.session_state:
                st.dataframe(st.session_state['cleaned_df'], use_container_width=True)
            else:
                st.warning("กรุณากดปุ่ม 'Start Cleaning' เพื่อดูข้อมูลหลัง Clean")

    with tab2:
        st.subheader("📊 Age Distribution (Histogram)")
        if 'cleaned_df' in st.session_state:
            target_df = st.session_state['cleaned_df']
            
            fig, ax = plt.subplots(figsize=(10, 5))
            target_df[age_c].plot(kind='hist', bins=10, color='skyblue', edgecolor='black', ax=ax)
            ax.set_title("Distribution of Customer Age")
            ax.set_xlabel("Age")
            ax.set_ylabel("Frequency")
            st.pyplot(fig)
        else:
            st.info("รอข้อมูลที่ทำความสะอาดแล้วเพื่อแสดงผล Histogram")

    with tab3:
        st.subheader("🥧 Age Group Proportions (Pie Chart)")
        if 'cleaned_df' in st.session_state:
            target_df = st.session_state['cleaned_df']
            
            # เตรียมนับจำนวนกลุ่มอายุ
            age_counts = target_df['Age_Group'].value_counts().sort_index()
            
            fig2, ax2 = plt.subplots(figsize=(8, 8))
            age_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, 
                           colors=['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0'], ax=ax2)
            ax2.set_ylabel("") # ลบชื่อแกน Y
            st.pyplot(fig2)
            
            # แสดงตารางสรุปเล็กๆ
            st.table(age_counts)
        else:
            st.info("รอข้อมูลที่ทำความสะอาดแล้วเพื่อแสดงผล Pie Chart")

    # ปุ่มดาวน์โหลด
    if 'cleaned_df' in st.session_state:
        st.divider()
        csv = st.session_state['cleaned_df'].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Cleaned CSV", data=csv, file_name="cleaned_data.csv", mime="text/csv")

else:
    st.info("👋 กรุณาอัปโหลดไฟล์ CSV เพื่อเริ่มต้นการวิเคราะห์")
