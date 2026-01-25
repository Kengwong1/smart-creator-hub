import streamlit as st
import sqlite3
import pandas as pd
import requests
import io
from PIL import Image
import urllib.parse
import random

# --- 1. SETUP DATABASE (เหมือนเดิมค่ะ) ---
def init_db():
    conn = sqlite3.connect('ultimate_creator.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS ideas (id INTEGER PRIMARY KEY, title TEXT, note TEXT)')
    conn.commit()
    return conn
conn = init_db()
c = conn.cursor()

# --- 2. AI IMAGE ENGINE (v12.7: เน้นหน้าชัด) ---
def generate_image_v4(prompt_text, width, height):
    # ปรับ Prompt ให้หน้าไม่เละ
    quality_prompts = "high resolution, photorealistic, cinematic lighting, sharp focus, detailed skin texture, 8k"
    full_prompt = f"{prompt_text}, {quality_prompts}"
    encoded_prompt = urllib.parse.quote(full_prompt)
    
    # เพิ่ม Seed แบบสุ่มจัดๆ เพื่อเลี่ยง Rate Limit
    random_seed = random.randint(1, 999999999)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model=flux&nologo=true&seed={random_seed}"
    
    try:
        response = requests.get(url, timeout=45)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content)), "OK"
        else:
            return None, f"Error: {response.status_code} (Server Busy)"
    except Exception as e:
        return None, str(e)

# --- 3. CONFIG ---
st.set_page_config(page_title="Creator Hub v12.7", page_icon="🎨", layout="centered") # ปรับเป็น centered เพื่อไม่ให้เบ้อเริ่ม

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🚀 Hub v12.7")
    menu = st.selectbox("เลือก:", ["🎨 AI สร้างภาพ (ฉบับคุมไซส์)", "💡 คลังไอเดีย", "🔗 คลังลิงก์", "📱 แฮชแท็ก", "💬 สคริปต์แชท"])
    st.info("💡 ถ้าขึ้น Rate Limit ให้รอ 1-2 นาทีแล้วกดใหม่นะคะ")

# --- 5. FUNCTIONALITY ---
if menu == "🎨 AI สร้างภาพ (ฉบับคุมไซส์)":
    st.header("🎨 AI สร้างภาพ (หน้าชัด+ขนาดพอดี)")
    
    prompt = st.text_area("อยากได้ภาพอะไร:", placeholder="เช่น: A handsome businessman smiling, professional headshot")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        aspect = st.selectbox("สัดส่วนภาพ:", ["สี่เหลี่ยม (1:1)", "แนวตั้ง (TikTok 9:16)", "แนวนอน (YouTube 16:9)"])
    with col_s2:
        display_width = st.slider("ขนาดการแสดงผลบนเว็บ:", 200, 800, 400) # คุมขนาด "เบ้อเริ่ม" ได้ที่นี่

    # กำหนดขนาดไฟล์จริง
    if "สี่เหลี่ยม" in aspect: w, h = 1024, 1024
    elif "แนวตั้ง" in aspect: w, h = 720, 1280
    else: w, h = 1280, 720

    if st.button("✨ เนรมิตภาพ"):
        if prompt:
            with st.spinner("⏳ กำลังวาดภาพแบบละเอียด..."):
                img, msg = generate_image_v4(prompt, w, h)
                if img:
                    # คีย์สำคัญ: ใส่ width ใน st.image เพื่อไม่ให้ภาพ "เบ้อเริ่ม" ค่ะ
                    st.image(img, width=display_width, caption="ผลงาน AI ของคุณเก่งค่ะ")
                    
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button("📥 ดาวน์โหลดไฟล์จริง (ความละเอียดสูง)", buf.getvalue(), "ai_pro.png", "image/png")
                else:
                    st.error(f"❌ {msg}")
                    st.info("ลองเปลี่ยนข้อความ (Prompt) นิดหน่อย หรือรอสักครู่แล้วกดใหม่นะคะ")