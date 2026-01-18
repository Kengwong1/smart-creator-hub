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
    # ดึงรายการกุญแจจาก Secrets (ต้องตั้งค่าในหน้าเว็บ Streamlit)
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
            # ถ้าโควต้าเต็ม (429) ให้ลองกุญแจดอกถัดไป
            if "429" in str(e) or "ResourceExhausted" in str(e):
                if idx < len(keys) - 1:
                    st.warning(f"⚠️ กุญแจดอกที่ {idx+1} เต็ม กำลังสลับไปใช้ดอกที่ {idx+2} ค่ะ")
                    time.sleep(2)
                    continue
                else:
                    st.error("❌ กุญแจทุกดอกโควต้าเต็มหมดแล้วค่ะ รบกวนรอ 1-2 นาทีนะคะ")
                    st.stop()
            else:
                st.error(f"เกิดข้อผิดพลาดที่ Gemini: {e}")
                st.stop()

# --- 3. ฟังก์ชันเสกรูปพร้อมระบบ Auto-Retry และขนาดภาพ ---
def generate_image_logic(prompt, width, height, hf_key, max_retries=5):
    # ใช้ Stable Diffusion 2.1 ที่เสถียรและเสกภาพ Cinematic สวยค่ะ
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
    headers = {"Authorization": f"Bearer {hf_key}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": width, 
            "height": height,
            "negative_prompt": "blurry, bad anatomy, low quality, distorted"
        }
    }
    
    for i in range(max_retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                return response.content
            elif response.status_code == 503:
                st.info(f"⏳ เซิร์ฟเวอร์กำลังเตรียมตัว... กำลังลองใหม่ครั้งที่ {i+1}/{max_retries} (รอ 10 วิ)")
                time.sleep(10)
            elif response.status_code == 410:
                st.error("❌ โมเดลนี้ปิดบริการชั่วคราวบน API ฟรีค่ะ")
                st.stop()
            else:
                st.error(f"❌ Hugging Face Error: {response.status_code}")
                st.stop()
        except requests.exceptions.RequestException as e:
            st.warning(f"⚠️ การเชื่อมต่อติดขัด กำลังลองใหม่... ({e})")
            time.sleep(5)
            
    raise Exception("เซิร์ฟเวอร์ไม่ว่างนานเกินไปค่ะ")

# --- 4. Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio(
        "เลือกเครื่องมือ:",
        ["🎨 เสกรูปภาพด้วย AI", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิปให้น่าคลิก", "💬 ผู้ช่วยตอบคอมเมนต์"]
    )
    st.divider()
    st.caption("v2.6 | Stable Release")

# --- 5. โซนการทำงานตามเมนู ---

# --- เมนู: เสกรูปภาพ ---
if menu == "🎨 เสกรูปภาพด้วย AI":
    st.header("🎨 AI ศิลปินเสกรูปภาพ (v2.6)")
    img_desc = st.text_area("อยากให้ AI วาดภาพอะไร? (พิมพ์ไทยได้เลย)", placeholder="เช่น หุ่นยนต์ซ่อมมือถือในโลกอนาคต แสงนีออน")
    
    col1, col2 = st.columns(2)
    with col1:
        size_option = st.selectbox(
            "เลือกขนาดภาพ:",
            ["แนวตั้ง (9:16) - TikTok/Reels", "แนวนอน (16:9) - FB/YouTube", "จัตุรัส (1:1) - IG/Profile"]
        )
    
    # ปรับขนาดให้เหมาะกับ SD 2.1 (768 เป็นค่ามาตรฐานที่ภาพสวยค่ะ)
    if "9:16" in size_option: w, h = 512, 896
    elif "16:9" in size_option: w, h = 896, 512
    else: w, h = 768, 768

    if st.button("✨ เริ่มเสกรูป"):
        hf_api_key = st.secrets.get("HUGGINGFACE_API_KEY")
        if not img_desc:
            st.warning("กรุณาใส่คำบรรยายภาพก่อนค่ะ")
        elif not hf_api_key:
            st.error("ไม่พบ Hugging Face API Key ใน Secrets ค่ะ")
        else:
            # 1. แปลภาษาและขยาย Prompt ด้วย Gemini
            with st.spinner("⏳ กำลังเตรียมคำสั่งภาษาอังกฤษระดับโปร..."):
                eng_prompt = call_gemini_with_retry(f"Generate a detailed, cinematic English image generation prompt for: {img_desc}")
                st.info(f"✅ Prompt: {eng_prompt}")
            
            # 2. ส่งไปวาดรูป
            with st.spinner("🎨 กำลังวาดรูป... (อาจใช้เวลา 10-30 วินาที)"):
                try:
                    img_bytes = generate_image_logic(eng_prompt, w, h, hf_api_key)
                    image = Image.open(io.BytesIO(img_bytes))
                    st.image(image, caption=f"เสร็จแล้วค่ะ! ขนาด {size_option}", use_container_width=True)
                    
                    # ปุ่มดาวน์โหลด
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("📥 ดาวน์โหลดรูปภาพ", data=buf.getvalue(), file_name="ai_creator_image.png", mime="image/png")
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")

# --- เมนูอื่นๆ (ระบบสลับกุญแจทำงานพื้นหลัง) ---
elif menu == "🎬 วางแผนคอนเทนต์":
    st.header("🎬 วางแผนคอนเทนต์")
    topic = st.text_input("หัวข้อที่ต้องการ")
    if st.button("✨ วางแผน"):
        with st.spinner("กำลังคิดแผน..."):
            result = call_gemini_with_retry(f"วางแผนคอนเทนต์เรื่อง {topic} อย่างละเอียด")
            st.markdown(result)

elif menu == "💰 เขียนแคปชั่นป้ายยา":
    st.header("💰 เขียนแคปชั่นป้ายยา")
    details = st.text_area("ข้อมูลสินค้า")
    if st.button("💸 เสกแคปชั่น"):
        with st.spinner("กำลังเขียน..."):
            result = call_gemini_with_retry(f"เขียนแคปชั่นป้ายยาแรงๆ จากข้อมูลนี้: {details}")
            st.code(result)

elif menu == "🔍 ตั้งชื่อคลิปให้น่าคลิก":
    st.header("🔍 ตั้งชื่อคลิป")
    topic_name = st.text_input("เนื้อหาคลิป")
    if st.button("🚀 คิดชื่อ"):
        with st.spinner("กำลังคิดชื่อ..."):
            result = call_gemini_with_retry(f"คิดชื่อคลิป Viral 5 แบบ สำหรับเรื่อง {topic_name}")
            st.markdown(result)

elif menu == "💬 ผู้ช่วยตอบคอมเมนต์":
    st.header("💬 ผู้ช่วยตอบคอมเมนต์")
    comment = st.text_area("คอมเมนต์")
    style = st.select_slider("สไตล์", options=["สุภาพ", "เป็นกันเอง", "กวนๆ"])
    if st.button("💭 คิดคำตอบ"):
        with st.spinner("กำลังหาคำตอบ..."):
            result = call_gemini_with_retry(f"ตอบคอมเมนต์ '{comment}' ในสไตล์ {style}")
            st.code(result)