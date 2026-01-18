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

# --- 2. ฟังก์ชันเรียกใช้ Gemini (สลับกุญแจอัตโนมัติ) ---
def call_gemini_with_retry(prompt_text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    if not keys:
        st.error("❌ ไม่พบ GEMINI_KEYS ใน Secrets")
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
                    time.sleep(2)
                    continue
                else:
                    st.error("❌ โควต้า Gemini เต็มทุกดอกแล้วค่ะ รบกวนรอ 1-2 นาทีนะค")
                    st.stop()
    return None

# --- 3. ฟังก์ชันเสกรูป (ระบบศิลปินสำรอง 3 ชีวิต) ---
def generate_image_immortal(prompt, width, height, hf_key):
    # รายชื่อศิลปิน AI ที่ยังเปิดให้ใช้ฟรีและเสถียร
    models = [
        "runwayml/stable-diffusion-v1-5",
        "prompthero/openjourney",
        "stabilityai/stable-diffusion-2-1"
    ]
    
    headers = {"Authorization": f"Bearer {hf_key}"}
    payload = {
        "inputs": prompt,
        "parameters": {"width": width, "height": height}
    }

    for model_path in models:
        api_url = f"https://api-inference.huggingface.co/models/{model_path}"
        try:
            # ลองเรียกใช้โมเดล
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.content, model_path
            elif response.status_code == 503:
                st.warning(f"⏳ {model_path} กำลังหลับ... กำลังปลุกค่ะ (รอ 10 วิ)")
                time.sleep(10)
                # ลองซ้ำตัวเดิมอีก 1 รอบ
                response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                if response.status_code == 200: return response.content, model_path
            
            # ถ้า 410 หรือยังไม่ได้ผล ให้ข้ามไปรุ่นถัดไป
            st.write(f"⚠️ {model_path} ไม่พร้อมใช้งาน กำลังเปลี่ยนตัวศิลปิน...")
            continue
            
        except Exception:
            continue
            
    raise Exception("❌ ศิลปินทุกคนลาหยุดพร้อมกันค่ะ กรุณาลองใหม่ในอีก 1 นาทีนะคะ")

# --- 4. Sidebar ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["🎨 เสกรูปภาพด้วย AI", "🎬 วางแผนคอนเทนต์", "💰 แคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิป", "💬 ตอบคอมเมนต์"])
    st.divider()
    st.caption("v2.7 | Immortal AI Engine")

# --- 5. การทำงาน ---
if menu == "🎨 เสกรูปภาพด้วย AI":
    st.header("🎨 AI ศิลปินอมตะ (พร้อมระบบสำรอง)")
    img_desc = st.text_area("บรรยายภาพ (ไทยหรืออังกฤษก็ได้ค่ะ)", height=150)
    
    size_option = st.selectbox("ขนาดภาพ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    if "9:16" in size_option: w, h = 512, 896
    elif "16:9" in size_option: w, h = 896, 512
    else: w, h = 512, 512

    if st.button("✨ เริ่มเสกรูป"):
        hf_api_key = st.secrets.get("HUGGINGFACE_API_KEY")
        if not img_desc:
            st.warning("กรุณาใส่คำบรรยายก่อนค่ะ")
        else:
            # ตรวจสอบว่าเป็นภาษาอังกฤษอยู่แล้วหรือไม่ (เพื่อประหยัดโควต้า Gemini)
            is_english = all(ord(c) < 128 for c in img_desc[:50])
            
            with st.spinner("⏳ กำลังจัดเตรียมคำสั่ง..."):
                if is_english:
                    eng_prompt = img_desc
                else:
                    eng_prompt = call_gemini_with_retry(f"Convert this to detailed English image prompt: {img_desc}")
            
            if eng_prompt:
                st.info(f"✅ ใช้คำสั่ง: {eng_prompt[:100]}...")
                try:
                    with st.spinner("🎨 กำลังวาดภาพ (ระบบกำลังวนหาศิลปินที่ว่างให้ค่ะ)..."):
                        img_bytes, used_model = generate_image_immortal(eng_prompt, w, h, hf_api_key)
                        image = Image.open(io.BytesIO(img_bytes))
                        st.image(image, caption=f"วาดโดย: {used_model}", use_container_width=True)
                        
                        buf = io.BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button("📥 โหลดรูป", data=buf.getvalue(), file_name="ai_img.png")
                except Exception as e:
                    st.error(str(e))

# (เมนูอื่นๆ โค้ดเดิมจาก v2.6 ได้เลยค่ะ)
elif menu == "🎬 วางแผนคอนเทนต์":
    topic = st.text_input("หัวข้อ")
    if st.button("วางแผน"):
        res = call_gemini_with_retry(f"วางแผนคอนเทนต์: {topic}")
        if res: st.markdown(res)