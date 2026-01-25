import streamlit as st
import requests
import io
from PIL import Image
import urllib.parse
import random
import google.generativeai as genai
import re

# --- 1. SETUP & UI CONFIG ---
st.set_page_config(page_title="Creator Hub v13.1", page_icon="⚡", layout="centered")

# เตรียมระบบแปลภาษา (ใช้กรณีพิมพ์ไทยเท่านั้น)
try:
    genai.configure(api_key=st.secrets["GEMINI_KEYS"])
    model_gemini = genai.GenerativeModel('gemini-pro')
except:
    model_gemini = None

# --- 2. SPEED OPTIMIZED FUNCTIONS ---
def contains_thai(text):
    return bool(re.search('[ก-ฮ]', text))

def ultra_fast_translate(text):
    if not model_gemini or not contains_thai(text): return text
    try:
        # สั่งให้แปลแบบกระชับที่สุด
        response = model_gemini.generate_content(f"Short English prompt for: {text}")
        return response.text.strip()
    except:
        return text

def instant_generate(prompt_text, width, height, model):
    encoded = urllib.parse.quote(prompt_text)
    seed = random.randint(1, 10**6)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model={model}&nologo=true&seed={seed}"
    
    try:
        # ปรับ timeout ให้สั้นลงเพื่อความไว
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            return Image.open(io.BytesIO(r.content))
        return None
    except:
        return None

# --- 3. MAIN INTERFACE ---
st.title("⚡ AI วาดภาพความเร็วสูง (v13.1)")

with st.sidebar:
    st.header("⚙️ ความเร็ว & ขนาด")
    model_choice = st.radio("เลือกโหมด:", ["turbo (ไวที่สุด)", "flux (ละเอียด)"], index=0)
    selected_model = model_choice.split(" ")[0]
    size_choice = st.selectbox("สัดส่วนภาพ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

# ล็อกขนาดมาตรฐาน
if "9:16" in size_choice: w, h = 720, 1280
elif "16:9" in size_choice: w, h = 1280, 720
else: w, h = 1024, 1024

user_input = st.text_input("ใส่ไอเดีย (พิมพ์อังกฤษจะไวขึ้น 2 เท่า!):", placeholder="เช่น cat ninja")

if st.button("🚀 เนรมิตภาพทันที"):
    if user_input:
        with st.status("🚀 กำลังทำงาน...", expanded=True) as status:
            # ตรวจสอบว่าต้องแปลไหม (ถ้าเป็นอังกฤษอยู่แล้วจะข้ามทันที)
            if contains_thai(user_input):
                st.write("🛰️ กำลังแปลภาษาไทย...")
                final_p = ultra_fast_translate(user_input)
            else:
                final_p = user_input
            
            st.write(f"🎨 กำลังวาด: {final_p}...")
            img = instant_generate(final_p, w, h, selected_model)
            
            if img:
                status.update(label="✅ สำเร็จ!", state="complete", expanded=False)
                st.image(img, width=400)
                
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("📥 โหลดภาพ", buf.getvalue(), "fast_ai.png", "image/png")
            else:
                status.update(label="❌ ขัดข้อง", state="error")
                st.error("Server หนาแน่นชั่วคราว ลองกดอีกครั้งนะค่ะ")
    else:
        st.warning("กรุณาใส่ไอเดียก่อนนะค่ะ")