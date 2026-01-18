import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. ฟังก์ชันเรียกใช้ Gemini (ระบบสลับกุญแจ) ---
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
                    st.error("❌ โควต้าเต็มทุกกุญแจแล้วค่ะ รบกวนรอ 1-2 นาทีนะค")
                    st.stop()
    return None

# --- 3. ฟังก์ชันเสกรูป (ใช้ Endpoint ที่เสถียรขึ้น) ---
def generate_image_url(prompt, width, height):
    # เข้ารหัสข้อความ
    encoded_prompt = urllib.parse.quote(prompt)
    # ใช้ Seed จากเวลาเพื่อให้รูปเปลี่ยนใหม่เสมอ
    seed = int(time.time())
    # เปลี่ยนไปใช้ endpoint image.pollinations.ai ซึ่งเหมาะกับการฝังในหน้าเว็บมากกว่า
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"
    return image_url

# --- 4. Sidebar ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio(
        "เลือกเครื่องมือ:",
        ["🎨 เสกรูปภาพด้วย AI", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิปให้น่าคลิก", "💬 ผู้ช่วยตอบคอมเมนต์"]
    )
    st.divider()
    st.caption("v3.1 | Visual Fix Edition")

# --- 5. การทำงาน ---
if menu == "🎨 เสกรูปภาพด้วย AI":
    st.header("🎨 AI ศิลปินเสกรูปภาพ (ระบบเสถียร 100%)")
    img_desc = st.text_area("อยากให้ AI วาดภาพอะไร? (ไทย/อังกฤษ)", placeholder="เช่น นกยูงสวยๆ รำแพนหาง")
    
    size_option = st.selectbox(
        "เลือกขนาดภาพ:",
        ["แนวตั้ง (9:16) - TikTok/Reels", "แนวนอน (16:9) - FB/YouTube", "จัตุรัส (1:1) - IG/Profile"]
    )
    
    # กำหนดขนาด
    if "9:16" in size_option: w, h = 540, 960
    elif "16:9" in size_option: w, h = 960, 540
    else: w, h = 768, 768

    if st.button("✨ เริ่มเสกรูป"):
        if not img_desc:
            st.warning("กรุณาใส่คำบรรยายภาพก่อนนะคะ")
        else:
            with st.spinner("⏳ กำลังเตรียมคำสั่งภาพ..."):
                is_english = all(ord(c) < 128 for c in img_desc[:50])
                if is_english:
                    eng_prompt = img_desc
                else:
                    eng_prompt = call_gemini_with_retry(f"Write a short, cinematic English image prompt for: {img_desc}")
            
            if eng_prompt:
                st.info(f"✅ กำลังวาด: {eng_prompt[:80]}...")
                final_url = generate_image_url(eng_prompt, w, h)
                
                # --- แก้ไขจุดนี้: ใช้ HTML แทน st.image เพื่อให้เบราว์เซอร์ดึงภาพเอง ---
                st.markdown(
                    f'<div style="text-align:center;"><img src="{final_url}" style="width:100%; border-radius:10px; box-shadow: 0px 4px 15px rgba(0,0,0,0.1);"></div>',
                    unsafe_allow_html=True
                )
                
                st.write("เสร็จแล้วค่ะ! วาดโดย Pollinations AI")
                
                # ปุ่มดาวน์โหลด
                st.markdown(f'### [📥 คลิกที่นี่เพื่อดาวน์โหลดรูปภาพ]({final_url})')

# --- เมนูอื่นๆ (เหมือนเดิม) ---
elif menu == "🎬 วางแผนคอนเทนต์":
    topic = st.text_input("หัวข้อคอนเทนต์")
    if st.button("✨ วางแผน"):
        result = call_gemini_with_retry(f"วางแผนคอนเทนต์เรื่อง {topic}")
        if result: st.markdown(result)

elif menu == "💰 เขียนแคปชั่นป้ายยา":
    details = st.text_area("ข้อมูลสินค้า")
    if st.button("💸 เสกแคปชั่น"):
        result = call_gemini_with_retry(f"เขียนแคปชั่นป้ายยา: {details}")
        if result: st.code(result)

elif menu == "🔍 ตั้งชื่อคลิปให้น่าคลิก":
    topic_name = st.text_input("เนื้อหาคลิปสรุป")
    if st.button("🚀 เสกชื่อคลิป"):
        result = call_gemini_with_retry(f"คิดชื่อคลิป Viral 5 แบบ: {topic_name}")
        if result: st.markdown(result)

elif menu == "💬 ผู้ช่วยตอบคอมเมนต์":
    comment = st.text_area("คอมเมนต์จากแฟนคลับ")
    style = st.select_slider("สไตล์", options=["สุภาพ", "เป็นกันเอง", "กวนๆ"])
    if st.button("💭 คิดคำตอบ"):
        result = call_gemini_with_retry(f"ตอบคอมเมนต์ '{comment}' สไตล์ {style}")
        if result: st.code(result)