import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v4.5", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. สไตล์ภาพที่เน้นความสมจริง (Visual Focus) ---
STYLE_PRESETS = {
    "สไตล์ปกติ (เน้นสมจริง)": ", professional photography, close-up shot, real-life scenario, detailed hands and tools, 8k, sharp focus",
    "ช่างซ่อมยุคอวกาศ (Cyber Repair)": ", cyberpunk style, neon circuits, intricate details, futuristic technology, 8k masterpiece",
    "ฉากหลังสินค้า Affiliate (Studio)": ", high-end product photography, soft studio lighting, minimalist stand, bokeh, commercial quality",
    "ไทยโมเดิร์น (Thai Art)": ", Thai traditional motif, elegant, vibrant colors, cultural masterpiece, high detail",
    "ภาพถ่ายระดับโปร (DSLR)": ", shot on 85mm lens, f/1.8, cinematic lighting, ultra-realistic, professional color grading"
}

# --- 3. ระบบ AI และแปลภาษา ---
def translate_visual(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    # เน้นให้ AI แปลโดยมองเป็น "ภาพเหตุการณ์"
    prompt = f"Convert this topic into a professional photographic image prompt: {text}. Focus on real actions and objects."
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(prompt)
            return res.text
        except: continue
    # ตัวแปลสำรอง
    try:
        return GoogleTranslator(source='th', target='en').translate(text) + ", professional photography, detailed"
    except: return text

def generate_thai_content(prompt_text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(f"{prompt_text} (ตอบเป็นภาษาไทยอย่างละเอียด)")
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
    st.title("🎬 Smart Creator Hub v4.5")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผน & แคปชั่น"])
    st.divider()
    st.caption("v4.5 | UI & Visual Fix")

# --- 6. โซนการทำงาน ---
if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package")
    topic = st.text_input("หัวข้อคอนเทนต์:", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: chosen_style = st.selectbox("เลือกสไตล์ภาพ:", list(STYLE_PRESETS.keys()))
    with col_s2: chosen_size = st.selectbox("เลือกขนาด:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("กรุณาใส่หัวข้อค่ะ")
        else:
            with st.spinner("⏳ กำลังปรุงคอนเทนต์ให้เป๊ะ..."):
                text_res = generate_thai_content(f"ทำคอนเทนต์เรื่อง '{topic}': 1.ชื่อคลิป Viral 5 แบบ, 2.แคปชั่นป้ายยา Affiliate, 3.สคริปต์การถ่ายทำ")
                
                if text_res == "QUOTA_FULL":
                    st.error("โควต้าเต็ม รบกวนรอ 1 นาทีนะคะ")
                else:
                    eng_p = translate_visual(topic)
                    w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                    img_url = get_img_url(eng_p, w, h, STYLE_PRESETS[chosen_style])
                    
                    st.divider()
                    st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                    
                    # --- ปรับกรอบรูปภาพใหม่ให้ดูแพงและพอดีกรอบ ---
                    st.markdown(f"""
                        <div style="display: flex; justify-content: center; background-color: #1e1e1e; padding: 20px; border-radius: 20px;">
                            <img src="{img_url}" style="max-width: 100%; max-height: 80vh; border-radius: 10px; border: 2px solid #333;">
                        </div>
                        <div style="text-align: center; margin-top: 15px;">
                            <a href="{img_url}" target="_blank" style="padding: 10px 20px; background-color: #FF4B4B; color: white; border-radius: 8px; text-decoration: none; font-weight: bold;">📥 ดาวน์โหลดภาพขนาดเต็ม</a>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)

# (ส่วนเมนูอื่นๆ ใช้ Logic แสดงผลรูปแบบเดียวกันได้เลยค่ะ)
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    st.header("🎨 AI ศิลปินเสกรูป")
    img_desc = st.text_area("อยากได้รูปอะไรคะ?")
    if st.button("✨ วาดรูป"):
        with st.spinner("🎨 กำลังวาด..."):
            eng_prompt = translate_visual(img_desc)
            # (ใส่ logic แสดงรูปเหมือนด้านบนได้เลยค่ะ)
            final_url = get_img_url(eng_prompt, 768, 768, "")
            st.image(final_url)