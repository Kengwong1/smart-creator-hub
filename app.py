import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import io
from PIL import Image

# --- 1. ตั้งค่าและโหลดกุญแจ ---
st.set_page_config(page_title="Smart Creator Hub", page_icon="🎬", layout="wide")
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
hf_api_key = os.getenv("HUGGINGFACE_API_KEY")

# ตรวจสอบกุญแจ
if not gemini_api_key:
    st.error("❌ ไม่พบ Gemini API Key")
    st.stop()

genai.configure(api_key=gemini_api_key)
model_text = genai.GenerativeModel('gemini-flash-latest')

# API สำหรับวาดรูป
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
hf_headers = {"Authorization": f"Bearer {hf_api_key}"}

def generate_image(prompt):
    response = requests.post(HF_API_URL, headers=hf_headers, json={"inputs": prompt})
    return response.content

# --- Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub")
    st.write(f"สวัสดีค่ะคุณเก่ง")
    menu = st.radio(
        "เลือกเครื่องมือ:",
        ["🎨 เสกรูปภาพด้วย AI", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิปให้น่าคลิก", "💬 ผู้ช่วยตอบคอมเมนต์"]
    )
    st.divider()
    st.caption("v2.0 | AI Image Edition")

# --- โซน 1: เสกรูปภาพด้วย AI ---
if menu == "🎨 เสกรูปภาพด้วย AI":
    st.header("🎨 AI ศิลปินเสกรูปภาพตามสั่ง")
    img_desc = st.text_area("อยากได้ภาพอะไร? (พิมพ์ไทยได้เลย)", placeholder="เช่น แมวใส่ชุดนักบินอวกาศ สไตล์ภาพถ่าย")
    
    if st.button("✨ เสกรูปภาพ"):
        if not hf_api_key:
            st.error("กรุณาใส่ Hugging Face Token ใน Secrets ก่อนนะคะ")
        elif not img_desc:
            st.warning("บอกใบ้ AI หน่อยค่ะว่าอยากได้รูปอะไร")
        else:
            with st.spinner("⏳ กำลังแปลภาษาและวาดภาพ..."):
                # แปลไทยเป็นอังกฤษด้วย Gemini
                trans_res = model_text.generate_content(f"Translate to English for image prompt: {img_desc}")
                eng_prompt = trans_res.text
                # วาดรูป
                img_bytes = generate_image(eng_prompt)
                try:
                    image = Image.open(io.BytesIO(img_bytes))
                    st.image(image, caption="เสร็จแล้วค่ะ!", use_container_width=True)
                    # ปุ่มโหลดรูป
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("📥 ดาวน์โหลดรูปภาพ", data=buf.getvalue(), file_name="ai_img.png", mime="image/png")
                except:
                    st.error("เซิร์ฟเวอร์วาดรูปไม่ว่าง กรุณารอ 30 วิแล้วกดใหม่อีกครั้งนะคะ")

# --- โซน 2: วางแผนคอนเทนต์ ---
elif menu == "🎬 วางแผนคอนเทนต์":
    st.header("🎬 ผู้ช่วยวางแผนคอนเทนต์ทุกแพลตฟอร์ม")
    topic = st.text_input("หัวข้อคอนเทนต์")
    platform = st.selectbox("ช่องทาง", ["วิดีโอสั้น (TikTok/Reels)", "วิดีโอยาว (FB/YouTube)", "โพสต์รูปภาพ"])
    if st.button("✨ วางแผน"):
        res = model_text.generate_content(f"วางแผนคอนเทนต์เรื่อง {topic} ลง {platform} ขอละเอียดๆ")
        st.markdown(res.text)

# --- โซน 3: เขียนแคปชั่นป้ายยา ---
elif menu == "💰 เขียนแคปชั่นป้ายยา":
    st.header("💰 เขียนแคปชั่นป้ายยา Affiliate")
    details = st.text_area("จุดเด่นสินค้า")
    if st.button("💸 เสกแคปชั่น"):
        res = model_text.generate_content(f"เขียนแคปชั่นป้ายยาแรงๆ จากข้อมูลนี้: {details}")
        st.code(res.text)

# --- โซน 4: ตั้งชื่อคลิปให้น่าคลิก ---
elif menu == "🔍 ตั้งชื่อคลิปให้น่าคลิก":
    st.header("🔍 ตัวช่วยตั้งชื่อให้คนกดดู")
    topic_name = st.text_input("เนื้อหาคลิปสรุป")
    if st.button("🚀 เสกชื่อคลิป"):
        res = model_text.generate_content(f"คิดชื่อคลิป Viral 5 แบบ สำหรับเรื่อง {topic_name}")
        st.markdown(res.text)

# --- โซน 5: ผู้ช่วยตอบคอมเมนต์ ---
elif menu == "💬 ผู้ช่วยตอบคอมเมนต์":
    st.header("💬 ผู้ช่วยตอบคอมเมนต์")
    comment = st.text_area("คอมเมนต์จากแฟนคลับ")
    style = st.select_slider("สไตล์", options=["สุภาพ", "เป็นกันเอง", "กวนๆ"])
    if st.button("💭 คิดคำตอบ"):
        res = model_text.generate_content(f"คิดคำตอบคอมเมนต์ '{comment}' สไตล์ {style}")
        st.code(res.text)