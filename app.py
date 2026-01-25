import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re

# --- 1. SETUP ---
st.set_page_config(page_title="Creator Hub v13.4", page_icon="🎨", layout="centered")

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
    # สั่งให้ Gemini แปลและเติมแต่งให้สวยตามสไตล์ที่เลือก
    style_context = f"in {style} style, highly detailed, professional lighting"
    prompt = f"Transform this image prompt into a descriptive English version: '{text}'. Add artistic keywords for {style_context}. (Response only English)"
    try:
        response = model_gemini.generate_content(prompt)
        return response.text.strip()
    except:
        return text

# --- 3. MAIN UI ---
st.title("🎨 AI เนรมิตภาพฉลาดเลือก (v13.4)")

with st.sidebar:
    st.header("⚙️ ตั้งค่า")
    model_choice = st.radio("โหมด:", ["turbo (ไว)", "flux (สวย)"], index=0)
    size_choice = st.selectbox("สัดส่วน:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    st.divider()
    st.caption("v13.4: แก้ปัญหาไทยไม่สวยและช้า")

# ส่วนเลือกสไตล์ด่วน (ช่วยให้ภาพสวยขึ้นโดยไม่ต้องพิมพ์เยอะ)
st.write("✨ **เลือกสไตล์ที่ชอบ:**")
style_col = st.columns(3)
with style_col[0]: style_photo = st.button("📸 ภาพถ่ายจริง")
with style_col[1]: style_anime = st.button("🏮 อนิเมะ")
with style_col[2]: style_art = st.button("🎨 งานศิลปะ")

# กำหนดสไตล์หลัก
current_style = "Cinematic Realistic"
if style_photo: current_style = "Hyper-realistic Photography"
elif style_anime: current_style = "Detailed Japanese Anime"
elif style_art: current_style = "Oil Painting Digital Art"

user_input = st.text_input("พิมพ์คำสั่ง (ไทย/อังกฤษ):", placeholder="เช่น หมาใส่แว่น")

# กำหนดขนาด
if "9:16" in size_choice: w, h = 720, 1280
elif "16:9" in size_choice: w, h = 1280, 720
else: w, h = 1024, 1024

if st.button("🚀 เริ่มเนรมิตภาพ"):
    if user_input:
        # 1. แปลและแต่งประโยคให้สวย (Expand)
        with st.spinner("🪄 กำลังแต่งประโยคให้สวยแบบโปร..."):
            final_p = expand_prompt(user_input, current_style)
        
        # 2. สร้าง URL
        seed = random.randint(1, 999999)
        encoded = urllib.parse.quote(final_p)
        selected_model = model_choice.split(" ")[0]
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&model={selected_model}&nologo=true&seed={seed}"
        
        # 3. แสดงผล (Fast Load)
        st.write(f"🔍 **AI กำลังวาดสไตล์ {current_style}:**")
        st.markdown(f'<img src="{image_url}" width="100%" style="border-radius: 15px;">', unsafe_allow_html=True)
        st.caption(f"English Prompt: {final_p}")
        st.markdown(f'[📥 ดาวน์โหลดภาพขนาดเต็ม]({image_url})')
    else:
        st.warning("ใส่ไอเดียก่อนนะค่ะ")