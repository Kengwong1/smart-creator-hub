import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
import requests
from io import BytesIO
from PIL import Image
from deep_translator import GoogleTranslator

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v4.9", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. สไตล์ภาพ (Visual Presets) ---
STYLE_PRESETS = {
    "สไตล์ปกติ (สมจริงพื้นฐาน)": ", professional photography, human hands repairing smartphone, macro shot, tools, 8k, sharp focus, no cartoon",
    "ช่างซ่อมยุคอวกาศ (Cyber Repair)": ", cyberpunk style, neon lights, intricate mechanical parts, 8k cinematic",
    "ฉากหลังสินค้า Affiliate (Studio)": ", high-end product photo, studio lighting, marble surface, blurred background",
    "ภาพถ่ายระดับโปร (DSLR)": ", shot on 85mm lens, f/1.8, cinematic lighting, ultra-realistic texture"
}

# --- 3. ระบบ AI และแปลภาษา ---
def translate_visual(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    prompt = f"Convert this to a professional photography prompt: {text}. Focus on human hands and real tools. Realistic style."
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(prompt)
            return res.text
        except: continue
    try:
        return GoogleTranslator(source='th', target='en').translate(text) + ", professional photography, detailed hands"
    except: return text

def generate_thai_content(prompt_text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(f"{prompt_text} (ตอบภาษาไทยอย่างละเอียด)")
            return res.text
        except: continue
    return "QUOTA_FULL"

# --- 4. ฟังก์ชันดึงรูปภาพ (โหลดให้เสร็จก่อนโชว์) ---
def fetch_image(prompt, width, height, style_suffix):
    full_prompt = prompt + style_suffix
    encoded = urllib.parse.quote(full_prompt)
    seed = int(time.time())
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"
    
    # พยายามดึงรูปภาพสูงสุด 3 ครั้ง
    for i in range(3):
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                return response.content, url
        except:
            time.sleep(2)
            continue
    return None, url

# --- 5. Sidebar ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v4.9")
    st.write(f"ยินดีต้อนรับค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา"])
    st.divider()
    st.caption("v4.9 | Image Data Fetcher")

# --- 6. โซนการทำงาน ---
if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package")
    topic = st.text_input("หัวข้อคอนเทนต์:", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: chosen_style = st.selectbox("เลือกสไตล์ภาพ:", list(STYLE_PRESETS.keys()))
    with col_s2: chosen_size = st.selectbox("เลือกขนาด:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("ใส่หัวข้อก่อนนะคะ")
        else:
            with st.spinner("⏳ กำลังเตรียมเนื้อหาภาษาไทย..."):
                text_res = generate_thai_content(f"ทำคอนเทนต์เรื่อง '{topic}': 1.ชื่อคลิป Viral 5 แบบ, 2.แคปชั่นป้ายยา Affiliate, 3.สคริปต์การถ่ายทำ")
                
                if text_res == "QUOTA_FULL":
                    st.error("โควต้าเต็ม รบกวนรอ 1 นาทีนะคะ")
                else:
                    with st.spinner("🎨 กำลังวาดรูปและโหลดภาพให้ชัวร์..."):
                        eng_p = translate_visual(topic)
                        w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                        img_data, final_url = fetch_image(eng_p, w, h, STYLE_PRESETS[chosen_style])
                        
                        st.divider()
                        st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                        
                        if img_data:
                            # จัดกลาง
                            c1, c2, c3 = st.columns([1, 2, 1]) if "9:16" in chosen_size else st.columns([0.1, 5, 0.1])
                            with c2:
                                st.image(img_data, use_container_width=True)
                                st.markdown(f'<div style="text-align:center;"><a href="{final_url}" target="_blank" style="color:#FF4B4B; font-weight:bold;">📥 ดาวน์โหลดภาพขนาดเต็ม</a></div>', unsafe_allow_html=True)
                        else:
                            st.error("❌ ดึงรูปภาพไม่สำเร็จเนื่องจากเซิร์ฟเวอร์ช้าเกินไป รบกวนกดปุ่มใหม่อีกครั้งนะค")
                    
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)

# (หมวดหมู่อื่นๆ ปรับปรุงให้ใช้ fetch_image เช่นกันค่ะ)