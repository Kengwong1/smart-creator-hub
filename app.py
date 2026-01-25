import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re

# --- 1. SETUP ---
st.set_page_config(page_title="Creator Hub v13.6", page_icon="🎨", layout="centered")

# ระบบจำสถานะ (Session State)
if 'selected_style' not in st.session_state:
    st.session_state.selected_style = "Cinematic Realistic"

try:
    # เช็กกุญแจ Gemini
    genai.configure(api_key=st.secrets["GEMINI_KEYS"])
    model_gemini = genai.GenerativeModel('gemini-pro')
except Exception as e:
    model_gemini = None
    st.error(f"⚠️ ระบบแปลภาษาขัดข้อง: {e}")

# --- 2. FAST ENGINE ---
def contains_thai(text):
    return bool(re.search('[ก-ฮ]', text))

def expand_prompt(text, style):
    if not model_gemini: return text
    # ปรับคำสั่งให้ Gemini ตอบไวที่สุด (Short & Sharp)
    prompt = f"English image prompt for: {text}. Style: {style}. 10 words max."
    try:
        response = model_gemini.generate_content(prompt)
        return response.text.strip()
    except:
        return text

# --- 3. MAIN UI ---
st.title("🎨 AI เนรมิตภาพ (v13.6: No More Lag)")

with st.sidebar:
    st.header("⚙️ ตั้งค่า")
    model_choice = st.radio("โหมด:", ["turbo (ไว)", "flux (สวย)"], index=0)
    size_choice = st.selectbox("สัดส่วน:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    st.divider()
    if st.button("🔄 รีเซ็ตแอป"): st.rerun()

# ส่วนเลือกสไตล์ด่วน (แสดงผลชัดเจนว่าเลือกอะไรอยู่)
st.subheader(f"✨ สไตล์ปัจจุบัน: {st.session_state.selected_style}")
style_col = st.columns(3)
with style_col[0]:
    if st.button("📸 Realistic"): st.session_state.selected_style = "Hyper-realistic Photography"
with style_col[1]:
    if st.button("🏮 Anime"): st.session_state.selected_style = "Detailed Japanese Anime"
with style_col[2]:
    if st.button("🎨 Digital Art"): st.session_state.selected_style = "Oil Painting Digital Art"

user_input = st.text_input("พิมพ์สิ่งที่ต้องการ:", placeholder="เช่น แมวขี่มอเตอร์ไซค์")

# ล็อกขนาด
if "9:16" in size_choice: w, h = 720, 1280
elif "16:9" in size_choice: w, h = 1280, 720
else: w, h = 1024, 1024

if st.button("🚀 เนรมิตภาพ"):
    if user_input:
        # ใช้ placeholder เพื่อล้างภาพเก่าออกก่อน จะได้ไม่สับสนว่าค้างไหมค่ะ
        image_placeholder = st.empty()
        
        with st.status("🚀 กำลังทำงาน...", expanded=True) as status:
            # ขั้นตอน 1: แปล
            st.write("🛰️ กำลังแปลภาษา (Gemini thinking...)")
            final_p = expand_prompt(user_input, st.session_state.selected_style)
            
            # ขั้นตอน 2: เจนภาพ
            st.write(f"🎨 กำลังวาด: {final_p}")
            seed = random.randint(1, 10**6)
            encoded = urllib.parse.quote(final_p)
            selected_model = model_choice.split(" ")[0]
            image_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&model={selected_model}&nologo=true&seed={seed}"
            
            # แสดงผล
            image_placeholder.markdown(f'<img src="{image_url}" width="100%" style="border-radius: 15px; border: 2px solid #ff4b4b;">', unsafe_allow_html=True)
            
            status.update(label="✅ วาดเสร็จแล้วค่ะ!", state="complete", expanded=False)
            st.caption(f"Prompt ที่ใช้: {final_p}")
            st.markdown(f'[📥 ดาวน์โหลดภาพขนาดเต็ม]({image_url})')
    else:
        st.warning("กรุณาใส่ไอเดียก่อนนะคะ")