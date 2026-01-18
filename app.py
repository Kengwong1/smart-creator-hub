import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import io
from PIL import Image
import time

# --- 1. ตั้งค่าพื้นฐาน ---
st.set_page_config(page_title="Smart Creator Hub", page_icon="🎬", layout="wide")
load_dotenv()

# โหลดกุญแจ
gemini_api_key = os.getenv("GEMINI_API_KEY")
hf_api_key = os.getenv("HUGGINGFACE_API_KEY")

# ตรวจสอบเบื้องต้น
if not gemini_api_key:
    st.error("❌ ไม่พบ Gemini API Key ในระบบ")
    st.stop()

# ตั้งค่าโมเดล
genai.configure(api_key=gemini_api_key)
model_text = genai.GenerativeModel('gemini-flash-latest')

# ฟังก์ชันเสกรูป (Hugging Face)
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
hf_headers = {"Authorization": f"Bearer {hf_api_key}"}

def generate_image(prompt):
    response = requests.post(HF_API_URL, headers=hf_headers, json={"inputs": prompt})
    if response.status_code != 200:
        raise Exception(f"Hugging Face Error: {response.status_code}")
    return response.content

# --- Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio(
        "เลือกเครื่องมือ:",
        ["🎨 เสกรูปภาพด้วย AI", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิปให้น่าคลิก", "💬 ผู้ช่วยตอบคอมเมนต์"]
    )
    st.divider()
    st.caption("v2.1 | Fixed Quota Issues")

# --- โซน 1: เสกรูปภาพด้วย AI (เวอร์ชันแก้ Error) ---
if menu == "🎨 เสกรูปภาพด้วย AI":
    st.header("🎨 AI ศิลปินเสกรูปภาพตามสั่ง")
    st.write("ถ้าเสกไม่ได้เพราะโควต้าเต็ม ระบบจะแจ้งเตือนให้คุณพัก 1 นาทีค่ะ")
    
    img_desc = st.text_area("บรรยายภาพที่ต้องการ (ภาษาไทย)", placeholder="เช่น ช่างซ่อมมือถือในโลกอนาคต แสงนีออน สไตล์เกมเมอร์")
    
    if st.button("✨ เริ่มเสกรูป"):
        if not hf_api_key:
            st.error("กรุณาใส่ Hugging Face Token ก่อนนะค")
        elif not img_desc:
            st.warning("ใส่คำอธิบายภาพก่อนค่ะ")
        else:
            # ขั้นตอนแปลภาษา (ดัก Error โควต้าเต็ม)
            eng_prompt = ""
            with st.spinner("⏳ กำลังแปลภาษา (ใช้ Gemini)..."):
                try:
                    trans_res = model_text.generate_content(f"Translate this to a detailed English image prompt: {img_desc}")
                    eng_prompt = trans_res.text
                    st.info(f"แปลเป็น: {eng_prompt}")
                except Exception as e:
                    if "429" in str(e) or "ResourceExhausted" in str(e):
                        st.error("⚠️ ตอนนี้คุณใช้ Gemini เยอะเกินไปแล้วค่ะ! รบกวนรอ 1-2 นาทีแล้วกดใหม่นะคะ (โควต้าฟรีมีจำกัดค่ะ)")
                        st.stop()
                    else:
                        st.error(f"เกิดข้อผิดพลาด: {e}")
                        st.stop()

            # ขั้นตอนวาดรูป
            if eng_prompt:
                with st.spinner("🎨 กำลังวาดรูป (ใช้ Hugging Face)..."):
                    try:
                        img_bytes = generate_image(eng_prompt)
                        image = Image.open(io.BytesIO(img_bytes))
                        st.image(image, caption="ภาพของคุณเสร็จแล้ว!", use_container_width=True)
                        
                        buf = io.BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button("📥 ดาวน์โหลดรูป", data=buf.getvalue(), file_name="ai_image.png")
                    except Exception as e:
                        st.error("⌛ เซิร์ฟเวอร์วาดรูปกำลังโหลดหนัก/กำลังตื่น รบกวนกดใหม่อีกครั้งใน 30 วินาทีนะคะ")

# --- โซนอื่นๆ (ใส่ไว้ให้ครบเหมือนเดิม) ---
elif menu == "🎬 วางแผนคอนเทนต์":
    st.header("🎬 วางแผนคอนเทนต์")
    topic = st.text_input("หัวข้อ")
    if st.button("วางแผน"):
        try:
            res = model_text.generate_content(f"วางแผนคอนเทนต์เรื่อง {topic}")
            st.markdown(res.text)
        except: st.error("โควต้าเต็ม รอ 1 นาทีค่ะ")

elif menu == "💰 เขียนแคปชั่นป้ายยา":
    st.header("💰 เขียนแคปชั่นป้ายยา")
    details = st.text_area("ข้อมูลสินค้า")
    if st.button("เสกแคปชั่น"):
        try:
            res = model_text.generate_content(f"เขียนแคปชั่นขายของ: {details}")
            st.code(res.text)
        except: st.error("โควต้าเต็ม รอ 1 นาทีค่ะ")

elif menu == "🔍 ตั้งชื่อคลิปให้น่าคลิก":
    st.header("🔍 ตั้งชื่อคลิป")
    topic_name = st.text_input("สรุปเนื้อหา")
    if st.button("🚀 คิดชื่อคลิป"):
        try:
            res = model_text.generate_content(f"คิดชื่อคลิป Viral: {topic_name}")
            st.markdown(res.text)
        except: st.error("โควต้าเต็ม รอ 1 นาทีค่ะ")

elif menu == "💬 ผู้ช่วยตอบคอมเมนต์":
    st.header("💬 ผู้ช่วยตอบคอมเมนต์")
    comment = st.text_area("คอมเมนต์")
    if st.button("คิดคำตอบ"):
        try:
            res = model_text.generate_content(f"ตอบคอมเมนต์นี้: {comment}")
            st.code(res.text)
        except: st.error("โควต้าเต็ม รอ 1 นาทีค่ะ")