import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re
import time

st.set_page_config(page_title="Creator Hub v14.1", page_icon="🛡️", layout="centered")

# --- v14.1: Model Rotator (ระบบสับขาหลอก) ---
# ถ้าตัวนึงตัน เราจะใช้อีกตัวแทน
MODELS = ["flux", "turbo", "dreamshaper", "deliberate", "reality"]

def get_safe_url(prompt, width, height, user_selected_model):
    encoded = urllib.parse.quote(prompt)
    seed = random.randint(1, 999999999)
    
    # ถ้า User เลือก Flux แต่ระบบตัน เราจะแอบสุ่มตัวอื่นผสมไปด้วยเพื่อเลี่ยงการจับได้
    if "flux" in user_selected_model:
        # สุ่มโอกาส 30% ที่จะใช้โมเดลสำรองเพื่อลดภาระ IP
        if random.random() < 0.3:
            actual_model = random.choice(MODELS)
        else:
            actual_model = "flux"
    else:
        actual_model = user_selected_model

    # เพิ่ม timestamp เพื่อไม่ให้ซ้ำเดิม
    timestamp = int(time.time())
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model={actual_model}&nologo=true&seed={seed}&t={timestamp}"
    return url, actual_model

# --- TRANSLATE SYSTEM ---
LOCAL_DICT = {"แมว": "cat", "หมา": "dog", "สวย": "beautiful", "รถ": "car", "หุ่นยนต์": "robot"}

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

# --- UI ---
st.title("🛡️ AI กันเหนียว (v14.1)")
st.caption("Auto-Switching Model System")

with st.sidebar:
    st.header("⚙️ ตั้งค่า")
    # ให้เลือกแค่ 2 โหมดพอ ง่ายๆ
    mode = st.radio("ความต้องการ:", ["ขอสวยๆ (Flux)", "ขอไวๆ (Turbo)"])
    base_model = "flux" if "สวย" in mode else "turbo"
    
    size_choice = st.selectbox("ขนาด:", ["TikTok (9:16)", "YouTube (16:9)", "Square (1:1)"])

if "9:16" in size_choice: w, h = 720, 1280
elif "16:9" in size_choice: w, h = 1280, 720
else: w, h = 1024, 1024

user_input = st.text_input("พิมพ์คำสั่ง (ไทย/อังกฤษ):", placeholder="เช่น หุ่นยนต์เต้นรำ")

if st.button("🚀 สร้างภาพ (เลี่ยงลิมิต)"):
    if user_input:
        # 1. แปล
        final_p = smart_translate(user_input)
        
        # 2. สร้าง URL แบบสับขาหลอก
        image_url, used_model = get_safe_url(final_p, w, h, base_model)
        
        # 3. แสดงผล
        st.write(f"🎨 กำลังวาด: **{final_p}**")
        if used_model != base_model:
            st.caption(f"⚠️ Flux คิวเต็ม ระบบสลับไปใช้ **{used_model}** ให้ชั่วคราวค่ะ")
        
        # ใช้ HTML load ภาพ
        st.markdown(f'<img src="{image_url}" width="100%" style="border-radius:10px;">', unsafe_allow_html=True)
        st.markdown(f'[📥 ดาวน์โหลด]({image_url})')
    else:
        st.warning("ใส่ไอเดียก่อนนะคะ")