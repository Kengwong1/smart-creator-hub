import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re

# --- 1. SETUP ---
st.set_page_config(page_title="Creator Hub v13.3", page_icon="⚡", layout="centered")

try:
    genai.configure(api_key=st.secrets["GEMINI_KEYS"])
    model_gemini = genai.GenerativeModel('gemini-pro')
except:
    model_gemini = None

# --- 2. SPEED FUNCTIONS ---
def contains_thai(text):
    return bool(re.search('[ก-ฮ]', text))

def fast_translate(text):
    if not model_gemini or not contains_thai(text): return text
    try:
        # สั่งให้แปลแบบคำต่อคำเพื่อให้ไวที่สุด
        response = model_gemini.generate_content(f"Translate to English: {text}")
        return response.text.strip()
    except:
        return text

# --- 3. MAIN UI ---
st.title("⚡ AI วาดภาพความเร็วเทพ (v13.3)")

with st.sidebar:
    st.header("⚙️ ปรับความเร็ว")
    # แนะนำโหมด turbo สำหรับความไวสูงสุด
    model_choice = st.radio("โmoved:", ["turbo (ไวเทพ)", "flux (สวยละเอียด)"], index=0)
    selected_model = model_choice.split(" ")[0]
    size_choice = st.selectbox("สัดส่วน:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

# ล็อกขนาด
if "9:16" in size_choice: w, h = 720, 1280
elif "16:9" in size_choice: w, h = 1280, 720
else: w, h = 1024, 1024

user_input = st.text_input("ใส่ไอเดีย (พิมพ์อังกฤษจะไวกว่า 3 วินาที!):", placeholder="เช่น หมาเท่ๆ")

if st.button("🚀 เนรมิตภาพทันที"):
    if user_input:
        # 1. ขั้นตอนแปล (ถ้าเป็นไทย)
        final_p = fast_translate(user_input) if contains_thai(user_input) else user_input
        
        # 2. สร้าง URL
        seed = random.randint(1, 999999)
        encoded = urllib.parse.quote(final_p)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&model={selected_model}&nologo=true&seed={seed}"
        
        # 3. แสดงผลด้วย HTML (เร็วกว่า st.image ปกติ)
        st.markdown(f'<img src="{image_url}" width="100%" style="border-radius: 15px;">', unsafe_allow_html=True)
        
        # 4. ปุ่มเปิดดู/เซฟ
        st.write(f"🔍 AI วาดจากคำสั่ง: **{final_p}**")
        st.markdown(f'[📥 คลิกเพื่อเปิดดูภาพขนาดเต็มและบันทึกภาพ]({image_url})')
    else:
        st.warning("กรุณาใส่ไอเดียก่อนนะคะ")