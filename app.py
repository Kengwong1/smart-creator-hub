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
                    st.error("❌ โควต้า Gemini เต็มทุกกุญแจแล้วค่ะ รบกวนพัก 1 นาทีนะค")
                    st.stop()
    return None

# --- 3. ฟังก์ชันเสกรูป (ระบบศิลปินรุ่นใหม่ FLUX & SDXL) ---
def generate_image_immortal(prompt, width, height, hf_key):
    # เปลี่ยนรายชื่อโมเดลเป็นรุ่นใหม่ที่มักจะออนไลน์ในระบบฟรีค่ะ
    models = [
        "black-forest-labs/FLUX.1-schnell", # ตัวที่เก่งที่สุดตอนนี้
        "stabilityai/stable-diffusion-xl-base-1.0",
        "CompVis/stable-diffusion-v1-4" # ตัวสำรองสุดท้ายที่มักจะไม่ล่ม
    ]
    
    headers = {"Authorization": f"Bearer {hf_key}"}
    payload = {
        "inputs": prompt,
        "parameters": {"width": width, "height": height}
    }

    for model_path in models:
        api_url = f"https://api-inference.huggingface.co/models/{model_path}"
        try:
            st.write(f"🎨 กำลังติดต่อศิลปิน: {model_path}...")
            response = requests.post(api_url, headers=headers, json=payload, timeout=40)
            
            if response.status_code == 200:
                return response.content, model_path
            elif response.status_code == 503:
                # ถ้าโมเดลกำลังโหลด ต้องรอนานขึ้นนิดนึงค่ะ
                st.info(f"⏳ {model_path} กำลังเตรียมสี... รอ 20 วินาทีนะคะ")
                time.sleep(20)
                response = requests.post(api_url, headers=headers, json=payload, timeout=40)
                if response.status_code == 200: return response.content, model_path
            
            # หาก 410 หรือไม่ว่าง ให้ลองตัวถัดไปทันที
            continue
            
        except Exception:
            continue
            
    raise Exception("❌ ศิลปินทุกคนไม่พร้อมทำงานในขณะนี้ กรุณารอ 1 นาทีแล้วลองใหม่อีกครั้งนะคะ")

# --- 4. Sidebar ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["🎨 เสกรูปภาพด้วย AI", "🎬 วางแผนคอนเทนต์", "💰 แคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิป", "💬 ตอบคอมเมนต์"])
    st.divider()
    st.caption("v2.8 | FLUX & SDXL Support")

# --- 5. การทำงาน ---
if menu == "🎨 เสกรูปภาพด้วย AI":
    st.header("🎨 AI ศิลปินเสกรูปภาพ (Next-Gen Edition)")
    img_desc = st.text_area("อยากได้รูปอะไร? (ไทย/อังกฤษ)", height=100, placeholder="เช่น หุ่นยนต์ซ่อมมือถือสุดเท่ แสงสีนีออน")
    
    size_option = st.selectbox("เลือกขนาดภาพ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    if "9:16" in size_option: w, h = 512, 896
    elif "16:9" in size_option: w, h = 896, 512
    else: w, h = 768, 768

    if st.button("✨ เริ่มเสกรูป"):
        hf_api_key = st.secrets.get("HUGGINGFACE_API_KEY")
        if not img_desc:
            st.warning("กรุณาใส่คำบรรยายก่อนค่ะ")
        else:
            # เช็คภาษาอังกฤษเบื้องต้น
            is_english = all(ord(c) < 128 for c in img_desc[:50])
            
            with st.spinner("⏳ กำลังเตรียมสคริปต์ภาพ..."):
                if is_english:
                    eng_prompt = img_desc
                else:
                    eng_prompt = call_gemini_with_retry(f"Write a very short, high-quality image prompt in English for: {img_desc}")
            
            if eng_prompt:
                try:
                    with st.spinner("🎨 กำลังวาดภาพ... (ระบบกำลังสลับหาศิลปินที่ว่างให้ค่ะ)"):
                        img_bytes, used_model = generate_image_immortal(eng_prompt, w, h, hf_api_key)
                        image = Image.open(io.BytesIO(img_bytes))
                        st.image(image, caption=f"ผลงานโดย: {used_model}", use_container_width=True)
                        
                        buf = io.BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button("📥 โหลดรูปนี้", data=buf.getvalue(), file_name="ai_creator.png", mime="image/png")
                except Exception as e:
                    st.error(str(e))

# --- เมนูอื่นๆ (ใช้ Gemini สลับกุญแจ) ---
elif menu == "🎬 วางแผนคอนเทนต์":
    topic = st.text_input("หัวข้อ")
    if st.button("✨ วางแผน"):
        res = call_gemini_with_retry(f"วางแผนคอนเทนต์: {topic}")
        if res: st.markdown(res)

elif menu == "💰 แคปชั่นป้ายยา":
    details = st.text_area("ข้อมูลสินค้า")
    if st.button("💸 เสกแคปชั่น"):
        res = call_gemini_with_retry(f"เขียนแคปชั่นป้ายยา: {details}")
        if res: st.code(res)

elif menu == "🔍 ตั้งชื่อคลิป":
    topic_name = st.text_input("เนื้อหาคลิป")
    if st.button("🚀 คิดชื่อ"):
        res = call_gemini_with_retry(f"คิดชื่อคลิป Viral 5 แบบ: {topic_name}")
        if res: st.markdown(res)

elif menu == "💬 ตอบคอมเมนต์":
    comment = st.text_area("คอมเมนต์")
    if st.button("💭 คิดคำตอบ"):
        res = call_gemini_with_retry(f"ตอบคอมเมนต์นี้ให้ดูน่ารัก: {comment}")
        if res: st.code(res)