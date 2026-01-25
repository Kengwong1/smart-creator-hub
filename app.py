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
    # ตรวจสอบ Model ID ให้แม่นยำที่สุด
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {hf_token}"}
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt_text}, timeout=45)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content)), "OK"
        elif response.status_code == 401:
            return None, "Token ไม่ถูกต้อง (Unauthorized)"
        elif response.status_code == 503:
            return None, "โมเดลกำลังโหลด (Model Loading) - ลองกดซ้ำนะคะ"
        else:
            return None, f"Error Code: {response.status_code}"
    except Exception as e:
        return None, str(e)

# --- 3. CONFIG & SECRETS CHECK ---
st.set_page_config(page_title="Ultimate Creator Hub v12.2", page_icon="🚀", layout="wide")

# ดึงรหัสลับจากระบบ Secrets
try:
    # ตรวจสอบชื่อตัวแปรให้ตรงกับในหน้า Streamlit Secrets เป๊ะๆ
    HF_TOKEN = st.secrets["HUGGINGFACE_API_KEY"]
except Exception as e:
    HF_TOKEN = None

# --- 4. SIDEBAR MENU ---
with st.sidebar:
    st.title("🚀 Creator Hub v12.2")
    menu = st.selectbox("เลือกเครื่องมือ:", [
        "🎨 AI สร้างภาพโปรโมต",
        "💡 คลังไอเดีย & Shot List",
        "🔗 คลังลิงก์ป้ายยาด่วน",
        "📱 แฮชแท็ก & แคปชั่นลับ",
        "💬 สคริปต์ตอบแชทปิดการขาย",
        "✅ Checklist กระจายโพสต์"
    ])
    st.divider()
    st.caption("Debug Mode Enabled 🛠️")

# --- 5. FUNCTIONALITY ---

if menu == "🎨 AI สร้างภาพโปรโมต":
    st.header("🎨 AI เนรมิตภาพสวย (Debug Version)")
    
    # --- ส่วนตรวจสอบกุญแจ (Debug) ---
    with st.expander("🛠️ ตรวจสอบสถานะกุญแจ (สำหรับคุณเก่ง)"):
        if HF_TOKEN:
            st.success(f"✅ ตรวจพบกุญแจในระบบ: {HF_TOKEN[:5]}***{HF_TOKEN[-4:]}")
            st.info("ถ้าภาพไม่ขึ้น ให้ลองเช็กว่าใน Hugging Face ตั้งค่า Token เป็น 'Read' หรือยังนะคะ")
        else:
            st.error("❌ ไม่พบกุญแจชื่อ 'HUGGINGFACE_API_KEY' ใน Secrets")
            st.write("กรุณาไปที่ Manage App > Settings > Secrets แล้วพิมพ์:")
            st.code('HUGGINGFACE_API_KEY = "hf_xxxxxx"')
    # ----------------------------

    prompt = st.text_area("คำอธิบายภาพ (ภาษาอังกฤษ):", placeholder="เช่น: A cute robot repairman, cinematic lighting")
    
    if st.button("✨ เริ่มสร้างภาพ"):
        if not HF_TOKEN:
            st.error("ระบบทำงานไม่ได้เพราะไม่มีกุญแจค่ะ")
        elif prompt:
            with st.spinner("⏳ กำลังสั่ง AI วาดภาพ..."):
                img, msg = generate_image(prompt, HF_TOKEN)
                if img:
                    st.image(img, caption="ผลงาน AI ของคุณเก่งค่ะ", use_container_width=True)
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button("📥 ดาวน์โหลดภาพ", buf.getvalue(), "ai_image.png", "image/png")
                else:
                    st.error(f"❌ พบปัญหา: {msg}")
                    if "503" in msg:
                        st.warning("คำแนะนำ: โมเดลกำลังตื่นนอนค่ะ ลองกดปุ่มสร้างภาพซ้ำอีก 2-3 ครั้งนะคะ")
        else:
            st.warning("พิมพ์สิ่งที่อยากให้วาดก่อนนะค่ะ")

# --- เมนูอื่นๆ ใส่ไว้เพื่อให้แอปสมบูรณ์ค่ะ ---
elif menu == "💡 คลังไอเดีย & Shot List":
    st.header("💡 คลังไอเดียคอนเทนต์")
    with st.form("idea_form", clear_on_submit=True):
        t = st.text_input("หัวข้อคอนเทนต์:")
        n = st.text_area("มุมกล้อง/สคริปต์ย่อ:")
        if st.form_submit_button("บันทึก"):
            c.execute("INSERT INTO ideas (title, note) VALUES (?,?)", (t, n))
            conn.commit()
            st.rerun()
    data = pd.read_sql_query("SELECT * FROM ideas", conn)
    for i, row in data.iterrows():
        with st.expander(f"📌 {row['title']}"):
            st.write(row['note'])
            if st.button("🗑️ ลบ", key=f"del_{row['id']}"):
                c.execute(f"DELETE FROM ideas WHERE id={row['id']}")
                conn.commit()
                st.rerun()

elif menu == "🔗 คลังลิงก์ป้ายยาด่วน":
    st.header("🔗 รวมพิกัดสินค้า")
    with st.form("link_form", clear_on_submit=True):
        n = st.text_input("ชื่อสินค้า:")
        u = st.text_input("URL ลิงก์:")
        if st.form_submit_button("เพิ่ม"):
            c.execute("INSERT INTO links (name, url) VALUES (?,?)", (n, u))
            conn.commit()
            st.rerun()
    data = pd.read_sql_query("SELECT * FROM links", conn)
    for i, row in data.iterrows():
        st.code(f"🔥 {row['name']}\n📍 พิกัด: {row['url']}")

elif menu == "📱 แฮชแท็ก & แคปชั่นลับ":
    st.header("📱 คลังแฮชแท็กดึงดูดวิว")
    with st.form("tag_form", clear_on_submit=True):
        g = st.text_input("ชื่อกลุ่ม:")
        t = st.text_area("แฮชแท็ก:")
        if st.form_submit_button("บันทึก"):
            c.execute("INSERT INTO hashtags (group_name, tags) VALUES (?,?)", (g, t))
            conn.commit()
            st.rerun()
    data = pd.read_sql_query("SELECT * FROM hashtags", conn)
    for i, row in data.iterrows():
        with st.expander(f"🏷️ {row['group_name']}"):
            st.code(row['tags'])

elif menu == "💬 สคริปต์ตอบแชทปิดการขาย":
    st.header("💬 ประโยคปิดการขาย")
    with st.form("script_form", clear_on_submit=True):
        topic = st.text_input("หัวข้อ:")
        cont = st.text_area("ข้อความ:")
        if st.form_submit_button("บันทึก"):
            c.execute("INSERT INTO scripts (topic, content) VALUES (?,?)", (topic, cont))
            conn.commit()
            st.rerun()
    data = pd.read_sql_query("SELECT * FROM scripts", conn)
    for i, row in data.iterrows():
        st.subheader(f"💡 {row['topic']}")
        st.code(row['content'])

elif menu == "✅ Checklist กระจายโพสต์":
    st.header("✅ เช็กรายการโพสต์ 5 ช่องทาง")
    v_name = st.text_input("ชื่อคลิป:")
    st.checkbox("Facebook")
    st.checkbox("TikTok")
    st.checkbox("YouTube Shorts")
    st.checkbox("Instagram Reels")
    st.checkbox("Line VOOM")