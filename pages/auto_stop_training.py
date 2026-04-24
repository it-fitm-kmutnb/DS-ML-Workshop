import streamlit as st

count = 3
wait = 0
best_loss = float('inf')  # ตั้งค่าเป็นอนันต์เพื่อให้ค่าแรกที่กรอกชนะเสมอ
epoch = 1  #จำนวนรอบของการเรียนรู้ข้อมูล

st.title("--- ระบบจำลอง Early Stopping ---")
st.info("(กรอกค่า Loss ในแต่ละรอบ เพื่อดูว่า AI จะหยุดเทรนเมื่อไหร่)")

while wait < count:
    current_loss = st.number_input("Epoch {epoch} - กรอกค่า Loss: ", min_value=0.0, step=100.0)
    if current_loss < best_loss:
        # กรณีโมเดลเก่งขึ้น
        best_loss = current_loss
        wait = 0 
        st.success(f"New Best Loss: {best_loss}")
    else:
        # กรณีโมเดลไม่พัฒนา
        wait += 1
        st.info(f"ค่า loss ไม่ลดลง {wait} รอบแล้ว (ขีดจำกัดคือ {count})")
    
    epoch += 1

st.info("-" * 40)
st.info(f"หยุดการเทรนที่ Epoch {epoch-1}")
st.info(f"ค่า Loss ที่ดีที่สุดที่ทำได้คือ: {best_loss}")


if st.button("🏠 กลับหน้าหลัก"):
    st.switch_page("app.py")
