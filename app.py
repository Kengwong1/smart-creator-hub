import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v5.2", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. สไตล์ภาพ (Visual Presets) ---
STYLE_PRESETS = {
    "สไตล์ปกติ (สมจริงพื้นฐาน)": ", professional photography, human hands repairing smartphone, detailed tools, macro lens, 8k, sharp focus, authentic workshop, no robots",
    "ช่างซ่อมยุคอวกาศ (Cyber Repair)": ", cyberpunk style, neon lights, intricate mechanical parts, 8k cinematic",
    "ฉากหลังสินค้า Affiliate (Studio)": ", high-end product photo, studio lighting, marble surface, blurred background",
    "ไทยโมเดิร์น (Thai Art)": ", Thai traditional pattern, gold and silk textures, elegant, 8k"
}

# --- 3. ระบบ AI และแปลภาษา ---
def translate_visual(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    # บังคับ Gemini ให้เขียน Prompt ที่เน้น "มือคน" และ "ความจริง"
    sys_prompt = f"Professional photography prompt for: {text}. Must focus on 'real human hands' and 'repairing actions'. Photorealistic style."
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(sys_prompt)
            return res.text
        except: continue
    return GoogleTranslator(source='th', target='en').translate(text) + ", professional photography, real human hands"

def generate_thai_content(prompt_text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(f"{prompt_text} (ตอบภาษาไทยอย่างละเอียด)")
            return res.text
        except: continue
    return "QUOTA_FULL"

# --- 4. Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v5.2")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio(
        "เลือกเครื่องมือ:", 
        ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิปให้น่าคลิก", "💬 ผู้ช่วยตอบคอมเมนต์"]
    )
    st.divider()
    st.caption("v5.2 | Reverting to High Stability")

# --- 5. โซนการทำงาน ---
if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package")
    topic = st.text_input("หัวข้อคอนเทนต์:", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: chosen_style = st.selectbox("เลือกสไตล์ภาพ:", list(STYLE_PRESETS.keys()))
    with col_s2: chosen_size = st.selectbox("เลือกขนาด:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("ใส่หัวข้อก่อนนะคะ")
        else:
            with st.spinner("⏳ กำลังเตรียมเนื้อหาภาษาไทย..."):
                text_res = generate_thai_content(f"ทำคอนเทนต์เรื่อง '{topic}': 1.ชื่อคลิป Viral 5 แบบ, 2.แคปชั่นป้ายยา Affiliate, 3.สคริปต์การถ่ายทำ")
                
                if text_res == "QUOTA_FULL":
                    st.error("โควต้าเต็ม รบกวนรอ 1 นาทีนะคะ")
                else:
                    # สร้าง URL สำหรับรูปภาพ (แบบยิงตรงเหมือนเวอร์ชันเก่าที่เคยสำเร็จ)
                    eng_p = translate_visual(topic)
                    w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                    full_prompt = urllib.parse.quote(eng_p + STYLE_PRESETS[chosen_style])
                    final_url = f"https://image.pollinations.ai/prompt/{full_prompt}?width={w}&height={h}&seed={int(time.time())}&model=flux"
                    
                    st.divider()
                    st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                    
                    # --- การจัดวางรูปภาพแบบใหม่ (บีบระยะและใช้สีพื้นหลังเพื่อความสวยงาม) ---
                    if "9:16" in chosen_size:
                        c1, c2, c3 = st.columns([1, 1.2, 1]) # บีบคอลัมน์กลางให้แคบลงเพื่อความพอดี
                        with c2:
                            st.image(final_url, caption="📸 กำลังโหลดรูปภาพ...", use_container_width=True)
                    else:
                        st.image(final_url, caption="📸 กำลังโหลดรูปภาพ...", use_container_width=True)
                    
                    st.markdown(f'<div style="text-align:center;"><a href="{final_url}" target="_blank" style="color:#FF4B4B; font-weight:bold; text-decoration:none;">📥 ดาวน์โหลดรูปภาพขนาดเต็ม</a></div>', unsafe_allow_html=True)
                    
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)

# (เมนูอื่นๆ ใช้หลักการแสดงผลแบบเดียวกันเพื่อให้เสถียรค่ะ)
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    st.header("🎨 AI ศิลปินเสกรูป")
    img_desc = st.text_area("อยากได้รูปอะไรคะ?")
    if st.button("✨ เริ่มวาดรูป"):
        with st.spinner("🎨 กำลังวาด..."):
            eng_p = translate_visual(img_desc)
            final_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(eng_p)}?width=768&height=768&seed={int(time.time())}&model=flux"
            st.image(final_url, use_container_width=True)
            st.markdown(f'[📥 ดาวน์โหลดรูปภาพ]({final_url})')

# (เมนูวางแผน, แคปชั่น, ตั้งชื่อ, ตอบคอมเมนต์ คงเดิม)