import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v5.3", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. สไตล์ภาพ (Visual Presets) ---
STYLE_PRESETS = {
    "สไตล์ปกติ (สมจริงพื้นฐาน)": ", professional photography, human hands repairing smartphone, detailed tools, 8k, sharp focus, real workplace",
    "ช่างซ่อมยุคอวกาศ (Cyber Repair)": ", cyberpunk style, neon lights, intricate mechanical parts, 8k cinematic",
    "ฉากหลังสินค้า Affiliate (Studio)": ", high-end product photo, studio lighting, marble surface, blurred background",
    "ภาพถ่ายระดับโปร (DSLR)": ", shot on 85mm lens, f/1.8, cinematic lighting, ultra-realistic texture"
}

# --- 3. ระบบ AI และแปลภาษา ---
def translate_visual(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    sys_prompt = f"Professional photography prompt: {text}. Focus on human hands and real tools. Realistic."
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(sys_prompt)
            return res.text
        except: continue
    try:
        return GoogleTranslator(source='th', target='en').translate(text) + ", photography, 8k"
    except: return text

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
    st.title("🎬 Smart Creator Hub v5.3")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio(
        "เลือกเครื่องมือ:", 
        ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิป", "💬 ตอบคอมเมนต์"]
    )
    st.divider()
    st.caption("v5.3 | Final Visual Solution")

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
                    eng_p = translate_visual(topic)
                    w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                    full_prompt = urllib.parse.quote(eng_p + STYLE_PRESETS[chosen_style])
                    # เพิ่ม Random Seed เพื่อบังคับโหลดใหม่
                    final_url = f"https://image.pollinations.ai/prompt/{full_prompt}?width={w}&height={h}&seed={int(time.time())}&nologo=true&model=flux"
                    
                    st.divider()
                    st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                    
                    # --- ใช้ HTML พิเศษเพื่อบังคับแสดงรูปภาพให้เสถียรที่สุด ---
                    st.markdown(f"""
                        <div style="display: flex; justify-content: center; background-color: #111; padding: 20px; border-radius: 15px;">
                            <div style="max-width: 450px; width: 100%;">
                                <img src="{final_url}" style="width: 100%; border-radius: 10px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5);" 
                                     alt="กำลังเสกรูปภาพ... โปรดรอสักครู่">
                            </div>
                        </div>
                        <div style="text-align: center; margin-top: 15px;">
                            <a href="{final_url}" target="_blank" style="color: #FF4B4B; font-weight: bold; text-decoration: none;">📥 คลิกเพื่อเปิดดูภาพขนาดเต็ม / ดาวน์โหลด</a>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)

elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    img_desc = st.text_area("อยากได้รูปอะไรคะ?")
    if st.button("✨ วาดรูป"):
        with st.spinner("🎨 กำลังวาด..."):
            eng_p = translate_visual(img_desc)
            final_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(eng_p)}?width=800&height=800&seed={int(time.time())}&model=flux"
            st.markdown(f'<div style="text-align:center;"><img src="{final_url}" style="max-width:100%; border-radius:10px;"></div>', unsafe_allow_html=True)
            st.markdown(f'[📥 ดาวน์โหลดรูปภาพ]({final_url})')