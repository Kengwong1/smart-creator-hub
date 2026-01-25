import streamlit as st
import sqlite3
import pandas as pd
import requests
import io
from PIL import Image
import urllib.parse

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

# --- 2. AI IMAGE GENERATION (v12.6: ปรับขนาด + โมเดลชัด) ---
def generate_image_v3(prompt_text, width, height):
    # เพิ่มคำสั่งลับเพื่อให้ภาพชัดขึ้น
    enhanced_prompt = f"{prompt_text}, highly detailed face, realistic, sharp focus, 8k uhd"
    encoded_prompt = urllib.parse.quote(enhanced_prompt)
    
    # ใช้โมเดล 'flux' ที่ให้รายละเอียดสมจริง และกำหนดขนาดตามที่เลือก
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model=flux&nologo=true&seed={pd.Timestamp.now().microsecond}"
    
    try:
        response = requests.get(url, timeout=45)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content)), "OK"
        else:
            return None, f"Error: {response.status_code}"
    except Exception as e:
        return None, str(e)

# --- 3. CONFIG ---
st.set_page_config(page_title="Creator Hub v12.6", page_icon="🎨", layout="wide")

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🚀 Creator Hub v12.6")
    menu = st.selectbox("เครื่องมือ:", ["🎨 AI สร้างภาพ (ชัด+เลือกไซส์)", "💡 คลังไอเดีย", "🔗 คลังลิงก์", "📱 แฮชแท็ก", "💬 สคริปต์แชท", "✅ Checklist"])
    st.divider()
    st.success("โหมด: ภาพชัด หน้าไม่เละ ✨")

# --- 5. FUNCTIONALITY ---

if menu == "🎨 AI สร้างภาพ (ชัด+เลือกไซส์)":
    st.header("🎨 AI เนรมิตภาพ (ควบคุมได้ดั่งใจ)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_area("อยากให้วาดอะไร (ภาษาอังกฤษ):", placeholder="เช่น: Iron Man portrait, futuristic city background", height=150)
    
    with col2:
        st.write("📐 **เลือกสัดส่วนภาพ:**")
        aspect_ratio = st.radio(
            "สัดส่วน:",
            ("จัตุรัส (Square 1:1)", "แนวตั้ง (Portrait 2:3)", "แนวนอน (Landscape 16:9)"),
            index=0
        )
        
        # กำหนดขนาดตามที่เลือก
        if "Square" in aspect_ratio:
            w, h = 768, 768
        elif "Portrait" in aspect_ratio:
            w, h = 512, 768
        else: # Landscape
            w, h = 1024, 576

    if st.button("✨ เริ่มสร้างภาพ (แบบคมชัด)"):
        if prompt:
            with st.spinner("⏳ กำลังวาดภาพแบบละเอียด... รอสักครู่นะครับ"):
                img, msg = generate_image_v3(prompt, w, h)
                if img:
                    st.image(img, caption=f"สัดส่วน: {aspect_ratio}", use_container_width=True)
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button("📥 ดาวน์โหลดภาพ", buf.getvalue(), "ai_image_v12.6.png", "image/png")
                else:
                    st.error(f"เกิดปัญหา: {msg}")
        else:
            st.warning("กรุณาพิมพ์คำสั่งก่อนนะครับ")

# (ส่วนเมนูอื่นๆ 💡, 🔗, 📱, 💬, ✅ ใส่ต่อท้ายให้ครบเหมือนเดิมนะครับ)