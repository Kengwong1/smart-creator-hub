import streamlit as st
import requests
import io
from PIL import Image
import urllib.parse
import random
import google.generativeai as genai

# --- 1. SETUP & UI CONFIG ---
st.set_page_config(page_title="Creator Hub v13.0", page_icon="⚡", layout="centered")

# ดึงกุญแจสำหรับล่ามแปลภาษา
try:
    genai.configure(api_key=st.secrets["GEMINI_KEYS"])
    model_gemini = genai.GenerativeModel('gemini-pro')
except:
    model_gemini = None

# --- 2. FAST FUNCTIONS ---
def fast_translate(text):
    if not model_gemini or not text: return text
    try:
        # สั่งให้แปลแบบสั้นที่สุดเพื่อประหยัดเวลา
        response = model_gemini.generate_content(f"Translate to English (short): {text}")
        return response.text.strip()
    except:
        return text

def quick_generate(prompt_text, width, height, model):
    encoded = urllib.parse.quote(prompt_text)
    seed = random.randint(1, 10**9)
    # ใช้ URL ตรงเข้า Engine เพื่อความเร็ว
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model={model}&nologo=true&seed={seed}"
    
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            return Image.open(io.BytesIO(r.content))
        return None
    except:
        return None

# --- 3. MAIN INTERFACE ---
st.title("⚡ AI วาดภาพด่วน (v13.0)")

with st.sidebar:
    st.header("⚙️ ตั้งค่าความเร็ว")
    # ตั้งค่าเริ่มต้นเป็น Turbo เพื่อความไวที่สุดค่ะ
    model_choice = st.radio("เลือกโหมด:", ["turbo (ไวมาก)", "flux (สวยแต่ช้า)"], index=0)
    selected_model = model_choice.split(" ")[0]
    
    size_choice = st.selectbox("ขนาดภาพ:", ["TikTok (9:16)", "YouTube (16:9)", "Square (1:1)"])

# กำหนดขนาด
if "9:16" in size_choice: w, h = 720, 1280
elif "16:9" in size_choice: w, h = 1280, 720
else: w, h = 1024, 1024

user_input = st.text_input("พิมพ์สิ่งที่ต้องการ (ไทย/อังกฤษ):", placeholder="เช่น แมวขี่มอเตอร์ไซค์")

if st.button("🚀 เนรมิตภาพทันที"):
    if user_input:
        # ขั้นตอนที่ 1: แปลแบบด่วน
        with st.status("🔍 กำลังประมวลผล...", expanded=True) as status:
            st.write("🛰️ กำลังแปลภาษา...")
            eng_p = fast_translate(user_input)
            
            st.write(f"🎨 กำลังวาด: {eng_p}...")
            img = quick_generate(eng_p, w, h, selected_model)
            
            if img:
                status.update(label="✅ เสร็จเรียบร้อย!", state="complete", expanded=False)
                st.image(img, width=400)
                
                # ปุ่มดาวน์โหลดด่วน
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("📥 โหลดภาพ", buf.getvalue(), "fast_ai.png", "image/png")
            else:
                status.update(label="❌ ขัดข้อง", state="error")
                st.error("ระบบไม่ตอบสนอง ลองกดใหม่อีกครั้งนะค่ะ")
    else:
        st.warning("ใส่ไอเดียก่อนนะค่ะ")