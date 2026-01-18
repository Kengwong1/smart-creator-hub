import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v5.4", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. สไตล์ภาพ (Visual Presets) ---
STYLE_PRESETS = {
    "สไตล์ปกติ (สมจริงพื้นฐาน)": ", professional photography, human hands repairing smartphone, detailed tools, 8k, sharp focus, authentic workshop",
    "ช่างซ่อมยุคอวกาศ (Cyber Repair)": ", cyberpunk style, neon lights, intricate mechanical parts, 8k cinematic",
    "ฉากหลังสินค้า Affiliate (Studio)": ", high-end product photo, studio lighting, marble surface, blurred background",
    "ภาพถ่ายระดับโปร (DSLR)": ", shot on 85mm lens, f/1.8, cinematic lighting, ultra-realistic texture"
}

# --- 3. ระบบ AI และแปลภาษา ---
def translate_visual(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    sys_prompt = f"Professional photography prompt for: {text}. Must include 'real human hands' and 'repairing tools'. Photorealistic style."
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
            res = model.generate_content(f"{prompt_text} (โปรดตอบเป็นภาษาไทยอย่างละเอียด)")
            return res.text
        except: continue
    return "QUOTA_FULL"

# --- 4. Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v5.4")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผน & แคปชั่น"])
    st.divider()
    st.caption("v5.4 | Resilience Edition")

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
                    # เก็บเนื้อหาไว้ใน Session เพื่อให้กดโหลดรูปใหม่ได้โดยเนื้อหาไม่หาย
                    st.session_state['last_topic'] = topic
                    st.session_state['last_text'] = text_res
                    st.session_state['last_style'] = chosen_style
                    st.session_state['last_size'] = chosen_size
                    st.session_state['seed'] = int(time.time())

    # ส่วนแสดงผล (ถ้ามีเนื้อหาใน Session)
    if 'last_text' in st.session_state:
        st.divider()
        st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
        
        # สร้าง URL รูปภาพ
        eng_p = translate_visual(st.session_state['last_topic'])
        w, h = (540, 960) if "9:16" in st.session_state['last_size'] else (960, 540) if "16:9" in st.session_state['last_size'] else (768, 768)
        encoded = urllib.parse.quote(eng_p + STYLE_PRESETS[st.session_state['last_style']])
        final_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&seed={st.session_state['seed']}&nologo=true"
        
        # แสดงรูปภาพด้วย HTML เพื่อความอึด
        st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: center; background-color: #0e1117; padding: 20px; border-radius: 15px;">
                <div style="max-width: 400px; width: 100%; text-align: center;">
                    <img src="{final_url}" style="width: 100%; border-radius: 10px; border: 2px solid #333;" alt="🎨 กำลังเสกรูปภาพ... หากนานเกิน 10 วินาที โปรดกดปุ่มโหลดใหม่ด้านล่างนะคะ">
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔄 ไม่เห็นรูป? กดโหลดใหม่อีกครั้ง"):
                st.session_state['seed'] = int(time.time()) + 1 # เปลี่ยน Seed เพื่อบังคับโหลดใหม่
                st.rerun()
        with col_btn2:
            st.markdown(f'<div style="margin-top:10px;"><a href="{final_url}" target="_blank" style="color:#FF4B4B; font-weight:bold; text-decoration:none;">📥 ดาวน์โหลดภาพขนาดเต็ม</a></div>', unsafe_allow_html=True)

        st.divider()
        st.subheader("📝 รายละเอียดคอนเทนต์")
        st.markdown(st.session_state['last_text'])

# (ส่วนเมนูอื่นๆ ปรับปรุงให้มีระบบ Session คล้ายกันได้ค่ะ)