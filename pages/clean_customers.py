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
    # อ่านข้อมูลเริ่มต้น
    if 'raw_df' not in st.session_state or st.sidebar.button("🔄 Reset Data"):
        st.session_state['raw_df'] = pd.read_csv(uploaded_file)
        if 'cleaned_df' in st.session_state:
            del st.session_state['cleaned_df']

    df = st.session_state['raw_df']
    st.success("โหลดไฟล์สำเร็จ!")
    
    # -----------------------------------------
    # Sidebar: การตั้งค่าการ Clean ข้อมูล
    # -----------------------------------------
    st.sidebar.header("Data Cleaning Options")
    all_columns = df.columns.tolist()
    
    name_col = st.sidebar.selectbox("เลือกคอลัมน์ 'ชื่อ':", all_columns, index=all_columns.index('Name') if 'Name' in all_columns else 0)
    age_col = st.sidebar.selectbox("เลือกคอลัมน์ 'อายุ':", all_columns, index=all_columns.index('Age') if 'Age' in all_columns else 0)
    phone_col = st.sidebar.selectbox("เลือกคอลัมน์ 'เบอร์โทรศัพท์':", all_columns, index=all_columns.index('Phone') if 'Phone' in all_columns else 0)

    if st.sidebar.button("✨ Clean Data Now"):
        # คัดลอกข้อมูลมาเพื่อ Clean
        working_df = df.copy()
        working_df[name_col] = working_df[name_col].fillna('unknown')
        working_df = working_df.dropna(subset=[phone_col])
        
        # Clean ชื่อ
        working_df['Name_Cleaned'] = working_df[name_col].astype(str).str.strip().str.lower()
        
        # Clean เบอร์โทรด้วย Regex
        working_df['Phone_Numeric'] = working_df[phone_col].astype(str).str.replace(r'[-.\s]', '', regex=True)
        
        # ลบข้อมูลซ้ำ
        before_count = len(working_df)
        working_df = working_df.drop_duplicates(subset=['Phone_Numeric']).reset_index(drop=True)
        after_count = len(working_df)
        
        # สร้างกลุ่มอายุสำหรับการทำ Pie Chart
        bins = [0, 20, 30, 40, 50, 100]
        labels = ['Under 20', '21-30', '31-40', '41-50', 'Over 50']
        working_df['Age_Group'] = pd.cut(working_df[age_col], bins=bins, labels=labels)
        
        # เก็บลง session_state
        st.session_state['cleaned_df'] = working_df
        st.sidebar.info(f"ลบข้อมูลซ้ำออกไป {before_count - after_count} แถว")

    # -----------------------------------------
    # Main Content: แสดงผลข้อมูลเปรียบเทียบ
    # -----------------------------------------
    tab1, tab2 = st.tabs(["📋 Data Tables", "📊 Visualizations"])

    with tab1:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("1️⃣ Raw Data (Original)")
            st.dataframe(df, use_container_width=True, height=400)
            st.write(f"จำนวนแถวเริ่มต้น: {len(df)}")

        with col_b:
            st.subheader("2️⃣ Cleaned Data (After Process)")
            if 'cleaned_df' in st.session_state:
                st.dataframe(st.session_state['cleaned_df'], use_container_width=True, height=400)
                st.write(f"จำนวนแถวหลัง Clean: {len(st.session_state['cleaned_df'])}")
            else:
                st.info("💡 กดปุ่ม 'Clean Data Now' เพื่อดูข้อมูลที่จัดการแล้ว")

    # -----------------------------------------
    # Visualization Section
    # -----------------------------------------
    with tab2:
        if 'cleaned_df' in st.session_state:
            cdf = st.session_state['cleaned_df']
            st.subheader("📈 Insights from Cleaned Data")
            
            v_col1, v_col2 = st.columns(2)
            
            with v_col1:
                st.write(f"**Histogram: การกระจายตัวของอายุ ({age_col})**")
                fig, ax = plt.subplots()
                cdf[age_col].plot(kind='hist', bins=10, color='teal', edgecolor='white', ax=ax)
                ax.set_xlabel("Age")
                ax.set_ylabel("Frequency")
                st.pyplot(fig)
                
            with v_col2:
                st.write("**Pie Chart: สัดส่วนกลุ่มอายุ**")
                fig2, ax2 = plt.subplots()
                age_counts = cdf['Age_Group'].value_counts().sort_index()
                if not age_counts.empty:
                    age_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=ax2, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0'])
                    ax2.set_ylabel("")
                    st.pyplot(fig2)
                else:
                    st.write("ไม่มีข้อมูลเพียงพอสำหรับสร้างกราฟวงกลม")

            # ปุ่มดาวน์โหลด
            st.divider()
            csv = cdf.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Processed CSV",
                data=csv,
                file_name='processed_data.csv',
                mime='text/csv',
            )
        else:
            st.info("📊 กรุณาทำการ Clean Data ก่อนเพื่อดูภาพรวมสถิติ")

else:
    st.info("👆 กรุณาอัปโหลดไฟล์ CSV เพื่อเริ่มต้นใช้งาน")
    st.write("ตัวอย่างโครงสร้างไฟล์ที่แนะนำ:")
    st.code("Name,Age,Phone\nJohn Doe,30,081-234-5678")

# ปุ่มกลับหน้าหลัก
st.sidebar.divider()
if st.sidebar.button("🏠 กลับหน้าหลัก"):
    st.switch_page("app.py")
