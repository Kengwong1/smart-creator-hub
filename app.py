import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re

# --- 1. SETUP ---
st.set_page_config(page_title="Creator Hub v13.2", page_icon="⚡", layout="centered")

try:
    genai.configure(api_key=st.secrets["GEMINI_KEYS"])
    model_gemini = genai.GenerativeModel('gemini-pro')
except:
    model_gemini = None

# --- 2. SMART FUNCTIONS ---
def contains_thai(text):
    return bool(re.search('[ก-ฮ]', text))

def fast_translate(text):
    if not model_gemini or not contains_thai(text): return text
    try:
        response = model_gemini.generate_content(f"Translate to English (one short phrase): {text}")
        return response.text.strip()
    except:
        return text

# --- 3. MAIN UI ---
st.title("⚡ AI วาดภาพความเร็วแสง (v13.2)")

with st.sidebar:
    st.header("⚙️ ปรับจูน")
    model_choice = st.radio("โหมด:", ["turbo (ไวที่สุด)", "flux (ละเอียด)"], index=0)
    selected_model = model_choice.split(" ")[0]
    size_choice = st.selectbox("สัดส่วน:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

# กำหนดขนาด
if "9:16" in size_choice: w, h = 720, 1280
elif "16:9" in size_choice: w, h = 1280, 720
else: w, h = 1024, 1024

user_input = st.text_input("ใส่ไอเดีย:", placeholder="เช่น หมาใส่หมวกเท่ๆ")

if st.button("🚀 เนรมิตภาพทันที"):
    if user_input:
        # ขั้นตอนแปล (ถ้าจำเป็น)
        final_p = fast_translate(user_input) if contains_thai(user_input) else user_input
        
        # สร้าง URL สำหรับภาพ
        seed = random.randint(1, 10**6)
        encoded = urllib.parse.quote(final_p)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&model={selected_model}&nologo=true&seed={seed}"
        
        # --- จุดเปลี่ยนสำคัญ (Speed Hack) ---
        # แสดงภาพด้วย URL โดยตรง (บราวเซอร์จะดึงเอง ไม่ผ่าน server ทำให้ไวมาก!)
        st.image(image_url, caption=f"Prompt: {final_p}", use_container_width=True)
        
        # ลิงก์ดาวน์โหลดแบบด่วน
        st.markdown(f'''
            <a href="{image_url}" target="_blank">
                <button style="width:100%; border-radius:10px; padding:10px; background-color:#ff4b4b; color:white; border:none; cursor:pointer;">
                    📥 เปิดภาพขนาดเต็ม / บันทึกภาพ
                </button>
            </a>
        ''', unsafe_allow_html=True)
    else:
        st.warning("กรุณาใส่ไอเดียก่อนนะคะ")