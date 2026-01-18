import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
import requests  # ตัวช่วยดึงข้อมูลรูปภาพ
from io import BytesIO
from deep_translator import GoogleTranslator

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v5.7", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. ชุดคีย์เวิร์ดมาตรฐาน ---
PRO_PHOTO_SUFFIX = ", professional photography, real human hands, smartphone repair tools, macro shot, highly detailed, 8k, sharp focus, authentic workshop, NO ROBOTS"

STYLE_PRESETS = {
    "สไตล์ปกติ (ช่างซ่อมสมจริง)": PRO_PHOTO_SUFFIX,
    "ภาพถ่ายระดับโปร (Macro)": ", high-detail macro shot, internal phone hardware, realistic textures, cinematic lighting, NO ROBOTS",
    "ฉากหลังสินค้า Affiliate": ", high-end product photography, smartphone on minimalist desk, soft light, bokeh, 8k",
    "ไทยโมเดิร์น": ", Thai local repair shop atmosphere, realistic, 8k"
}

# --- 3. ระบบ AI และการแปลภาษา ---
def translate_to_pro_prompt(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    instruction = "Convert this topic into a professional photography prompt for a YouTube thumbnail. Focus on REAL HUMAN HANDS and REPAIR TOOLS. No sci-fi, no robots. Topic: "
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(instruction + text)
            return res.text
        except: continue
    return GoogleTranslator(source='th', target='en').translate(text) + PRO_PHOTO_SUFFIX

def generate_thai_content(prompt_text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(f"{prompt_text} (โปรดตอบเป็นภาษาไทยอย่างละเอียด)")
            return res.text
        except: continue
    return "QUOTA_FULL"

# --- 4. ฟังก์ชันดึงรูปภาพจาก Backend (หัวใจสำคัญของ v5.7) ---
def fetch_image_bytes(url):
    try:
        # ให้เวลารอรูปภาพสูงสุด 60 วินาที
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"Error fetching image: {e}")
    return None

# --- 5. Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v5.7")
    menu = st.radio("เลือกเครื่องมือ:", ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา"])
    st.divider()
    st.caption("v5.7 | Backend Image Fetcher")

# --- 6. โซนการทำงาน ---

if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package")
    topic = st.text_input("คุณอยากทำคอนเทนต์เรื่องอะไร?", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: chosen_style = st.selectbox("เลือกสไตล์ภาพหน้าปก:", list(STYLE_PRESETS.keys()))
    with col_s2: chosen_size = st.selectbox("ขนาดภาพที่ต้องการ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("กรุณาใส่หัวข้อคอนเทนต์ค่ะ")
        else:
            with st.spinner("⏳ กำลังใช้ระบบ AI ผลิตเนื้อหาและเสกรูปภาพ (โปรดรอสักครู่)..."):
                # 1. คิดเนื้อหา
                text_res = generate_thai_content(f"ทำคอนเทนต์เรื่อง '{topic}': 1.ชื่อคลิป Viral 5 แบบ, 2.แคปชั่นป้ายยา Affiliate, 3.สคริปต์การถ่ายทำ")
                
                if text_res == "QUOTA_FULL":
                    st.error("⚠️ โควต้า Gemini เต็มค่ะ รบกวนรอ 1 นาทีนะคะ")
                else:
                    # 2. เสกรูปภาพและดึงข้อมูลมาที่เครื่อง
                    eng_p = translate_to_pro_prompt(topic)
                    w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                    full_prompt = urllib.parse.quote(eng_p + STYLE_PRESETS[chosen_style])
                    final_url = f"https://image.pollinations.ai/prompt/{full_prompt}?width={w}&height={h}&seed={int(time.time())}&nologo=true&model=flux"
                    
                    # ดึงรูปภาพมาเป็น Bytes
                    image_bytes = fetch_image_bytes(final_url)
                    
                    st.divider()
                    st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                    
                    if image_bytes:
                        if "9:16" in chosen_size:
                            c1, c2, c3 = st.columns([1, 1.2, 1])
                            with c2: st.image(image_bytes, use_container_width=True)
                        else:
                            st.image(image_bytes, use_container_width=True)
                    else:
                        st.error("❌ ไม่สามารถดึงรูปภาพจากเซิร์ฟเวอร์ได้ในขณะนี้ โปรดลองกดปุ่มใหม่อีกครั้งค่ะ")
                    
                    st.markdown(f'### [📥 ดาวน์โหลดภาพหน้าปก]({final_url})')
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)

# (สำหรับหมวดเสกรูปอย่างเดียว ให้ปรับใช้ fetch_image_bytes เช่นกันค่ะ)
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    img_desc = st.text_area("อยากได้รูปอะไรคะ?")
    if st.button("✨ เริ่มวาดรูป"):
        with st.spinner("🎨 กำลังวาดรูปคุณภาพสูง..."):
            eng_p = translate_to_pro_prompt(img_desc)
            final_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(eng_p)}?width=768&height=768&seed={int(time.time())}&nologo=true&model=flux"
            image_bytes = fetch_image_bytes(final_url)
            if image_bytes:
                st.image(image_bytes, use_container_width=True)
            else:
                st.error("รูปภาพโหลดไม่สำเร็จค่ะ")
            st.markdown(f'[📥 ดาวน์โหลดรูปภาพ]({final_url})')