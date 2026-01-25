import streamlit as st
import requests
import io
from PIL import Image
import urllib.parse
import random
import google.generativeai as genai

# --- 1. SETUP & SECRETS ---
st.set_page_config(page_title="Creator Hub v12.9", page_icon="🎨", layout="centered")

try:
    # ดึงกุญแจที่มีอยู่แล้วมาใช้เป็นล่ามแปลภาษาครับ
    genai.configure(api_key=st.secrets["GEMINI_KEYS"])
    model_gemini = genai.GenerativeModel('gemini-pro')
except:
    model_gemini = None

# --- 2. FUNCTION: ล่ามแปลไทย -> อังกฤษ ---
def translate_prompt(text):
    if not model_gemini: return text
    try:
        response = model_gemini.generate_content(f"Translate this Thai image prompt to English: {text}")
        return response.text
    except:
        return text

# --- 3. FUNCTION: ENGINE สร้างภาพ (v12.9: Anti-Ban) ---
def generate_image_v6(prompt_text, width, height, model_type):
    encoded_prompt = urllib.parse.quote(prompt_text)
    # สุ่มเลข Seed ทุกครั้งแบบมหาศาลเพื่อเลี่ยงการโดนจำ IP
    random_seed = random.randint(1, 999999999)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model={model_type}&nologo=true&seed={random_seed}"
    
    try:
        response = requests.get(url, timeout=45)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content)), "OK"
        elif response.status_code == 429:
            return None, "โดนจำกัดจำนวน (Rate Limit) รอ 1-2 นาทีนะครับ"
        else:
            return None, f"Error: {response.status_code}"
    except:
        return None, "การเชื่อมต่อขัดข้อง"

# --- 4. INTERFACE ---
st.title("🎨 AI เนรมิตภาพ (แปลไทยได้ + กันแบน)")

with st.expander("⚙️ ตั้งค่าขนาดและโหมด"):
    mode = st.radio("🚀 โหมด:", ["เน้นสวย (Flux)", "เน้นไว (Turbo)"], index=1) # ค่าเริ่มต้นเป็น Turbo เพื่อความไว
    target_size = st.selectbox("เลือกขนาด:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

# กำหนดขนาดมาตรฐาน
if "9:16" in target_size: w, h = 720, 1280
elif "16:9" in target_size: w, h = 1280, 720
else: w, h = 1024, 1024

user_prompt = st.text_area("อยากให้วาดอะไร (พิมพ์ไทยได้เลยครับ):", placeholder="เช่น แมวใส่ชุดอวกาศ")

if st.button("✨ เริ่มเนรมิตภาพ"):
    if user_prompt:
        with st.spinner("⏳ กำลังแปลภาษาและวาดภาพ..."):
            # ขั้นตอน 1: แปลภาษาก่อน
            eng_prompt = translate_prompt(user_prompt)
            st.caption(f"🔍 AI แปลเป็น: {eng_prompt}") # โชว์ให้ดูว่าแปลถูกไหม
            
            # ขั้นตอน 2: เจนภาพ
            m_key = "flux" if "Flux" in mode else "turbo"
            img, msg = generate_image_v6(eng_prompt, w, h, m_key)
            
            if img:
                st.image(img, width=450, caption="ผลงานของคุณเก่งครับ")
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("📥 ดาวน์โหลด", buf.getvalue(), "ai_art.png", "image/png")
            else:
                st.error(f"❌ {msg}")
                st.info("💡 ทริค: ถ้าโดน Rate Limit ลองเปลี่ยนคำสั่งนิดหน่อย หรือสลับไปใช้เน็ตมือถือจะหายทันทีครับ")
    else:
        st.warning("พิมพ์สิ่งที่ต้องการก่อนนะค่ะ")