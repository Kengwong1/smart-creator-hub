import streamlit as st
import random
import urllib.parse
import time

# --- 1. CONFIG (ตั้งค่าให้เบาที่สุด) ---
st.set_page_config(page_title="Creator Hub v14.2", page_icon="🚀", layout="centered")

# --- 2. UI แบบเน้นความไว ---
st.title("🚀 v14.2: ระบบทางด่วน (Direct Link)")
st.caption("ถ้าภาพไม่ขึ้น ให้กดปุ่มสีแดงด้านล่าง เพื่อเปิดภาพทันที")

# เมนูเลือก
with st.sidebar:
    st.header("⚙️ ตัวเลือก")
    # บังคับ Turbo เป็นค่าเริ่มต้น (ไวสุด)
    model = st.selectbox("โมเดล:", ["turbo (ไวปานจรวด)", "flux (สวยแต่ช้า)"])
    model_key = "turbo" if "turbo" in model else "flux"

# ช่องพิมพ์ (แนะนำพิมพ์อังกฤษเพื่อความไว)
user_input = st.text_input("พิมพ์คำสั่ง (แนะนำภาษาอังกฤษ เช่น Cat, Car):", placeholder="cat")

if st.button("⚡ สร้างภาพทันที"):
    if user_input:
        # สร้าง URL
        seed = random.randint(1, 999999)
        encoded = urllib.parse.quote(user_input)
        
        # URL สำหรับกดเปิดเอง (Direct Link)
        direct_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model={model_key}&nologo=true&seed={seed}"
        
        # 1. แสดงปุ่มใหญ่ๆ (ไม้ตายแก้ภาพไม่ขึ้น)
        st.success("✅ สั่งงานเรียบร้อย! ถ้าภาพด้านล่างไม่มา ให้กดปุ่มนี้:")
        st.markdown(f'''
            <a href="{direct_url}" target="_blank">
                <button style="
                    background-color: #FF4B4B; 
                    color: white; 
                    padding: 15px 32px; 
                    text-align: center; 
                    text-decoration: none; 
                    display: inline-block; 
                    font-size: 20px; 
                    margin: 4px 2px; 
                    cursor: pointer; 
                    border-radius: 12px; 
                    border: none;
                    width: 100%;">
                    🚀 คลิกเพื่อเปิดดูภาพทันที (Direct Open)
                </button>
            </a>
            ''', unsafe_allow_html=True)

        # 2. พยายามโหลดภาพโชว์ (เผื่อเน็ตดี)
        st.caption("👇 ตัวอย่างภาพ (ถ้าเน็ตดีจะขึ้นตรงนี้):")
        st.image(direct_url, caption=f"Prompt: {user_input}")
        
    else:
        st.warning("พิมพ์คำศัพท์ก่อนนะครับ เช่น cat")