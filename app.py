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
        return None
    
    for idx, key in enumerate(keys):
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(prompt_text)
            return response.text
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                if idx < len(keys) - 1:
                    time.sleep(3)
                    continue
    return "QUOTA_FULL"

# --- 3. ฟังก์ชันเสกรูป (ใช้ Endpoint ที่เสถียรที่สุด) ---
def generate_image_url(prompt, width, height):
    encoded_prompt = urllib.parse.quote(prompt)
    seed = int(time.time())
    # ใช้โมเดล flux เพื่อความสวยงามระดับพรีเมียม
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

# --- 4. Sidebar ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub")
    st.write(f"ยินดีต้อนรับค่ะคุณเก่ง ✨")
    menu = st.radio(
        "เลือกเครื่องมือ:",
        ["🎨 เสกรูปภาพด้วย AI", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิปให้น่าคลิก", "💬 ผู้ช่วยตอบคอมเมนต์"]
    )
    st.divider()
    st.caption("v3.2 | Never-Stop Edition")

# --- 5. โซนการทำงาน ---
if menu == "🎨 เสกรูปภาพด้วย AI":
    st.header("🎨 AI ศิลปินเสกรูปภาพ")
    
    # --- ปุ่มเลือกโหมดการทำงาน ---
    use_ai = st.toggle("ให้ AI ช่วยแปลและแต่งคำสั่งให้สวยขึ้น (ใช้โควต้า Gemini)", value=True)
    
    img_desc = st.text_area("อยากให้ AI วาดภาพอะไร?", placeholder="เช่น หุ่นยนต์ซ่อมมือถือสีทอง / robotic golden repairman", height=100)
    
    size_option = st.selectbox("เลือกขนาดภาพ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    if "9:16" in size_option: w, h = 540, 960
    elif "16:9" in size_option: w, h = 960, 540
    else: w, h = 768, 768

    if st.button("✨ เริ่มเสกรูป"):
        if not img_desc:
            st.warning("กรุณาใส่คำบรรยายภาพก่อนนะคะ")
        else:
            eng_prompt = ""
            if use_ai:
                with st.spinner("⏳ Gemini กำลังช่วยแต่งคำสั่งให้สวยขึ้น..."):
                    res = call_gemini_with_retry(f"Write a very short, high-quality English image prompt for: {img_desc}")
                    if res == "QUOTA_FULL":
                        st.error("⚠️ โควต้า Gemini เต็มชั่วคราวค่ะ! แนะนำให้ 'ปิดปุ่มใช้ AI' ด้านบน แล้วพิมพ์ภาษาอังกฤษสั้นๆ แทนนะคะ")
                    else:
                        eng_prompt = res
            else:
                # ถ้าไม่ใช้ AI ให้ใช้ข้อความที่ผู้ใช้พิมพ์มาตรงๆ เลย
                eng_prompt = img_desc
                st.info("💡 โหมด Manual: ส่งคำสั่งโดยตรงไม่ใช้โควต้า AI ค่ะ")

            if eng_prompt and eng_prompt != "QUOTA_FULL":
                st.success(f"✅ กำลังวาด: {eng_prompt[:80]}...")
                final_url = generate_image_url(eng_prompt, w, h)
                
                # แสดงผลรูปภาพ
                st.markdown(
                    f'<div style="text-align:center;"><img src="{final_url}" style="width:100%; border-radius:10px; box-shadow: 0px 4px 15px rgba(0,0,0,0.2);"></div>',
                    unsafe_allow_html=True
                )
                
                st.markdown(f'### [📥 คลิกที่นี่เพื่อดาวน์โหลดรูปภาพ]({final_url})')

# --- เมนูอื่นๆ (เพิ่มระบบดัก Error โควต้า) ---
elif menu == "🎬 วางแผนคอนเทนต์":
    topic = st.text_input("หัวข้อคอนเทนต์")
    if st.button("✨ วางแผน"):
        res = call_gemini_with_retry(f"วางแผนคอนเทนต์เรื่อง {topic}")
        if res == "QUOTA_FULL": st.error("โควต้าเต็ม รบกวนรอ 1 นาทีนะคะ")
        elif res: st.markdown(res)
# (เมนูอื่นๆ ใส่ logic เดียวกันนี้ได้เลยค่ะ)