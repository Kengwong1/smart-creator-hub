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

# --- 3. ฟังก์ชันเสกรูป (Pollinations AI) ---
def generate_image_url(prompt, width, height):
    encoded_prompt = urllib.parse.quote(prompt)
    seed = int(time.time())
    # ใช้โมเดล flux และเพิ่ม nologo=true
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

# --- 4. Sidebar ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub")
    st.write(f"ยินดีต้อนรับค่ะ ✨")
    menu = st.radio(
        "เลือกเครื่องมือ:",
        ["🎨 เสกรูปภาพด้วย AI", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิปให้น่าคลิก", "💬 ผู้ช่วยตอบคอมเมนต์"]
    )
    st.divider()
    st.caption("v3.3 | Perfect UI Edition")

# --- 5. โซนการทำงาน ---
if menu == "🎨 เสกรูปภาพด้วย AI":
    st.header("🎨 AI ศิลปินเสกรูปภาพ")
    
    # สวิตช์เลือกโหมด
    use_ai = st.toggle("เปิดใช้ AI ช่วยแปลและแต่งภาพ (แนะนำให้เปิดไว้)", value=True)
    
    if use_ai:
        st.caption("💡 พิมพ์ไทยได้เลย เดี๋ยว AI จัดการให้")
        placeholder_txt = "เช่น หุ่นยนต์ซ่อมมือถือสีทอง แสงนีออน ในห้องแล็บล้ำสมัย"
    else:
        st.caption("⚠️ โหมด Manual: ต้องพิมพ์ภาษาอังกฤษเท่านั้น (ใช้เมื่อโควต้า AI เต็ม)")
        placeholder_txt = "e.g., golden repair robot, neon lights, futuristic lab"

    img_desc = st.text_area("คำบรรยายภาพ:", placeholder=placeholder_txt, height=100)
    
    size_option = st.selectbox("เลือกขนาดภาพ:", ["แนวตั้ง (9:16) - TikTok/Reels", "แนวนอน (16:9) - FB/YouTube", "จัตุรัส (1:1) - IG/Profile"])
    
    # กำหนดขนาด
    if "9:16" in size_option: w, h = 540, 960
    elif "16:9" in size_option: w, h = 960, 540
    else: w, h = 768, 768

    if st.button("✨ เริ่มเสกรูป"):
        if not img_desc:
            st.warning("กรุณาใส่คำบรรยายภาพก่อนนะคะ")
        else:
            eng_prompt = ""
            if use_ai:
                with st.spinner("⏳ AI กำลังช่วยแต่งคำสั่งให้ภาพสวยที่สุด..."):
                    res = call_gemini_with_retry(f"Write a highly detailed, photographic English image prompt for: {img_desc}")
                    if res == "QUOTA_FULL":
                        st.error("⚠️ โควต้า AI เต็มชั่วคราว! กรุณาปิดสวิตช์ด้านบนแล้วพิมพ์อังกฤษสั้นๆ แทนนะคะ")
                    elif res:
                        eng_prompt = res
            else:
                eng_prompt = img_desc # ใช้คำสั่งสดๆ

            if eng_prompt and eng_prompt != "QUOTA_FULL":
                with st.spinner("🎨 กำลังวาดภาพ..."):
                    final_url = generate_image_url(eng_prompt, w, h)
                    
                    st.success("✨ เสร็จแล้วค่ะ!")
                    
                    # --- ส่วนจัดหน้าจอแสดงผลใหม่ ---
                    # โค้ด HTML สำหรับแสดงรูปพร้อมเงาสวยๆ และจำกัดความสูงไม่ให้ล้นจอ
                    html_code = f'<div style="display: flex; justify-content: center; margin-bottom: 20px;"><img src="{final_url}" style="max-width: 100%; max-height: 75vh; border-radius: 12px; box-shadow: 0px 8px 20px rgba(0,0,0,0.25);"></div>'

                    if "9:16" in size_option:
                        # ถ้าเป็นแนวตั้ง ใช้เทคนิคแบ่งคอลัมน์บีบให้รูปอยู่ตรงกลาง
                        c1, c2, c3 = st.columns([1, 2, 1]) # อัตราส่วน ว่าง:รูป:ว่าง
                        with c2:
                             st.markdown(html_code, unsafe_allow_html=True)
                    else:
                        # ถ้าเป็นแนวนอนหรือจัตุรัส แสดงเต็มความกว้างได้เลย
                        st.markdown(html_code, unsafe_allow_html=True)
                    
                    # ปุ่มดาวน์โหลดแบบสวยงาม
                    st.markdown(f"""
                        <div style="text-align: center;">
                            <a href="{final_url}" target="_blank" style="display: inline-block; padding: 12px 24px; background-color: #FF4B4B; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
                                📥 ดาวน์โหลดรูปภาพขนาดเต็มไฟล์
                            </a>
                        </div>
                    """, unsafe_allow_html=True)

# --- เมนูอื่นๆ (คงเดิม) ---
elif menu == "🎬 วางแผนคอนเทนต์":
    topic = st.text_input("หัวข้อคอนเทนต์")
    if st.button("✨ วางแผน"):
        res = call_gemini_with_retry(f"วางแผนคอนเทนต์เรื่อง {topic}")
        if res and res != "QUOTA_FULL": st.markdown(res)
        elif res == "QUOTA_FULL": st.error("โควต้าเต็ม รอสักครู่นะคะ")

elif menu == "💰 เขียนแคปชั่นป้ายยา":
    details = st.text_area("ข้อมูลสินค้า")
    if st.button("💸 เสกแคปชั่น"):
        res = call_gemini_with_retry(f"เขียนแคปชั่นป้ายยา: {details}")
        if res and res != "QUOTA_FULL": st.code(res)
        elif res == "QUOTA_FULL": st.error("โควต้าเต็ม รอสักครู่นะคะ")

elif menu == "🔍 ตั้งชื่อคลิปให้น่าคลิก":
    topic_name = st.text_input("เนื้อหาคลิปสรุป")
    if st.button("🚀 เสกชื่อคลิป"):
        res = call_gemini_with_retry(f"คิดชื่อคลิป Viral 5 แบบ: {topic_name}")
        if res and res != "QUOTA_FULL": st.markdown(res)
        elif res == "QUOTA_FULL": st.error("โควต้าเต็ม รอสักครู่นะคะ")

elif menu == "💬 ผู้ช่วยตอบคอมเมนต์":
    comment = st.text_area("คอมเมนต์จากแฟนคลับ")
    style = st.select_slider("สไตล์", options=["สุภาพ", "เป็นกันเอง", "กวนๆ"])
    if st.button("💭 คิดคำตอบ"):
        res = call_gemini_with_retry(f"ตอบคอมเมนต์ '{comment}' สไตล์ {style}")
        if res and res != "QUOTA_FULL": st.code(res)
        elif res == "QUOTA_FULL": st.error("โควต้าเต็ม รอสักครู่นะคะ")