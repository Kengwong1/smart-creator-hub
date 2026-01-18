import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v4.2", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. เครื่องปรุงรสพิเศษ (Secret Sauce) ---
# เราจะแอบใส่คำเหล่านี้ต่อท้ายทุกครั้งเพื่อให้ภาพสวยระดับ 8K ค่ะ
MAGIC_SAUCE = ", cinematic lighting, hyper-realistic, highly detailed, 8k, masterpiece, sharp focus, professional photography"

# --- 3. ฟังก์ชัน AI แปลภาษา (ระบบอมตะ) ---
def translate_immortal(text):
    # แผน A: ลองใช้ Gemini ก่อน
    keys = st.secrets.get("GEMINI_KEYS", [])
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(f"Translate to English image prompt: {text}")
            return res.text
        except:
            continue
            
    # แผน B: ถ้า Gemini เต็ม สลับมาใช้ตัวแปลฟรี + ใส่เครื่องปรุงพิเศษทันที
    try:
        translated = GoogleTranslator(source='th', target='en').translate(text)
        return translated + MAGIC_SAUCE
    except:
        return text + MAGIC_SAUCE

# --- 4. ฟังก์ชันสร้าง URL รูปภาพ (Pollinations AI) ---
def get_img_url(prompt, width, height):
    encoded = urllib.parse.quote(prompt)
    seed = int(time.time())
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

# --- 5. Sidebar ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v4.2")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["🎨 เสกรูปภาพด่วน", "🎬 วางแผนคอนเทนต์", "💰 แคปชั่นป้ายยา"])
    st.divider()
    st.caption("v4.2 | Super Backup System")

# --- 6. โซนการทำงาน ---

if menu == "🎨 เสกรูปภาพด่วน":
    st.header("🎨 AI ศิลปินระบบอมตะ (แปลไทยได้ตลอดกาล)")
    img_input = st.text_area("อยากให้ AI วาดภาพอะไร? (พิมพ์ไทยได้เลยนะคะ)", placeholder="เช่น หุ่นยนต์ซ่อมมือถือสีทอง")
    
    size = st.selectbox("เลือกขนาด:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    if "9:16" in size: w, h = 540, 960
    elif "16:9" in size: w, h = 960, 540
    else: w, h = 768, 768

    if st.button("✨ เริ่มเสกรูป"):
        if not img_input:
            st.warning("ใส่คำบรรยายก่อนนะคะ")
        else:
            with st.spinner("⏳ ระบบกำลังเตรียมคำสั่งภาพให้สวยที่สุด..."):
                # ตรวจสอบว่าเป็นอังกฤษอยู่แล้วหรือไม่
                is_english = all(ord(c) < 128 for c in img_input[:20])
                if is_english:
                    final_prompt = img_input + MAGIC_SAUCE
                else:
                    final_prompt = translate_immortal(img_input)
            
            with st.spinner("🎨 กำลังวาดรูป..."):
                img_url = get_img_url(final_prompt, w, h)
                
                # แสดงผลแบบจัดวางตรงกลางสวยๆ
                st.success("✨ เสร็จเรียบร้อยค่ะ!")
                html_img = f'<div style="display:flex; justify-content:center;"><img src="{img_url}" style="max-width:100%; max-height:75vh; border-radius:15px; box-shadow: 0px 8px 30px rgba(0,0,0,0.3);"></div>'
                
                if "9:16" in size:
                    c1, c2, c3 = st.columns([1, 2, 1])
                    with c2: st.markdown(html_img, unsafe_allow_html=True)
                else:
                    st.markdown(html_img, unsafe_allow_html=True)
                
                st.markdown(f'<div style="text-align:center; margin-top:20px;"><a href="{img_url}" target="_blank" style="padding:12px 24px; background-color:#FF4B4B; color:white; border-radius:8px; text-decoration:none; font-weight:bold;">📥 ดาวน์โหลดภาพขนาดเต็ม</a></div>', unsafe_allow_html=True)

elif menu == "🎬 วางแผนคอนเทนต์":
    # เมนูนี้ยังต้องใช้ Gemini เพื่อความฉลาดในการคิดเนื้อหาไทยค่ะ
    topic = st.text_input("หัวข้อคอนเทนต์")
    if st.button("✨ วางแผน"):
        with st.spinner("กำลังคิด..."):
            keys = st.secrets.get("GEMINI_KEYS", [])
            success = False
            for key in keys:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-flash-latest')
                    res = model.generate_content(f"วางแผนคอนเทนต์เรื่อง {topic} เป็นภาษาไทย")
                    st.markdown(res.text)
                    success = True
                    break
                except: continue
            if not success: st.error("โควต้าเต็ม รบกวนรอ 1 นาทีนะคะ")