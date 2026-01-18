import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import io
from PIL import Image
import time

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. ฟังก์ชันเรียกใช้ Gemini พร้อมระบบสลับกุญแจ (Rotation) ---
def call_gemini_with_retry(prompt_text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    if not keys:
        st.error("❌ ไม่พบรายการ GEMINI_KEYS ใน Secrets ค่ะ")
        st.stop()
    
    for idx, key in enumerate(keys):
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(prompt_text)
            return response.text
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                if idx < len(keys) - 1:
                    st.warning(f"⚠️ กุญแจดอกที่ {idx+1} เต็ม กำลังสลับไปใช้ดอกที่ {idx+2} ค่ะ")
                    time.sleep(2)
                    continue
                else:
                    st.error("❌ กุญแจทุกดอกโควต้าเต็มหมดแล้วค่ะ รบกวนรอ 1-2 นาทีนะคะ")
                    st.stop()
            else:
                st.error(f"เกิดข้อผิดพลาด: {e}")
                st.stop()

# --- 3. ฟังก์ชันเสกรูปพร้อมระบบ Auto-Retry และขนาดภาพ ---
def generate_image_logic(prompt, width, height, hf_key, max_retries=5):
    # ใช้โมเดล SD v1.5 ที่เสถียรกว่าเพื่อเลี่ยง Error 410
    api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    headers = {"Authorization": f"Bearer {hf_key}"}
    payload = {
        "inputs": prompt,
        "parameters": {"width": width, "height": height}
    }
    
    for i in range(max_retries):
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.content
        elif response.status_code == 503:
            st.info(f"⏳ เซิร์ฟเวอร์วาดรูปกำลังตื่น... กำลังลองใหม่ครั้งที่ {i+1}/{max_retries} (รอ 10 วิ)")
            time.sleep(10)
        else:
            raise Exception(f"Hugging Face Error: {response.status_code}")
    raise Exception("เซิร์ฟเวอร์ไม่ว่างนานเกินไปค่ะ")

# --- 4. Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub")
    st.write("สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio(
        "เลือกเครื่องมือ:",
        ["🎨 เสกรูปภาพด้วย AI", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิปให้น่าคลิก", "💬 ผู้ช่วยตอบคอมเมนต์"]
    )
    st.divider()
    st.caption("v2.5 | Stable Model & Fixed Indent")

# --- 5. โซนการทำงานตามเมนู ---
if menu == "🎨 เสกรูปภาพด้วย AI":
    st.header("🎨 AI ศิลปินเสกรูปภาพ (รองรับขนาดภาพและสลับกุญแจอัตโนมัติ)")
    img_desc = st.text_area("บรรยายภาพที่ต้องการ (ภาษาไทย)", placeholder="เช่น แมวซ่อมมือถือในโลกอนาคต")
    
    col1, col2 = st.columns(2)
    with col1:
        size_option = st.selectbox(
            "เลือกขนาดภาพ:",
            ["แนวตั้ง (9:16) - TikTok/Reels", "แนวนอน (16:9) - FB/YouTube", "จัตุรัส (1:1) - IG/Profile"]
        )
    
    # ปรับขนาดให้เหมาะสมกับโมเดล SD v1.5
    if "9:16" in size_option: w, h = 512, 896
    elif "16:9" in size_option: w, h = 896, 512
    else: w, h = 512, 512

    if st.button("✨ เริ่มเสกรูป"):
        hf_api_key = st.secrets.get("HUGGINGFACE_API_KEY")
        if not img_desc:
            st.warning("กรุณาใส่คำบรรยายภาพก่อนค่ะ")
        elif not hf_api_key:
            st.error("ไม่พบ Hugging Face API Key ค่ะ")
        else:
            with st.spinner("⏳ กำลังใช้ Gemini แปลภาษาและปรับปรุง Prompt..."):
                eng_prompt = call_gemini_with_retry(f"Generate a detailed English image prompt for: {img_desc}")
                st.info(f"✅ Prompt ที่ใช้: {eng_prompt}")
            
            with st.spinner("🎨 กำลังวาดรูปตามขนาดที่เลือก..."):
                try:
                    img_bytes = generate_image_logic(eng_prompt, w, h, hf_api_key)
                    image = Image.open(io.BytesIO(img_bytes))
                    st.image(image, caption=f"ภาพขนาด {size_option} เสร็จแล้วค่ะ!", use_container_width=True)
                    
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("📥 ดาวน์โหลดรูป", data=buf.getvalue(), file_name="ai_image.png")
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")

elif menu == "🎬 วางแผนคอนเทนต์":
    st.header("🎬 วางแผนคอนเทนต์ทุกแพลตฟอร์ม")
    topic = st.text_input("หัวข้อคอนเทนต์")
    if st.button("✨ วางแผน"):
        with st.spinner("กำลังคิดแผนการโพสต์..."):
            result = call_gemini_with_retry(f"วางแผนคอนเทนต์เรื่อง {topic} ให้เป็นมืออาชีพ")
            st.markdown(result)

elif menu == "💰 เขียนแคปชั่นป้ายยา":
    st.header("💰 เขียนแคปชั่นป้ายยา Affiliate")
    details = st.text_area("ข้อมูลสินค้า")
    if st.button("💸 เสกแคปชั่น"):
        with st.spinner("กำลังเรียบเรียงคำพูด..."):
            result = call_gemini_with_retry(f"เขียนแคปชั่นป้ายยาแรงๆ จากข้อมูลนี้: {details}")
            st.code(result)

elif menu == "🔍 ตั้งชื่อคลิปให้น่าคลิก":
    st.header("🔍 ตัวช่วยตั้งชื่อให้คนกดดู")
    topic_name = st.text_input("เนื้อหาคลิปสรุป")
    if st.button("🚀 เสกชื่อคลิป"):
        with st.spinner("กำลังคิดชื่อที่น่าสนใจ..."):
            result = call_gemini_with_retry(f"คิดชื่อคลิป Viral 5 แบบ สำหรับเรื่อง {topic_name}")
            st.markdown(result)

elif menu == "💬 ผู้ช่วยตอบคอมเมนต์":
    st.header("💬 ผู้ช่วยตอบคอมเมนต์")
    comment = st.text_area("คอมเมนต์จากแฟนคลับ")
    style = st.select_slider("เลือกสไตล์", options=["สุภาพ", "เป็นกันเอง", "กวนๆ"])
    if st.button("💭 คิดคำตอบ"):
        with st.spinner("กำลังหาคำตอบที่โดนใจ..."):
            result = call_gemini_with_retry(f"คิดคำตอบคอมเมนต์ '{comment}' สไตล์ {style}")
            st.code(result)