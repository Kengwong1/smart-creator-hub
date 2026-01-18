import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator # ตัวแปลภาษาฟรี

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. ฟังก์ชันแปลภาษาแบบ 2 ระบบ (Gemini + Free Backup) ---
def translate_prompt(text):
    # ระบบ 1: ลองใช้ Gemini ก่อน (เพราะแปลสวยกว่า)
    keys = st.secrets.get("GEMINI_KEYS", [])
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(f"Translate to English image prompt: {text}")
            return res.text
        except:
            continue # ถ้าดอกแรกเต็ม ไปลองดอกถัดไป
            
    # ระบบ 2: ถ้า Gemini เต็มทุกลูก สลับมาใช้ Google Translate ฟรีทันที!
    try:
        translated = GoogleTranslator(source='th', target='en').translate(text)
        return translated + ", cinematic, highly detailed, 8k" # เติมคีย์เวิร์ดให้ภาพสวยขึ้น
    except:
        return text # ถ้าล้มหมดจริงๆ ส่งค่าเดิมไป

# --- 3. ฟังก์ชันเสกรูป (Pollinations AI) ---
def generate_image_url(prompt, width, height):
    encoded_prompt = urllib.parse.quote(prompt)
    seed = int(time.time())
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

# --- 4. Sidebar ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub")
    st.write(f"ยินดีต้อนรับค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["🎨 เสกรูปภาพด้วย AI", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา"])
    st.divider()
    st.caption("v3.4 | Multi-Translation System")

# --- 5. โซนการทำงาน ---
if menu == "🎨 เสกรูปภาพด้วย AI":
    st.header("🎨 AI ศิลปินเสกรูปภาพ (ระบบแปลภาษา 2 ชั้น)")
    
    img_desc = st.text_area("อยากให้ AI วาดภาพอะไร? (พิมพ์ไทยได้เลยค่ะ)", height=100)
    
    size_option = st.selectbox("เลือกขนาดภาพ:", ["แนวตั้ง (9:16) - TikTok/Reels", "แนวนอน (16:9) - FB/YouTube", "จัตุรัส (1:1) - IG/Profile"])
    
    if "9:16" in size_option: w, h = 540, 960
    elif "16:9" in size_option: w, h = 960, 540
    else: w, h = 768, 768

    if st.button("✨ เริ่มเสกรูป"):
        if not img_desc:
            st.warning("กรุณาใส่คำบรรยายภาพก่อนนะคะ")
        else:
            with st.spinner("⏳ กำลังเตรียมคำสั่งภาพ (ระบบกำลังเลือกตัวแปลที่ดีที่สุด)..."):
                # เช็คภาษาอังกฤษเบื้องต้น
                is_english = all(ord(c) < 128 for c in img_desc[:20])
                if is_english:
                    eng_prompt = img_desc
                else:
                    eng_prompt = translate_prompt(img_desc)
            
            if eng_prompt:
                with st.spinner("🎨 กำลังวาดภาพ..."):
                    final_url = generate_image_url(eng_prompt, w, h)
                    st.success("✨ เสร็จแล้วค่ะ!")
                    
                    # จัดหน้าจอรูปภาพ
                    html_code = f'<div style="display: flex; justify-content: center;"><img src="{final_url}" style="max-width: 100%; max-height: 75vh; border-radius: 12px; box-shadow: 0px 8px 20px rgba(0,0,0,0.3);"></div>'
                    
                    if "9:16" in size_option:
                        c1, c2, c3 = st.columns([1, 2, 1])
                        with c2: st.markdown(html_code, unsafe_allow_html=True)
                    else:
                        st.markdown(html_code, unsafe_allow_html=True)
                    
                    st.markdown(f'<div style="text-align: center; margin-top: 20px;"><a href="{final_url}" target="_blank" style="padding: 10px 20px; background-color: #FF4B4B; color: white; border-radius: 8px; text-decoration: none;">📥 ดาวน์โหลดภาพขนาดเต็ม</a></div>', unsafe_allow_html=True)