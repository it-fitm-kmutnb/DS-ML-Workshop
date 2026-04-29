
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ตั้งค่าความสวยงามของกราฟ
sns.set_theme(style="whitegrid")

st.title('📊 แอปพลิเคชันวิเคราะห์ข้อมูลคลังสินค้า')
st.write('แอปนี้จะช่วยทำความสะอาด จัดการ และแสดงผลข้อมูลสต็อกสินค้า')

@st.cache_data
def generate_raw_data():
    """สร้างข้อมูลดิบสำหรับคลังสินค้า"""
    n_rows = 120
    products = ['Energy_Original', 'Energy_Storm', 'Energy_Zero', 'Sport_Blue', 'Vit_C_Plus']
    regions = ['North', 'South', 'East', 'West', 'Central']

    data = {
        'SKU_ID': [f'SKU-{1000+i}' for i in range(n_rows)],
        'Product_Name': np.random.choice(products, n_rows),
        'Region': np.random.choice(regions, n_rows),
        'Current_Stock': np.random.randint(-15, 500, n_rows),
        'Unit_Cost': [np.random.uniform(15, 45) if np.random.random() > 0.15 else np.nan for _ in range(n_rows)],
        'Min_Requirement': [np.random.randint(50, 150) if np.random.random() > 0.05 else 9999 for _ in range(n_rows)],
        'Last_Restock': [(pd.to_datetime('2024-01-01') + pd.to_timedelta(np.random.randint(0, 100), unit='d')).strftime('%d/%m/%Y') for _ in range(n_rows)]
    }
    df_raw = pd.DataFrame(data)
    return df_raw

@st.cache_data
def process_and_clean_data(df_raw_input):
    """ประมวลผลและทำความสะอาดข้อมูลคลังสินค้า"""
    df = df_raw_input.copy()
    
    # 1. จัดการคอลัมน์ Last_Restock เป็นรูปแบบวันที่ที่ถูกต้อง
    df['Last_Restock'] = pd.to_datetime(df['Last_Restock'], dayfirst=True)

    # 2. จัดการสต๊อกติดลบ
    df.loc[df['Current_Stock'] < 0, 'Current_Stock'] = 0

    # 3. เติมราคาทุนที่หายไป (ใช้ Unit_Cost เฉลี่ยแยกตามกลุ่มสินค้า)
    df['Unit_Cost'] = df['Unit_Cost'].fillna(
        df.groupby('Product_Name')['Unit_Cost'].transform('mean')
    )

    # 4. จัดการค่า Min_Requirement ที่สูงผิดปกติ
    df.loc[df['Min_Requirement'] > 500, 'Min_Requirement'] = 100

    # 5. คำนวณมูลค่าทรัพย์สิน (Inventory_Value)
    df['Inventory_Value'] = df['Current_Stock'] * df['Unit_Cost']

    # 6. สร้างระบบแจ้งเตือน (Order_Signal)
    df['Order_Signal'] = np.where(df['Current_Stock'] < df['Min_Requirement'], 'ORDER NOW', 'STOCK OK')

    return df

# --- โหลดและประมวลผลข้อมูล ---
with st.spinner('กำลังสร้างและประมวลผลข้อมูล...'):
    df_raw_generated = generate_raw_data()
    df_cleaned = process_and_clean_data(df_raw_generated)

st.header('ข้อมูลคลังสินค้าที่ทำความสะอาดแล้ว')
st.dataframe(df_cleaned.head())
st.write(f"จำนวนรายการทั้งหมด: {len(df_cleaned)} รายการ")

st.subheader('สถิติข้อมูลเบื้องต้น')
st.dataframe(df_cleaned.describe())

# --- สรุปมูลค่าสต๊อกรวมแยกตามภูมิภาค ---
st.header('สรุปมูลค่าสต๊อกแยกตามภูมิภาค')
region_summary = df_cleaned.groupby('Region')['Inventory_Value'].sum().reset_index()
region_summary = region_summary.sort_values(by='Inventory_Value', ascending=False)
st.dataframe(region_summary)

fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.barplot(data=region_summary, x='Region', y='Inventory_Value', palette='viridis', ax=ax1)
ax1.set_title('Total Inventory Value by Region', fontsize=16, fontweight='bold')
ax1.set_xlabel('Region', fontsize=12)
ax1.set_ylabel('Total Value (THB)', fontsize=12)
st.pyplot(fig1)

# --- รายการสินค้าที่ต้องสั่งซื้อด่วน ---
st.header('รายการสินค้าที่ต้องสั่งซื้อด่วน')
order_list = df_cleaned[df_cleaned['Order_Signal'] == 'ORDER NOW'].copy()
order_list = order_list.sort_values(by='Product_Name')
st.dataframe(order_list[['SKU_ID', 'Product_Name', 'Region', 'Current_Stock', 'Min_Requirement', 'Inventory_Value']])
st.write(f"สรุป: มีสินค้าที่ต้องสั่งซื้อเพิ่มทั้งหมด {len(order_list)} รายการ")

# --- สถานะสุขภาพของสต็อก ---
st.header('สถานะสุขภาพของสต็อก')
fig2, ax2 = plt.subplots(figsize=(8, 5))
status_counts = df_cleaned['Order_Signal'].value_counts()
colors = ['#2ecc71' if (x == 'STOCK OK') else '#e74c3c' for x in status_counts.index]
status_counts.plot(kind='bar', color=colors, ax=ax2)
ax2.set_title('Inventory Health Status', fontsize=16, fontweight='bold')
ax2.set_xlabel('Status', fontsize=12)
ax2.set_ylabel('Number of SKUs', fontsize=12)
ax2.set_xticks(range(len(status_counts.index)), status_counts.index, rotation=0)
st.pyplot(fig2)
