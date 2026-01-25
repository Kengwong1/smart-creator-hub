import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re

# --- 1. SETUP ---
st.set_page_config(page_title="Creator Hub v13.7", page_icon="⚡", layout="centered")

# เตรียมระบบแปล (แต่รอบนี้เราจะไม่พึ่งมัน 100%)
try:
    genai.configure(api_key=st.secrets["GEMINI_KEYS"])
    model_gemini = genai.GenerativeModel('gemini-pro')
    gemini_ready = True
except:
    model_gemini = None
    gemini_ready = False

# --- 2. SMART FUNCTIONS ---
def contains_thai(text):
    return bool(re.search('[ก-ฮ]', text))

def safe_translate(text, style):
    # ถ้า Gemini ไม่พร้อม หรือ user ปิดการใช้งาน ให้ส่งคืนค่าเดิมทันที (ไม่รอ)
    if not gemini_ready: return text
    
    try:
        # สั่งแปลแบบด่วน
        prompt = f"Translate this to English prompt for image generation: '{text}'. Style: {style}. Keep it short."
        response = model_gemini.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # ถ้า Error ให้คืนค่าเดิมทันที (อย่าหมุนค้าง)
        return text

# --- 3. MAIN UI ---
st.title("🎨 AI สร้างภาพ (v13.7: แก้หมุนค้าง)")

with st.sidebar:
    st.header("⚙️ ตั้งค่า")
    # ปุ่มวิเศษ! ถ้าหมุนนาน ให้ติ๊กออกเลยค่ะ
    enable_translation = st.checkbox("เปิดล่ามแปลภาษา (Gemini)", value=True, help="ถ้าหมุนนานให้ปิดตัวนี้ แล้วพิมพ์อังกฤษเอง")
    
    model_choice = st.radio("โหมด:", ["turbo (ไว)", "flux (สวย)"], index=0)
    size_choice = st.selectbox("สัดส่วน:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

# เลือกสไตล์
st.subheader("✨ สไตล์ภาพ:")
c1, c2, c3 = st.columns(3)
if 'style' not in st.session_state: st.session_state.style = "Realistic"

with c1: 
    if st.button("📸 จริง"): st.session_state.style = "Hyper-realistic"
with c2: 
    if st.button("🏮 อนิเมะ"): st.session_state.style = "Anime"
with c3: 
    if st.button("🎨 ศิลปะ"): st.session_state.style = "Digital Art"

st.caption(f"กำลังใช้สไตล์: {st.session_state.style}")

user_input = st.text_input("พิมพ์คำสั่ง (ถ้าปิดล่าม ต้องพิมพ์อังกฤษนะ):", placeholder="เช่น cat, dog, beautiful girl")

# ล็อกขนาด
if "9:16" in size_choice: w, h = 720, 1280
elif "16:9" in size_choice: w, h = 1280, 720
else: w, h = 1024, 1024

if st.button("🚀 เนรมิตภาพ"):
    if user_input:
        final_p = user_input
        
        # 1. ระบบแปลภาษา (ทำงานเมื่อ User เปิดปุ่ม และมีภาษาไทย)
        if enable_translation and contains_thai(user_input):
            with st.status("🛰️ กำลังแปลภาษา...", expanded=True) as status:
                try:
                    translated = safe_translate(user_input, st.session_state.style)
                    if translated != user_input:
                        final_p = translated
                        status.update(label="✅ แปลเสร็จแล้ว!", state="complete")
                    else:
                        status.update(label="⚠️ แปลไม่ได้ ใช้ข้อความเดิม", state="error")
                except:
                    final_p = user_input
                    status.update(label="❌ ข้ามการแปล (ระบบขัดข้อง)", state="error")
        
        # 2. สร้างภาพทันที (ไม่รออะไรทั้งนั้น)
        st.write(f"🎨 กำลังวาด: **{final_p}**")
        
        seed = random.randint(1, 10**6)
        encoded = urllib.parse.quote(final_p)
        selected_model = model_choice.split(" ")[0]
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&model={selected_model}&nologo=true&seed={seed}"
        
        # HTML Injection เพื่อความไวสูงสุด
        st.markdown(f'<img src="{image_url}" width="100%" style="border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
        st.markdown(f'[📥 ดาวน์โหลดภาพ]({image_url})')
        
    else:
        st.warning("ใส่ไอเดียก่อนนะคะ")