import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import io
from PIL import Image
import time

# --- 1. ตั้งค่าพื้นฐาน ---
st.set_page_config(page_title="Smart Creator Hub", page_icon="🎬", layout="wide")
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
hf_api_key = os.getenv("HUGGINGFACE_API_KEY")

if not gemini_api_key:
    st.error("❌ ไม่พบ Gemini API Key")
    st.stop()

genai.configure(api_key=gemini_api_key)
model_text = genai.GenerativeModel('gemini-flash-latest')

# --- 2. ฟังก์ชันเสกรูปพร้อมระบบ Auto-Retry และกำหนดขนาด ---
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
hf_headers = {"Authorization": f"Bearer {hf_api_key}"}

def generate_image_with_retry(prompt, width, height, max_retries=5):
    # กำหนดพารามิเตอร์ขนาดภาพ
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": width,
            "height": height
        }
    }
    for i in range(max_retries):
        response = requests.post(HF_API_URL, headers=hf_headers, json=payload)
        if response.status_code == 200:
            return response.content
        elif response.status_code == 503:
            st.info(f"⏳ เซิร์ฟเวอร์วาดรูปกำลังตื่น... ลองใหม่ครั้งที่ {i+1}/{max_retries}")
            time.sleep(10)
        else:
            raise Exception(f"Hugging Face Error: {response.status_code}")
    raise Exception("เซิร์ฟเวอร์ไม่ว่างนานเกินไป")

# --- 3. Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub")
    st.write("สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio(
        "เลือกเครื่องมือ:",
        ["🎨 เสกรูปภาพด้วย AI", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิปให้น่าคลิก", "💬 ผู้ช่วยตอบคอมเมนต์"]
    )
    st.divider()
    st.caption("v2.3 | Multi-Size Support")

# --- โซน 1: เสกรูปภาพด้วย AI (เพิ่มเลือกขนาด) ---
if menu == "🎨 เสกรูปภาพด้วย AI":
    st.header("🎨 AI ศิลปินเสกรูปภาพตามขนาดที่ต้องการ")
    
    img_desc = st.text_area("บรรยายภาพที่ต้องการ (ภาษาไทย)", placeholder="เช่น นกคริสตัลในป่าเวทมนตร์")
    
    # --- ส่วนเลือกขนาดภาพ ---
    st.subheader("📏 เลือกขนาดภาพ")
    size_option = st.selectbox(
        "เลือกขนาดให้เหมาะกับแพลตฟอร์ม:",
        ["แนวตั้ง (9:16) - สำหรับ TikTok/Reels", "แนวนอน (16:9) - สำหรับ Facebook/YouTube", "จัตุรัส (1:1) - สำหรับ IG/Profile"]
    )
    
    # กำหนดตัวเลข Width/Height (SDXL ทำงานได้ดีที่สุดที่ประมาณ 1 ล้านพิกเซล)
    if "9:16" in size_option:
        w, h = 768, 1344
    elif "16:9" in size_option:
        w, h = 1344, 768
    else:
        w, h = 1024, 1024

    if st.button("✨ เริ่มเสกรูป"):
        if not hf_api_key:
            st.error("กรุณาใส่ Hugging Face Token ก่อนนะคะ")
        elif not img_desc:
            st.warning("ใส่คำอธิบายภาพก่อนค่ะ")
        else:
            # ส่วนแปลภาษา (พร้อม Retry)
            eng_prompt = ""
            success_trans = False
            for i in range(3):
                try:
                    with st.spinner(f"⏳ กำลังแปลภาษา... (ครั้งที่ {i+1})"):
                        trans_res = model_text.generate_content(f"Translate to English image prompt: {img_desc}")
                        eng_prompt = trans_res.text
                        success_trans = True
                        break
                except Exception as e:
                    if "429" in str(e) or "ResourceExhausted" in str(e):
                        if i < 2:
                            time.sleep(5)
                        else:
                            st.error("❌ โควต้าวันนี้เต็มจริงๆ ค่ะ รบกวนรอสักพักใหญ่ๆ นะคะ")
                            st.stop()
            
            # ส่วนวาดรูป
            if success_trans and eng_prompt:
                st.info(f"✅ แปลสำเร็จ: {eng_prompt}")
                try:
                    with st.spinner("🎨 กำลังวาดรูปตามขนาดที่เลือก..."):
                        img_bytes = generate_image_with_retry(eng_prompt, w, h)
                        image = Image.open(io.BytesIO(img_bytes))
                        st.image(image, caption=f"ภาพขนาด {size_option} เสร็จแล้วค่ะ!", use_container_width=True)
                        
                        buf = io.BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button("📥 ดาวน์โหลดรูป", data=buf.getvalue(), file_name="ai_image.png")
                except Exception as e:
                    st.error(f"❌ ขออภัยค่ะ: {e}")

# --- ส่วนอื่นๆ ของแอปคงเดิม ---
elif menu == "🎬 วางแผนคอนเทนต์":
    st.header("🎬 วางแผนคอนเทนต์")
    # ... โค้ดส่วนอื่นๆ ...