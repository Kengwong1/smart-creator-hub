import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v4.6", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. สไตล์ภาพที่เน้น "ภาพถ่ายจริง" (Studio Logic) ---
STYLE_PRESETS = {
    "สไตล์ปกติ (สมจริงพื้นฐาน)": ", real human hands repairing a smartphone, macro photography, professional technician tools, authentic lighting, 8k, sharp focus on screen",
    "ช่างซ่อมยุคอวกาศ (Cyber Repair)": ", cyberpunk workshop, neon glowing circuits, hyper-detailed mechanical arms, 8k cinematic",
    "ฉากหลังสินค้า Affiliate (Studio)": ", high-end commercial photography, product on marble stand, soft lighting, blurred background, 8k",
    "ไทยโมเดิร์น (Thai Art)": ", Thai contemporary art style, elegant traditional motifs, vibrant gold and blue, masterpiece",
    "ภาพถ่ายระดับโปร (Pro Photo)": ", shot on 35mm lens, f/1.8, realistic skin textures, authentic workstation, cinematic color grading"
}

# --- 3. ระบบ AI และแปลภาษา ---
def translate_visual_master(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    # บังคับ AI ให้มองเป็นการถ่ายภาพจริง (Photography)
    prompt = f"Create a professional photography prompt for an image about: {text}. Must include 'human hands', 'realistic tools', and 'detailed hardware'. No robots."
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(prompt)
            return res.text
        except: continue
    # ตัวแปลสำรอง + คีย์เวิร์ดกันเหนียว
    try:
        translated = GoogleTranslator(source='th', target='en').translate(text)
        return translated + ", professional realistic photography, human hands working"
    except: return text

def generate_thai_content(prompt_text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(f"{prompt_text} (ตอบเป็นภาษาไทยอย่างละเอียดที่สุด)")
            return res.text
        except: continue
    return "QUOTA_FULL"

# --- 4. ฟังก์ชันสร้าง URL รูปภาพ ---
def get_img_url(prompt, width, height, style_suffix):
    full_prompt = prompt + style_suffix
    encoded = urllib.parse.quote(full_prompt)
    seed = int(time.time())
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

# --- 5. Sidebar ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v4.6")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผน & แคปชั่น"])
    st.divider()
    st.caption("v4.6 | Studio Master UI")

# --- 6. โซนการทำงาน ---
if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package (Studio Master)")
    topic = st.text_input("คุณอยากทำคอนเทนต์เรื่องอะไร?", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: chosen_style = st.selectbox("เลือกสไตล์ภาพ:", list(STYLE_PRESETS.keys()))
    with col_s2: chosen_size = st.selectbox("เลือกขนาด:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("กรุณาใส่หัวข้อค่ะ")
        else:
            with st.spinner("⏳ กำลังเสกคอนเทนต์ระดับโปรให้คุณเก่ง..."):
                text_res = generate_thai_content(f"ทำคอนเทนต์เรื่อง '{topic}': 1.ชื่อคลิป Viral 5 แบบ, 2.แคปชั่นป้ายยา Affiliate, 3.สคริปต์การถ่ายทำละเอียด")
                
                if text_res == "QUOTA_FULL":
                    st.error("โควต้าเต็ม รบกวนรอ 1 นาทีนะคะ")
                else:
                    eng_p = translate_visual_master(topic)
                    w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                    img_url = get_img_url(eng_p, w, h, STYLE_PRESETS[chosen_style])
                    
                    st.divider()
                    st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                    
                    # --- ปรับ UI ใหม่: ใช้ Container สีเข้มเพื่อคุมขนาดรูปแนวตั้งให้พอดีกรอบ ---
                    st.markdown(f"""
                        <div style="display: flex; justify-content: center; background-color: #0e1117; padding: 30px; border-radius: 20px;">
                            <div style="max-width: 450px; width: 100%; box-shadow: 0px 20px 50px rgba(0,0,0,0.5); border: 4px solid #333; border-radius: 20px; overflow: hidden;">
                                <img src="{img_url}" style="width: 100%; display: block;">
                            </div>
                        </div>
                        <div style="text-align: center; margin-top: 20px;">
                            <a href="{img_url}" target="_blank" style="padding: 12px 30px; background-color: #FF4B4B; color: white; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 18px;">📥 ดาวน์โหลดภาพหน้าปก (Full HD)</a>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)

# (ส่วนเมนูอื่นๆ ก็จะใช้มาตรฐานเดียวกันค่ะ)