import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re

# --- 1. SETUP ---
st.set_page_config(page_title="Creator Hub v13.5", page_icon="🎨", layout="centered")

# --- ระบบจำสถานะ (Session State) ---
# เพื่อให้แอปจำได้ว่าคุณเก่งเลือกสไตล์ไหนไว้ค่ะ
if 'selected_style' not in st.session_state:
    st.session_state.selected_style = "Cinematic Realistic"

try:
    genai.configure(api_key=st.secrets["GEMINI_KEYS"])
    model_gemini = genai.GenerativeModel('gemini-pro')
except:
    model_gemini = None

# --- 2. SMART ENGINE ---
def contains_thai(text):
    return bool(re.search('[ก-ฮ]', text))

def expand_prompt(text, style):
    if not model_gemini: return text
    # สั่งให้ Gemini แปลและแต่งประโยคตามสไตล์ที่เลือกไว้ใน session_state ค่ะ
    prompt = f"Transform this image prompt into a descriptive English version: '{text}'. Style: {style}. Focus on high quality. (Response only English)"
    try:
        response = model_gemini.generate_content(prompt)
        return response.text.strip()
    except:
        return text

# --- 3. MAIN UI ---
st.title("🎨 AI เนรมิตภาพ (v13.5: Fix Style Buttons)")

with st.sidebar:
    st.header("⚙️ ตั้งค่า")
    model_choice = st.radio("โหมด:", ["turbo (ไว)", "flux (สวย)"], index=0)
    size_choice = st.selectbox("สัดส่วน:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

# ส่วนเลือกสไตล์ด่วน (ใช้การคลิกเพื่อเปลี่ยนค่าใน session_state ค่ะ)
st.write(f"✨ **สไตล์ที่เลือกอยู่:** `{st.session_state.selected_style}`")
style_col = st.columns(3)
with style_col[0]:
    if st.button("📸 ภาพถ่ายจริง"): st.session_state.selected_style = "Hyper-realistic Photography"
with style_col[1]:
    if st.button("🏮 อนิเมะ"): st.session_state.selected_style = "Detailed Japanese Anime"
with style_col[2]:
    if st.button("🎨 งานศิลปะ"): st.session_state.selected_style = "Oil Painting Digital Art"

user_input = st.text_input("พิมพ์คำสั่ง (ไทย/อังกฤษ):", placeholder="เช่น แมวขี่มอเตอร์ไซค์")

# กำหนดขนาด
if "9:16" in size_choice: w, h = 720, 1280
elif "16:9" in size_choice: w, h = 1280, 720
else: w, h = 1024, 1024

if st.button("🚀 เริ่มเนรมิตภาพ"):
    if user_input:
        # ใช้ st.status เพื่อให้คุณเก่งเห็นว่าระบบกำลังทำอะไร ไม่ค้างแน่นอนค่ะ
        with st.status("🪄 กำลังประมวลผล...", expanded=True) as status:
            st.write(f"🛰️ กำลังแปลเป็นสไตล์ {st.session_state.selected_style}...")
            final_p = expand_prompt(user_input, st.session_state.selected_style)
            
            st.write("🎨 กำลังวาดภาพ...")
            seed = random.randint(1, 999999)
            encoded = urllib.parse.quote(final_p)
            selected_model = model_choice.split(" ")[0]
            image_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&model={selected_model}&nologo=true&seed={seed}"
            
            st.markdown(f'<img src="{image_url}" width="100%" style="border-radius: 15px;">', unsafe_allow_html=True)
            st.caption(f"English Prompt: {final_p}")
            st.markdown(f'[📥 ดาวน์โหลดภาพขนาดเต็ม]({image_url})')
            status.update(label="✅ วาดเสร็จแล้วค่ะ!", state="complete")
    else:
        st.warning("ใส่ไอเดียก่อนนะค่ะ")