import streamlit as st
import sqlite3
import pandas as pd
import requests
import io
from PIL import Image

# --- 1. SETUP DATABASE ---
def init_db():
    conn = sqlite3.connect('ultimate_creator.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS ideas (id INTEGER PRIMARY KEY, title TEXT, note TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS links (id INTEGER PRIMARY KEY, name TEXT, url TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS hashtags (id INTEGER PRIMARY KEY, group_name TEXT, tags TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS scripts (id INTEGER PRIMARY KEY, topic TEXT, content TEXT)')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# --- 2. AI IMAGE GENERATION FUNCTION ---
def generate_image(prompt_text, hf_token):
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {hf_token}"}
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt_text}, timeout=30)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            return None
    except:
        return None

# --- 3. CONFIG & SECRETS CHECK ---
st.set_page_config(page_title="Ultimate Creator Hub v12.1", page_icon="🚀", layout="wide")

# ดึงรหัสลับจากระบบที่เราเคยตั้งไว้
try:
    HF_TOKEN = st.secrets["HUGGINGFACE_API_KEY"]
except:
    HF_TOKEN = None
    st.error("⚠️ ไม่พบ HUGGINGFACE_API_KEY ใน Secrets ค่ะ")

# --- 4. SIDEBAR MENU ---
with st.sidebar:
    st.title("🚀 Creator Hub v12.1")
    menu = st.selectbox("เลือกเครื่องมือ:", [
        "🎨 AI สร้างภาพโปรโมต",
        "💡 คลังไอเดีย & Shot List",
        "🔗 คลังลิงก์ป้ายยาด่วน",
        "📱 แฮชแท็ก & แคปชั่นลับ",
        "💬 สคริปต์ตอบแชทปิดการขาย",
        "✅ Checklist กระจายโพสต์"
    ])
    st.divider()
    st.caption("Secure Mode Active 🛡️")

# --- 5. FUNCTIONALITY ---

if menu == "🎨 AI สร้างภาพโปรโมต":
    st.header("🎨 AI เนรมิตภาพสวย (Flux Model)")
    prompt = st.text_area("คำอธิบายภาพ (ภาษาอังกฤษ):", placeholder="เช่น: A luxury watch on a dark marble table, soft lighting")
    
    if st.button("✨ เริ่มสร้างภาพ"):
        if not HF_TOKEN:
            st.error("กรุณาเช็กการตั้งค่า HUGGINGFACE_API_KEY ใน Secrets ก่อนนะค่ะ")
        elif prompt:
            with st.spinner("⏳ กำลังวาดภาพ... (อาจใช้เวลา 10-20 วินาทีนะคะ)"):
                img = generate_image(prompt, HF_TOKEN)
                if img:
                    st.image(img, caption="ผลงาน AI ของคุณเก่งค่ะ", use_container_width=True)
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button("📥 ดาวน์โหลดภาพ", buf.getvalue(), "ai_image.png", "image/png")
                else:
                    st.error("❌ การวาดภาพขัดข้อง ลองใหม่อีกครั้งหรือเช็ก Token นะคะ")
        else:
            st.warning("พิมพ์สิ่งที่อยากให้วาดก่อนนะค่ะ")

# ... (ส่วนเมนูอื่นๆ 💡, 🔗, 📱, 💬, ✅ เหมือนเดิมตาม v11.0 ค่ะ)
# 💡 ฉันละไว้เพื่อประหยัดพื้นที่ แต่คุณเก่งก๊อปจาก v11.0 มาใส่ต่อได้เลยค่ะ