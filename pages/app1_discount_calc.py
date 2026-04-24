import streamlit as st

# 1. ส่วนหัวของโปรแกรม (UI)
st.title("💰 ระบบคำนวณส่วนลดร้านค้า")
st.info("คำนวณส่วนลดลูกค้าตามยอดการสั่งซื้อสะสม")

# 2. รับข้อมูลผ่าน Web Interface (แทนที่ input)
total_bill = st.number_input("กรุณากรอกยอดซื้อรวม (บาท):", min_value=0.0, step=100.0)

# 3. ส่วนการคำนวณ (ใช้ Logic เดิม)
if total_bill >= 1000:
    discount_rate = 0.15  # ส่วนลด 15%
elif total_bill >= 500:
    discount_rate = 0.10  # ส่วนลด 10%
else:
    discount_rate = 0.00  # ไม่ได้รับส่วนลด

discount_amount = total_bill * discount_rate
net_price = total_bill - discount_amount

# 4. แสดงผลลัพธ์บนหน้าเว็บ (แทนที่ print)
if st.button("คำนวณยอดสุทธิ"):
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("ยอดซื้อรวม", f"{total_bill:,.2f} บาท")
        st.write(f"ส่วนลดที่ได้รับ ({discount_rate*100:.0f}%)")
        
    with col2:
        st.metric("ยอดชำระจริง", f"{net_price:,.2f} บาท", delta=f"-{discount_amount:,.2f}")
    
    if discount_rate > 0:
        st.success(f"คุณได้รับส่วนลดทั้งหมด {discount_amount:,.2f} บาท")
    else:
        st.info("ยอดซื้อไม่ถึงเกณฑ์รับส่วนลด")



if st.button("🏠 กลับหน้าหลัก"):
    st.switch_page("app.py")

