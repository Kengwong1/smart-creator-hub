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

# --- 2. AI IMAGE GENERATION FUNCTION (แก้ Error 410 ตรงนี้) ---
def generate_image(prompt_text, hf_token):
    # เปลี่ยน URL เป็นรุ่นที่เสถียรที่สุด (Stable Diffusion v1.5)
    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    headers = {"Authorization": f"Bearer {hf_token}"}
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt_text}, timeout=45)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content)), "OK"
        elif response.status_code == 503:
            return None, "⏳ โมเดลกำลังตื่นนอน (Loading)... กรุณากดซ้ำอีก 2-3 ครั้งนะคะ"
        elif response.status_code == 401:
            return None, "🔑 กุญแจ (Token) ไม่ถูกต้อง หรือสิทธิ์ไม่พอ"
        else:
            return None, f"Error Code: {response.status_code} ({response.reason})"
    except Exception as e:
        return None, str(e)

# --- 3. CONFIG & SECRETS CHECK ---
st.set_page_config(page_title="Creator Hub v12.3 (Stable)", page_icon="🚀", layout="wide")

try:
    HF_TOKEN = st.secrets["HUGGINGFACE_API_KEY"]
except:
    HF_TOKEN = None

# --- 4. SIDEBAR MENU ---
with st.sidebar:
    st.title("🚀 Creator Hub v12.3")
    menu = st.selectbox("เลือกเครื่องมือ:", [
        "🎨 AI สร้างภาพโปรโมต",
        "💡 คลังไอเดีย & Shot List",
        "🔗 คลังลิงก์ป้ายยาด่วน",
        "📱 แฮชแท็ก & แคปชั่นลับ",
        "💬 สคริปต์ตอบแชทปิดการขาย",
        "✅ Checklist กระจายโพสต์"
    ])
    st.divider()
    st.caption("✅ Fix Error 410 Applied")

# --- 5. FUNCTIONALITY ---

if menu == "🎨 AI สร้างภาพโปรโมต":
    st.header("🎨 AI เนรมิตภาพ (รุ่นเสถียร)")
    
    # Debug Bar
    with st.expander("🛠️ เช็กสถานะระบบ"):
        if HF_TOKEN:
            st.success(f"✅ กุญแจพร้อมใช้งาน (..{HF_TOKEN[-4:]})")
        else:
            st.error("❌ ไม่พบกุญแจใน Secrets")

    prompt = st.text_area("คำอธิบายภาพ (ภาษาอังกฤษ):", placeholder="เช่น: A cute cat sitting on a computer desk, highly detailed, 8k")
    
    if st.button("✨ เริ่มสร้างภาพ"):
        if not HF_TOKEN:
            st.error("กรุณาตั้งค่า HUGGINGFACE_API_KEY ใน Secrets ก่อนนะคะ")
        elif prompt:
            with st.spinner("⏳ กำลังสั่ง AI วาดภาพ..."):
                img, msg = generate_image(prompt, HF_TOKEN)
                if img:
                    st.image(img, caption="ผลงาน AI ของคุณเก่งค่ะ", use_container_width=True)
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button("📥 ดาวน์โหลดภาพ", buf.getvalue(), "ai_image.png", "image/png")
                else:
                    st.warning(f"⚠️ แจ้งเตือน: {msg}")
        else:
            st.warning("พิมพ์สิ่งที่อยากให้วาดก่อนนะค่ะ")

# --- เมนูเดิม (คงไว้ครบถ้วน) ---
elif menu == "💡 คลังไอเดีย & Shot List":
    st.header("💡 คลังไอเดียคอนเทนต์")
    with st.form("idea_form", clear_on_submit=True):
        t = st.text_input("หัวข้อ:")
        n = st.text_area("รายละเอียด:")
        if st.form_submit_button("บันทึก"):
            c.execute("INSERT INTO ideas (title, note) VALUES (?,?)", (t, n))
            conn.commit()
            st.rerun()
    data = pd.read_sql_query("SELECT * FROM ideas", conn)
    for i, row in data.iterrows():
        with st.expander(f"📌 {row['title']}"):
            st.write(row['note'])
            if st.button("ลบ", key=f"del_i_{row['id']}"):
                c.execute(f"DELETE FROM ideas WHERE id={row['id']}")
                conn.commit()
                st.rerun()

elif menu == "🔗 คลังลิงก์ป้ายยาด่วน":
    st.header("🔗 รวมพิกัดสินค้า")
    with st.form("link_form", clear_on_submit=True):
        n = st.text_input("ชื่อสินค้า:")
        u = st.text_input("URL:")
        if st.form_submit_button("เพิ่ม"):
            c.execute("INSERT INTO links (name, url) VALUES (?,?)", (n, u))
            conn.commit()
            st.rerun()
    data = pd.read_sql_query("SELECT * FROM links", conn)
    for i, row in data.iterrows():
        st.code(f"🔥 {row['name']}\n📍 พิกัด: {row['url']}")

elif menu == "📱 แฮชแท็ก & แคปชั่นลับ":
    st.header("📱 คลังแฮชแท็ก")
    with st.form("tag_form", clear_on_submit=True):
        g = st.text_input("กลุ่ม:")
        t = st.text_area("Tags:")
        if st.form_submit_button("บันทึก"):
            c.execute("INSERT INTO hashtags (group_name, tags) VALUES (?,?)", (g, t))
            conn.commit()
            st.rerun()
    data = pd.read_sql_query("SELECT * FROM hashtags", conn)
    for i, row in data.iterrows():
        with st.expander(f"🏷️ {row['group_name']}"):
            st.code(row['tags'])

elif menu == "💬 สคริปต์ตอบแชทปิดการขาย":
    st.header("💬 สคริปต์ตอบแชท")
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
    st.header("✅ Checklist")
    st.text_input("ชื่อคลิป:")
    st.checkbox("Facebook")
    st.checkbox("TikTok")
    st.checkbox("YouTube Shorts")
    st.checkbox("Instagram Reels")
    st.checkbox("Line VOOM")