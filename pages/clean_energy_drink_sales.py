
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

# --- 0. Streamlit App Setup ---
st.set_page_config(layout="wide", page_title="Energy Drink Sales Analysis")
st.title("🥤 Energy Drink Sales Data Analysis")
st.write("แอปพลิเคชันสำหรับวิเคราะห์ยอดขาย โดยเริ่มต้นจากการอัปโหลดข้อมูลดิบของคุณ")

# --- 1. Data Upload Section ---
st.header("1. การนำข้อมูลเข้าระบบ (Data Upload)")

# Sidebar สำหรับการตั้งค่า
st.sidebar.header("⚙️ Data Settings")
uploaded_file = st.sidebar.file_uploader("เลือกไฟล์ CSV ของคุณ", type=["csv"])

# ตรวจสอบการ Reset ข้อมูล
if st.sidebar.button("🔄 Reset Data"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

if uploaded_file is not None:
    # อ่านข้อมูลเมื่อมีการอัปโหลดครั้งแรก
    if 'raw_df' not in st.session_state:
        st.session_state['raw_df'] = pd.read_csv(uploaded_file)
    
    df = st.session_state['raw_df']
    st.success(f"อัปโหลดไฟล์ '{uploaded_file.name}' สำเร็จ!")

    # --- 2. Sidebar: Cleaning Options ---
    st.sidebar.divider()
    st.sidebar.header("🧹 Cleaning Options")
    all_cols = df.columns.tolist()
    
    # ให้ผู้ใช้เลือกคอลัมน์ที่ตรงกับข้อมูลจริงในไฟล์
    date_col = st.sidebar.selectbox("เลือกคอลัมน์ 'วันที่':", all_cols, index=all_cols.index('Date') if 'Date' in all_cols else 0)
    sales_col = st.sidebar.selectbox("เลือกคอลัมน์ 'ยอดขาย':", all_cols, index=all_cols.index('Sales') if 'Sales' in all_cols else 0)
    prod_col = st.sidebar.selectbox("เลือกคอลัมน์ 'สินค้า':", all_cols, index=all_cols.index('Product') if 'Product' in all_cols else 0)
    reg_col = st.sidebar.selectbox("เลือกคอลัมน์ 'ภูมิภาค':", all_cols, index=all_cols.index('Region') if 'Region' in all_cols else 0)

    if st.sidebar.button("✨ Clean & Process Data"):
        working_df = df.copy()
        
        # 3.1 Type Conversion
        working_df[date_col] = pd.to_datetime(working_df[date_col], errors='coerce')
        working_df[prod_col] = working_df[prod_col].astype('category')
        working_df[reg_col] = working_df[reg_col].astype('category')
        
        # 3.2 Logic Correction & Imputation (จัดการค่าลบและเติมค่าว่างด้วยค่าเฉลี่ยรายสินค้า)
        working_df.loc[working_df[sales_col] < 0, sales_col] = np.nan
        working_df[sales_col] = working_df[sales_col].fillna(
            working_df.groupby(prod_col, observed=False)[sales_col].transform('mean')
        )
        
        # 3.3 Outlier Handling (ตัดค่าที่ผิดปกติสูงเกินไป)
        working_df = working_df[working_df[sales_col] <= 1000]
        
        # 4. Feature Engineering
        working_df['DayOfWeek'] = working_df[date_col].dt.day_name()
        working_df['Is_Above_Target'] = working_df[sales_col] > 150
        
        st.session_state['cleaned_df'] = working_df
        st.sidebar.success("ทำความสะอาดข้อมูลเสร็จแล้ว!")

    # --- 3. Main Content: Tabs ---
    tab1, tab2, tab3 = st.tabs(["📋 การตรวจสอบข้อมูล", "📂 สรุปข้อมูลรายกลุ่ม", "📈 กราฟวิเคราะห์"])

    with tab1:
        col_a, col_b = st.columns(2)
        
        # --- ฝั่งข้อมูลดิบ (Raw Data) ---
        with col_a:
            st.subheader("🔍 ข้อมูลดิบ (Raw Data)")
            
            # แสดง .info()
            st.write("**Data Structure (.info):**")
            buffer_raw = StringIO()
            df.info(buf=buffer_raw)
            st.code(buffer_raw.getvalue())
            
            # แสดง .describe()
            st.write("**Statistics (.describe):**")
            st.dataframe(df.describe(), use_container_width=True)
            
            # แสดงตารางข้อมูลตัวอย่าง
            st.write("**Data Preview (Top 10):**")
            st.dataframe(df.head(10), use_container_width=True)
        
        # --- ฝั่งข้อมูลที่ Clean แล้ว (Cleaned Data) ---
        with col_b:
            st.subheader("🧼 ข้อมูลที่ Clean แล้ว (Cleaned Data)")
            
            if 'cleaned_df' in st.session_state:
                cdf = st.session_state['cleaned_df']
                
                # แสดง .info() ของข้อมูลที่ Clean แล้ว
                st.write("**Cleaned Structure (.info):**")
                buffer_clean = StringIO()
                cdf.info(buf=buffer_clean)
                st.code(buffer_clean.getvalue())
                
                # แสดง .describe() ของข้อมูลที่ Clean แล้ว
                st.write("**Cleaned Statistics (.describe):**")
                st.dataframe(cdf.describe(), use_container_width=True)
                
                # แสดงตารางข้อมูลตัวอย่างที่ Clean แล้ว
                st.write("**Cleaned Preview (Top 10):**")
                st.dataframe(cdf.head(10), use_container_width=True)
            else:
                # กรณีที่ยังไม่ได้กดปุ่ม Clean
                st.info("💡 กรุณากดปุ่ม 'Clean & Process Data' ที่แถบด้านซ้าย เพื่อเปรียบเทียบข้อมูล")
                st.image("https://cdn-icons-png.flaticon.com/512/2037/2037061.png", width=100) # ตกแต่งเล็กน้อย

    with tab2:
        if 'cleaned_df' in st.session_state:
            cdf = st.session_state['cleaned_df']
            st.subheader("📊 รายงานสรุปผล")
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("**ยอดขายเฉลี่ยรายภูมิภาค**")
                st.dataframe(cdf.groupby(reg_col, observed=False)[sales_col].mean().sort_values(ascending=False))
            with c2:
                st.write("**ยอดขายรวมรายสินค้า**")
                st.dataframe(cdf.groupby(prod_col, observed=False)[sales_col].sum())
            
            st.write("**Pivot Table: สินค้า vs ภูมิภาค**")
            pivot = cdf.pivot_table(values=sales_col, index=prod_col, columns=reg_col, aggfunc='sum', observed=False)
            st.dataframe(pivot, use_container_width=True)

    with tab3:
        if 'cleaned_df' in st.session_state:
            cdf = st.session_state['cleaned_df']
            st.subheader("📈 กราฟแสดงผล (Visualizations)")
            
            # กราฟที่ 1: Line Chart
            st.write("**แนวโน้มยอดขายตามวันที่**")
            daily_sales = cdf.groupby(date_col)[sales_col].sum()
            fig1, ax1 = plt.subplots(figsize=(10, 4))
            daily_sales.plot(kind='line', marker='o', color='#1f77b4', ax=ax1)
            ax1.set_ylabel("Total Sales")
            ax1.grid(True, linestyle='--', alpha=0.7)
            st.pyplot(fig1)

            # กราฟที่ 2 & 3
            c3, c4 = st.columns(2)
            with c3:
                st.write("**ยอดขายรวมแยกตามภูมิภาค**")
                fig2, ax2 = plt.subplots()
                cdf.groupby(reg_col, observed=False)[sales_col].sum().plot(kind='bar', color='orange', ax=ax2)
                plt.xticks(rotation=45)
                st.pyplot(fig2)
            with c4:
                st.write("**สัดส่วนยอดขายตามประเภทสินค้า**")
                fig3, ax3 = plt.subplots()
                cdf.groupby(prod_col, observed=False)[sales_col].sum().plot(kind='pie', autopct='%1.1f%%', ax=ax3)
                ax3.set_ylabel("")
                st.pyplot(fig3)

            # ปุ่มดาวน์โหลด
            st.divider()
            csv_data = cdf.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 ดาวน์โหลดไฟล์ที่ Clean แล้ว (CSV)", data=csv_data, file_name="cleaned_sales_report.csv", mime="text/csv")

else:
    st.info("👆 กรุณาอัปโหลดไฟล์ CSV ทางแถบเมนูด้านซ้ายเพื่อเริ่มต้นใช้งาน")

# ปุ่มกลับหน้าหลัก
st.sidebar.divider()
if st.sidebar.button("🏠 กลับหน้าหลัก"):
    st.switch_page("app.py")
