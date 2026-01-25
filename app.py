import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re
import time

# --- 1. CONFIG ---
st.set_page_config(page_title="Creator Hub v14.0", page_icon="🚀", layout="centered")

# --- 2. ENGINE (ระบบทะลุลิมิต) ---
def get_magic_url(prompt, width, height, model):
    # เข้ารหัสคำสั่ง
    encoded = urllib.parse.quote(prompt)
    
    # เทคนิคที่ 1: สุ่ม Seed แบบมหาศาล (เพื่อหลอกว่าเป็นคนใหม่)
    seed = random.randint(1, 999999999)
    
    # เทคนิคที่ 2: เพิ่ม Cache Buster (ตัวเลขสุ่มท้าย URL)
    cache_buster = int(time.time() * 1000)
    
    # สร้าง URL แบบพิเศษ
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model={model}&nologo=true&seed={seed}&v={cache_buster}"
    return url

# --- 3. TRANSLATION (เหมือนเดิมแต่ตัดให้สั้น) ---
LOCAL_DICT = {
    "แมว": "cat", "หมา": "dog", "สวย": "beautiful", "รถ": "car", 
    "ผู้หญิง": "woman", "ผู้ชาย": "man", "หุ่นยนต์": "robot"
}

try:
    genai.configure(api_key=st.secrets["GEMINI_KEYS"])
    model_gemini = genai.GenerativeModel('gemini-1.5-flash')
    gemini_ready = True
except:
    gemini_ready = False

def smart_translate(text):
    for thai, eng in LOCAL_DICT.items():
        if thai in text: text = text.replace(thai, eng)
    
    if bool(re.search('[ก-ฮ]', text)) and gemini_ready:
        try:
            response = model_gemini.generate_content(f"English prompt for: {text}")
            return response.text.strip()
        except:
            return text
    return text

# --- 4. UI ---
st.title("🚀 AI ทะลุขีดจำกัด (v14.0)")
st.info("💡 ถ้าภาพไม่ขึ้น ให้กดปุ่มสร้างใหม่อีกครั้ง ระบบจะเปลี่ยนเส้นทางให้อัตโนมัติค่ะ")

with st.sidebar:
    st.header("⚙️ ตั้งค่า")
    model_choice = st.radio("โหมด:", ["turbo (ไวมาก)", "flux (สวยคม)"], index=0)
    size_choice = st.selectbox("ขนาด:", ["TikTok (9:16)", "YouTube (16:9)", "Square (1:1)"])

# ปุ่มช่วยเลือก
st.write("✨ **เมนูลัด (กดปุ๊บ ภาพมาปั๊บ):**")
c1, c2, c3 = st.columns(3)
with c1: 
    if st.button("🐱 แมวน่ารัก"): user_prompt = "cute fluffy cat, 8k"
    else: user_prompt = ""
with c2: 
    if st.button("🚀 ยานอวกาศ"): user_prompt = "futuristic spaceship, sci-fi"
with c3: 
    if st.button("💃 นางแบบ"): user_prompt = "beautiful fashion model, portrait"

# กล่องพิมพ์ (ถ้าไม่ได้กดปุ่ม)
if not user_prompt:
    user_prompt = st.text_input("หรือพิมพ์คำสั่ง:", placeholder="เช่น หมาใส่แว่น")

# คำนวณขนาด
if "9:16" in size_choice: w, h = 720, 1280
elif "16:9" in size_choice: w, h = 1280, 720
else: w, h = 1024, 1024

if st.button("⚡ สร้างภาพทันที") or user_prompt:
    if user_prompt:
        # แปลภาษา
        final_p = smart_translate(user_prompt)
        
        # ดึง URL แบบพิเศษ
        selected_model = model_choice.split(" ")[0]
        image_url = get_magic_url(final_p, w, h, selected_model)
        
        # แสดงผล
        st.write(f"🎨 กำลังวาด: **{final_p}**")
        st.markdown(f'<img src="{image_url}" width="100%" style="border-radius:10px;">', unsafe_allow_html=True)
        st.markdown(f'[📥 ดาวน์โหลดภาพ]({image_url})')