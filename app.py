import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse # สำหรับจัดการข้อความ URL

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. ฟังก์ชันเรียกใช้ Gemini (สลับกุญแจ) ---
def call_gemini_with_retry(prompt_text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    for idx, key in enumerate(keys):
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(prompt_text)
            return response.text
        except Exception as e:
            if "429" in str(e) and idx < len(keys) - 1:
                continue
    return "Error: โควต้าเต็ม"

# --- 3. ฟังก์ชันเสกรูปใหม่ (ใช้ Pollinations AI - เสถียรสุดๆ) ---
def generate_image_pollinations(prompt, width, height):
    # เข้ารหัสข้อความเพื่อให้ส่งผ่าน URL ได้
    encoded_prompt = urllib.parse.quote(prompt)
    # สร้าง URL สำหรับดึงรูปภาพ (ไม่ต้องใช้ API Key!)
    image_url = f"https://pollinations.ai/p/{encoded_prompt}?width={width}&height={height}&seed={int(time.time())}&model=flux"
    return image_url

# --- 4. Sidebar ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub")
    menu = st.radio("เลือกเครื่องมือ:", ["🎨 เสกรูปภาพด้วย AI", "🎬 วางแผนคอนเทนต์", "💰 แคปชั่นป้ายยา"])
    st.divider()
    st.caption("v2.9 | Stable Engine")

# --- 5. การทำงาน ---
if menu == "🎨 เสกรูปภาพด้วย AI":
    st.header("🎨 AI ศิลปินเสกรูปภาพ (ระบบเสถียร 100%)")
    img_desc = st.text_area("อยากได้รูปอะไร? (ไทย/อังกฤษ)", placeholder="เช่น หุ่นยนต์ซ่อมมือถือ แสงสีนีออน")
    
    size_option = st.selectbox("เลือกขนาดภาพ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    if "9:16" in size_option: w, h = 540, 960
    elif "16:9" in size_option: w, h = 960, 540
    else: w, h = 768, 768

    if st.button("✨ เริ่มเสกรูป"):
        if not img_desc:
            st.warning("กรุณาใส่คำบรรยายก่อนค่ะ")
        else:
            with st.spinner("⏳ กำลังเตรียมความพร้อม..."):
                # ให้ Gemini ช่วยขยายความให้ภาพสวยขึ้น
                eng_prompt = call_gemini_with_retry(f"Write a short, cinematic English image prompt for: {img_desc}")
            
            if eng_prompt:
                st.info(f"✅ กำลังวาด: {eng_prompt[:50]}...")
                # ดึง URL รูปภาพ
                final_image_url = generate_image_pollinations(eng_prompt, w, h)
                
                # แสดงรูปภาพจาก URL ทันที
                st.image(final_image_url, caption="เสร็จแล้วค่ะ! (วาดโดย Pollinations AI)", use_container_width=True)
                
                # ปุ่มดาวน์โหลด
                st.markdown(f'[📥 ดาวน์โหลดรูปภาพคลิกที่นี่]({final_image_url})', unsafe_content_callback=True)

# (ส่วนเมนูอื่นๆ ใช้โค้ดเดิมได้เลยค่ะ)