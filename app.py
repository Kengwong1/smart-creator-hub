import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re

# --- 1. CONFIG ---
st.set_page_config(page_title="Creator Hub v13.8", page_icon="⚡", layout="centered")

# --- 2. FAST TRANSLATE SYSTEM ---
# 2.1 พจนานุกรมในตัว (แปลทันทีไม่ต้องรอเน็ต)
LOCAL_DICT = {
    "แมว": "cat", "หมา": "dog", "สุนัข": "dog", "นก": "bird", 
    "รถ": "car", "รถสปอร์ต": "sports car", "ผู้หญิง": "beautiful woman",
    "ผู้ชาย": "handsome man", "หุ่นยนต์": "robot", "อวกาศ": "space",
    "สวย": "beautiful", "น่ารัก": "cute", "เท่": "cool", 
    "cyberpunk": "cyberpunk style", "อนิเมะ": "anime style"
}

# 2.2 ระบบ Gemini Flash (ไวกว่าตัวเก่า 10 เท่า)
try:
    genai.configure(api_key=st.secrets["GEMINI_KEYS"])
    # เปลี่ยนเป็นรุ่น Flash เพื่อความไว
    model_gemini = genai.GenerativeModel('gemini-1.5-flash')
    gemini_ready = True
except:
    model_gemini = None
    gemini_ready = False

def smart_translate(text):
    # 1. เช็กในพจนานุกรมก่อน (ไวสุด 0.01 วิ)
    for thai, eng in LOCAL_DICT.items():
        if thai in text:
            # ถ้าเจอคำศัพท์ที่รู้จัก ให้แทนที่เลย
            text = text.replace(thai, eng)
    
    # 2. ถ้ายังเหลือภาษาไทย ค่อยถาม Gemini Flash
    if bool(re.search('[ก-ฮ]', text)) and gemini_ready:
        try:
            response = model_gemini.generate_content(f"Change to English prompt: {text}")
            return response.text.strip()
        except:
            return text # ถ้าถามไม่ได้ ก็ส่งไปทั้งอย่างนั้น
    return text

# --- 3. MAIN UI ---
st.title("🎨 AI สร้างภาพ (v13.8: แปลไว+มีปุ่มช่วย)")

with st.sidebar:
    st.header("⚙️ ตั้งค่า")
    model_choice = st.radio("โหมด:", ["turbo (ไว)", "flux (สวย)"], index=0)
    size_choice = st.selectbox("สัดส่วน:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

# --- ส่วนปุ่มช่วยจิ้ม (ไม่ต้องพิมพ์เอง) ---
st.write("✨ **จิ้มปุ่มเพื่อเพิ่มคำศัพท์ (ไม่ต้องพิมพ์เอง):**")
col1, col2, col3, col4 = st.columns(4)
prompt_parts = []

with col1: 
    if st.button("🐱 แมว"): prompt_parts.append("cute cat")
    if st.button("👩 หญิงสวย"): prompt_parts.append("beautiful woman")
with col2: 
    if st.button("🐶 หมา"): prompt_parts.append("cute dog")
    if st.button("🤖 หุ่นยนต์"): prompt_parts.append("futuristic robot")
with col3: 
    if st.button("🚗 รถหรู"): prompt_parts.append("luxury supercar")
    if st.button("🏰 ปราสาท"): prompt_parts.append("fantasy castle")
with col4: 
    if st.button("🚀 อวกาศ"): prompt_parts.append("galaxy space background")
    if st.button("🏙️ เมือง"): prompt_parts.append("cyberpunk city")

# กล่องข้อความ
user_input = st.text_input("หรือพิมพ์เอง (ไทย/อังกฤษ):", placeholder="เช่น แมวขี่มอเตอร์ไซค์")

# ล็อกขนาด
if "9:16" in size_choice: w, h = 720, 1280
elif "16:9" in size_choice: w, h = 1280, 720
else: w, h = 1024, 1024

if st.button("🚀 เนรมิตภาพ"):
    # รวมคำจากปุ่ม + คำที่พิมพ์
    full_prompt = " ".join(prompt_parts) + " " + user_input
    
    if full_prompt.strip():
        # แสดงสถานะแบบไม่บล็อกหน้าจอ
        status_text = st.empty()
        status_text.caption("⚡ กำลังประมวลผลคำสั่ง...")
        
        # แปลภาษา (ใช้ระบบใหม่ v13.8)
        final_p = smart_translate(full_prompt)
        status_text.caption(f"🎨 กำลังวาด: {final_p}")
        
        # สร้าง URL
        seed = random.randint(1, 10**6)
        encoded = urllib.parse.quote(final_p)
        selected_model = model_choice.split(" ")[0]
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&model={selected_model}&nologo=true&seed={seed}"
        
        # แสดงผลทันที
        st.markdown(f'<img src="{image_url}" width="100%" style="border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
        st.markdown(f'[📥 ดาวน์โหลดภาพ]({image_url})')
        status_text.empty() # ลบข้อความสถานะออกเมื่อเสร็จ
        
    else:
        st.warning("จิ้มปุ่มข้างบน หรือพิมพ์ไอเดียก่อนนะครับ")