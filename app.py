import streamlit as st
import sqlite3
import pandas as pd

# --- 1. SETUP DATABASE (รวมทุกอย่างไว้ในที่เดียว) ---
def init_db():
    conn = sqlite3.connect('ultimate_creator.db', check_same_thread=False)
    c = conn.cursor()
    # ตารางไอเดีย
    c.execute('CREATE TABLE IF NOT EXISTS ideas (id INTEGER PRIMARY KEY, title TEXT, platform TEXT, note TEXT)')
    # ตารางลิงก์ป้ายยา
    c.execute('CREATE TABLE IF NOT EXISTS links (id INTEGER PRIMARY KEY, name TEXT, url TEXT, tag TEXT)')
    # ตารางแฮชแท็ก
    c.execute('CREATE TABLE IF NOT EXISTS hashtags (id INTEGER PRIMARY KEY, group_name TEXT, tags TEXT)')
    # ตารางสคริปต์/คำตอบลูกค้า
    c.execute('CREATE TABLE IF NOT EXISTS scripts (id INTEGER PRIMARY KEY, topic TEXT, content TEXT)')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# --- 2. CONFIG หน้าเว็บ ---
st.set_page_config(page_title="Ultimate Creator Hub v11.0", page_icon="🚀", layout="wide")

# --- 3. SIDEBAR MENU ---
with st.sidebar:
    st.title("🚀 Creator Hub v11.0")
    st.write("เครื่องมือช่วยรวยของคนออนไลน์")
    menu = st.selectbox("เลือกเครื่องมือ:", [
        "💡 คลังไอเดีย & Shot List",
        "🔗 คลังลิงก์ป้ายยาด่วน",
        "📱 แฮชแท็ก & แคปชั่นลับ",
        "💬 สคริปต์ตอบแชทปิดการขาย",
        "✅ Checklist กระจายโพสต์ 5 ช่องทาง"
    ])
    st.divider()
    st.caption("No API | No Risk | 100% Productivity")

# --- 4. FUNCTIONALITY ---

# 4.1 คลังไอเดีย
if menu == "💡 คลังไอเดีย & Shot List":
    st.header("💡 คลังไอเดียคอนเทนต์")
    with st.expander("➕ เพิ่มไอเดียใหม่"):
        with st.form("idea_form", clear_on_submit=True):
            t = st.text_input("หัวข้อคอนเทนต์:")
            p = st.multiselect("จะลงแพลตฟอร์มไหนบ้าง?", ["Facebook", "TikTok", "YouTube", "Reels", "Lemon8"])
            n = st.text_area("จดบันทึก/มุมกล้องที่ต้องถ่าย:")
            if st.form_submit_button("บันทึกไอเดีย"):
                c.execute("INSERT INTO ideas (title, platform, note) VALUES (?,?,?)", (t, ", ".join(p), n))
                conn.commit()
                st.rerun()
    
    data = pd.read_sql_query("SELECT * FROM ideas", conn)
    if not data.empty:
        for i, row in data.iterrows():
            with st.container(border=True):
                st.write(f"📌 **{row['title']}**")
                st.caption(f"📺 แพลตฟอร์ม: {row['platform']}")
                st.write(row['note'])
                if st.button("🗑️ ลบไอเดีย", key=f"del_id_{row['id']}"):
                    c.execute(f"DELETE FROM ideas WHERE id={row['id']}")
                    conn.commit()
                    st.rerun()

# 4.2 คลังลิงก์ด่วน
elif menu == "🔗 คลังลิงก์ป้ายยาด่วน":
    st.header("🔗 รวมพิกัดสินค้า (กดก๊อปปี้ได้ทันที)")
    with st.form("link_form", clear_on_submit=True):
        n = st.text_input("ชื่อสินค้า:")
        u = st.text_input("URL ลิงก์ Affiliate:")
        if st.form_submit_button("เพิ่มเข้าคลัง"):
            c.execute("INSERT INTO links (name, url) VALUES (?,?)", (n, u))
            conn.commit()
            st.rerun()
    
    data = pd.read_sql_query("SELECT * FROM links", conn)
    for i, row in data.iterrows():
        st.code(f"🔥 {row['name']}\n📍 พิกัด: {row['url']}")

# 4.3 แฮชแท็ก & แคปชั่น
elif menu == "📱 แฮชแท็ก & แคปชั่นลับ":
    st.header("📱 คลังแฮชแท็กดึงดูดวิว")
    with st.form("tag_form", clear_on_submit=True):
        g = st.text_input("ชื่อกลุ่ม (เช่น สายไอโฟน, สายของกิน):")
        t = st.text_area("รายการแฮชแท็ก (ก๊อปมาวางเลย):")
        if st.form_submit_button("บันทึกกลุ่มแฮชแท็ก"):
            c.execute("INSERT INTO hashtags (group_name, tags) VALUES (?,?)", (g, t))
            conn.commit()
            st.rerun()
    
    data = pd.read_sql_query("SELECT * FROM hashtags", conn)
    for i, row in data.iterrows():
        with st.expander(f"🏷️ กลุ่ม: {row['group_name']}"):
            st.code(row['tags'])

# 4.4 สคริปต์ตอบแชท
elif menu == "💬 สคริปต์ตอบแชทปิดการขาย":
    st.header("💬 ประโยคปิดการขาย (ก๊อปไปตอบลูกค้า)")
    with st.form("script_form", clear_on_submit=True):
        topic = st.text_input("หัวข้อ (เช่น เมื่อลูกค้าบ่นแพง, ตามยอดโอน):")
        cont = st.text_area("ประโยคที่จะใช้:")
        if st.form_submit_button("บันทึกสคริปต์"):
            c.execute("INSERT INTO scripts (topic, content) VALUES (?,?)", (topic, cont))
            conn.commit()
            st.rerun()
    
    data = pd.read_sql_query("SELECT * FROM scripts", conn)
    for i, row in data.iterrows():
        st.subheader(f"💡 {row['topic']}")
        st.code(row['content'])

# 4.5 Checklist
elif menu == "✅ Checklist กระจายโพสต์ 5 ช่องทาง":
    st.header("✅ เช็กรายการโพสต์ (หนึ่งคลิปต้องกินให้คุ้ม)")
    st.write("เป้าหมาย: นำ 1 คลิป ไปลงให้ครบทุกที่เพื่อเพิ่มโอกาสการมองเห็น")
    
    video_name = st.text_input("ชื่อคลิปที่กำลังจะลง:")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.checkbox("Facebook")
    with col2: st.checkbox("TikTok")
    with col3: st.checkbox("YouTube Shorts")
    with col4: st.checkbox("Instagram Reels")
    with col5: st.checkbox("Line VOOM / อื่นๆ")
    
    st.info("💡 เคล็ดลับ: ลงห่างกันประมาณ 15-30 นาที เพื่อเช็กการทำงานของ Algorithm นะคะ")