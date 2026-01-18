import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
import requests
from io import BytesIO

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v5.1", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. สไตล์ภาพ (Visual Presets) ---
STYLE_PRESETS = {
    "สไตล์ปกติ (สมจริงพื้นฐาน)": ", professional macro photography, real human hands repairing smartphone, detailed tools, 8k, sharp focus, authentic workshop",
    "ช่างซ่อมยุคอวกาศ (Cyber Repair)": ", cyberpunk style, neon lights, intricate mechanical parts, 8k cinematic",
    "ฉากหลังสินค้า Affiliate (Studio)": ", high-end product photo, studio lighting, marble surface, blurred background",
    "ไทยโมเดิร์น (Thai Art)": ", Thai traditional gold pattern, elegant, artistic, 8k"
}

# --- 3. ระบบ AI และแปลภาษา ---
def translate_visual(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    prompt = f"Professional photography prompt: {text}. Focus on human hands and real tools. Realistic."
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(prompt)
            return res.text
        except: continue
    return text + ", professional photography, 8k"

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

# --- 4. ฟังก์ชันดึงรูปภาพ (โหลดจนเสร็จถึงจะโชว์) ---
def get_image_bytes(url):
    try:
        # ให้เวลารอรูปสูงสุด 30 วินาที
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.content
    except:
        return None
    return None

# --- 5. Sidebar เมนู (ครบ 6 เมนู) ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v5.1")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio(
        "เลือกเครื่องมือ:", 
        ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิปให้น่าคลิก", "💬 ผู้ช่วยตอบคอมเมนต์"]
    )
    st.divider()
    st.caption("v5.1 | Bulletproof Display Fix")

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
                    with st.spinner("🎨 กำลังวาดรูปและโหลดภาพให้ชัวร์ (อาจใช้เวลา 10-20 วินาที)..."):
                        eng_p = translate_visual(topic)
                        w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                        encoded = urllib.parse.quote(eng_p + STYLE_PRESETS[chosen_style])
                        final_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&nologo=true&seed={int(time.time())}"
                        
                        img_bytes = get_image_bytes(final_url)
                        
                        st.divider()
                        st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                        
                        if img_bytes:
                            # ปรับกรอบรูปภาพให้สวยงามและจัดกลาง
                            st.markdown(f"""
                                <div style="display: flex; justify-content: center; background-color: #0e1117; padding: 20px; border-radius: 15px;">
                                    <div style="max-width: 400px; width: 100%;">
                                        <img src="data:image/png;base64,{base64.b64encode(img_bytes).decode()}" style="width: 100%; border-radius: 10px; border: 2px solid #333;">
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ เซิร์ฟเวอร์รูปภาพไม่ตอบสนองชั่วคราว แต่คุณสามารถดูผ่านลิงก์นี้ได้ค่ะ:")
                        
                        st.markdown(f'### [📥 ดาวน์โหลดรูปภาพขนาดเต็ม]({final_url})')
                    
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)

# --- 6.2 เสกรูปภาพอย่างเดียว ---
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    st.header("🎨 AI ศิลปินเสกรูป")
    img_desc = st.text_area("อยากได้รูปอะไรคะ?")
    if st.button("✨ เริ่มวาดรูป"):
        with st.spinner("🎨 กำลังวาด..."):
            eng_p = translate_visual(img_desc)
            final_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(eng_p)}?width=768&height=768&nologo=true"
            st.image(final_url, use_container_width=True)
            st.markdown(f'[📥 ดาวน์โหลดรูปภาพ]({final_url})')

# --- เมนูย่อยอื่นๆ (ใช้งานตามปกติ) ---
elif menu == "🎬 วางแผนคอนเทนต์":
    topic = st.text_input("หัวข้อ:")
    if st.button("✨ วางแผน"):
        res = generate_thai_content(f"วางแผนคอนเทนต์: {topic}")
        if res != "QUOTA_FULL": st.markdown(res)
        else: st.error("รอ 1 นาทีนะคะ")

elif menu == "💰 เขียนแคปชั่นป้ายยา":
    details = st.text_area("ข้อมูลสินค้า:")
    if st.button("💸 เสกแคปชั่น"):
        res = generate_thai_content(f"เขียนแคปชั่น: {details}")
        if res != "QUOTA_FULL": st.code(res)
        else: st.error("รอ 1 นาทีนะคะ")

elif menu == "🔍 ตั้งชื่อคลิปให้น่าคลิก":
    topic = st.text_input("เนื้อหาคลิป:")
    if st.button("🚀 คิดชื่อ"):
        res = generate_thai_content(f"ชื่อคลิป 5 แบบ: {topic}")
        if res != "QUOTA_FULL": st.markdown(res)
        else: st.error("รอ 1 นาทีนะคะ")

elif menu == "💬 ผู้ช่วยตอบคอมเมนต์":
    comment = st.text_area("คอมเมนต์:")
    if st.button("💭 คิดคำตอบ"):
        res = generate_thai_content(f"ตอบคอมเมนต์: {comment}")
        if res != "QUOTA_FULL": st.code(res)
        else: st.error("รอ 1 นาทีนะคะ")

import base64 # เพิ่ม library สำหรับแสดงภาพ