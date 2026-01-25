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

# --- 2. AI IMAGE GENERATION (ระบบหลายโมเดล) ---
def generate_image(prompt_text, hf_token, model_url):
    headers = {"Authorization": f"Bearer {hf_token}"}
    try:
        response = requests.post(model_url, headers=headers, json={"inputs": prompt_text}, timeout=50)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content)), "OK"
        elif response.status_code == 503:
            return None, "⏳ โมเดลกำลังโหลด... กดซ้ำอีก 2-3 ครั้งนะคะ"
        elif response.status_code == 410:
            return None, "❌ โมเดลนี้ถูกปิดไปแล้ว (ลองเลือกตัวเลือกอื่นในกล่องด้านบนนะคะ)"
        else:
            return None, f"Error Code: {response.status_code} ({response.reason})"
    except Exception as e:
        return None, str(e)

# --- 3. CONFIG ---
st.set_page_config(page_title="Creator Hub v12.4 (Multi-Model)", page_icon="🚀", layout="wide")

try:
    HF_TOKEN = st.secrets["HUGGINGFACE_API_KEY"]
except:
    HF_TOKEN = None

# --- 4. SIDEBAR MENU ---
with st.sidebar:
    st.title("🚀 Creator Hub v12.4")
    menu = st.selectbox("เลือกเครื่องมือ:", [
        "🎨 AI สร้างภาพ (เลือกโมเดลได้)",
        "💡 คลังไอเดีย & Shot List",
        "🔗 คลังลิงก์ป้ายยาด่วน",
        "📱 แฮชแท็ก & แคปชั่นลับ",
        "💬 สคริปต์ตอบแชทปิดการขาย",
        "✅ Checklist กระจายโพสต์"
    ])
    st.divider()

# --- 5. FUNCTIONALITY ---

if menu == "🎨 AI สร้างภาพ (เลือกโมเดลได้)":
    st.header("🎨 AI เนรมิตภาพ")
    
    # === ส่วนเลือกโมเดล (พระเอกของเรา) ===
    st.info("💡 ถ้าอันไหนขึ้น Error 410 ให้ลองเปลี่ยนเป็นตัวเลือกอื่นนะคะ")
    model_option = st.selectbox(
        "เลือกสไตล์ภาพ / โรงงานผลิต:",
        [
            ("Stable Diffusion 2.1 (มาตรฐานใหม่)", "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"),
            ("Stable Diffusion XL (สวยคมชัด)", "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"),
            ("OpenJourney (สไตล์ศิลปะ Midjourney)", "https://api-inference.huggingface.co/models/prompthero/openjourney"),
            ("Stable Diffusion 1.5 (รุ่นเก่า)", "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5")
        ]
    )
    # ดึง URL จากตัวเลือกที่ user กด
    selected_model_url = model_option[1] 
    
    prompt = st.text_area("คำอธิบายภาพ (ภาษาอังกฤษ):", placeholder="เช่น: A futuristic cyberpunk city, neon lights, highly detailed")
    
    if st.button("✨ เริ่มสร้างภาพ"):
        if not HF_TOKEN:
            st.error("ไม่พบกุญแจใน Secrets")
        elif prompt:
            with st.spinner(f"⏳ กำลังสั่งงานโมเดล {model_option[0]} ..."):
                img, msg = generate_image(prompt, HF_TOKEN, selected_model_url)
                if img:
                    st.image(img, caption=f"สร้างโดย: {model_option[0]}", use_container_width=True)
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button("📥 ดาวน์โหลด", buf.getvalue(), "ai_image.png", "image/png")
                else:
                    st.error(f"⚠️ เกิดปัญหา: {msg}")
                    if "410" in msg:
                        st.warning("👉 คำแนะนำ: ลองเปลี่ยนตัวเลือกในกล่อง 'เลือกสไตล์ภาพ' ด้านบนเป็นอันอื่นดูนะคะ")
        else:
            st.warning("พิมพ์สิ่งที่อยากให้วาดก่อนนะค่ะ")

# (ส่วนเมนูอื่นๆ 💡, 🔗, 📱, 💬, ✅ เหมือนเดิมตาม v12.3 เลยค่ะ ก๊อปต่อท้ายได้เลย)
# เพื่อความชัวร์ ก๊อปส่วน Database และเมนูอื่นๆ จาก v12.3 มาใส่ต่อท้ายตรงนี้นะคะ
# หรือถ้าคุณเก่งมีไฟล์เดิมอยู่แล้ว ให้แก้แค่ส่วน "menu == 🎨 AI สร้างภาพ" ก็พอค่ะ