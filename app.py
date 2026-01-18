import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v6.2", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. คลังสไตล์ภาพระดับโปร (จูนใหม่ให้สวยทุกสไตล์) ---
STYLE_PRESETS = {
    "📸 ภาพถ่ายสมจริง (Realistic)": ", professional photography, realistic, natural lighting, 8k, sharp focus, authentic textures",
    "🎨 การ์ตูน / อนิเมะ (Anime)": ", vibrant cartoon style, anime illustration, clean lines, colorful, high quality 2D art",
    "🧸 3D แอนิเมชั่น (Pixar Style)": ", cute 3D character style, Pixar inspired, octane render, soft studio lighting, high detailed 3D",
    "🖼️ ภาพวาดดิจิทัล (Digital Art)": ", modern digital illustration, flat art style, clean vector look, professional graphic design",
    "🖌️ ภาพวาดสีน้ำมัน (Oil Painting)": ", masterpiece oil painting, visible brush strokes, rich textures, artistic lighting, classical art",
    "🚀 ไซเบอร์พังค์ (Cyberpunk)": ", futuristic style, neon glowing lights, high-tech atmosphere, cinematic dark blue and pink tones",
    "📝 ภาพสเก็ตช์ (Pencil Sketch)": ", hand-drawn pencil sketch, graphite shading, artistic drawing, paper texture, detailed lines"
}

# --- 3. ระบบ AI ---
def translate_to_visual_elements(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    instruction = """Convert this topic into a list of 5-7 physical, visible objects or actions for an image. 
    Focus on core elements. No abstract words. Output ONLY the list.
    Topic: """
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(instruction + text)
            return res.text.replace('"', '').replace("'", "").strip()
        except: continue
    return GoogleTranslator(source='th', target='en').translate(text)

def generate_thai_content(topic):
    keys = st.secrets.get("GEMINI_KEYS", [])
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(f"ทำคอนเทนต์เรื่อง '{topic}': 1.ชื่อคลิป Viral 5 แบบ, 2.แคปชั่นป้ายยา Affiliate, 3.สคริปต์การถ่ายทำ (ตอบเป็นภาษาไทย)")
            return res.text
        except: continue
    return "QUOTA_FULL"

# --- 4. ฟังก์ชันสร้าง URL รูปภาพ ---
def get_img_url(visual_elements, width, height, style_suffix):
    # ปรับปรุงโครงสร้าง URL ให้เสถียรที่สุด
    full_prompt = f"{visual_elements} {style_suffix}"
    encoded = urllib.parse.quote(full_prompt)
    seed = int(time.time())
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

# --- 5. Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v6.2")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา"])
    st.divider()
    st.caption("v6.2 | Multi-Style Engine")

# --- 6. โซนการทำงาน ---

# --- 6.1 Magic Content (ชุดใหญ่) ---
if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package (เลือกได้หลายสไตล์)")
    topic = st.text_input("คุณอยากทำคอนเทนต์เรื่องอะไร?", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: chosen_style = st.selectbox("เลือกสไตล์ภาพหน้าปก:", list(STYLE_PRESETS.keys()))
    with col_s2: chosen_size = st.selectbox("ขนาดภาพที่ต้องการ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("กรุณาใส่หัวข้อค่ะ")
        else:
            with st.spinner("⏳ กำลังเสกเนื้อหาและรูปภาพ..."):
                text_res = generate_thai_content(topic)
                if text_res == "QUOTA_FULL":
                    st.error("⚠️ โควต้าเต็ม รบกวนรอ 1 นาทีนะคะ")
                else:
                    visual_elements = translate_to_visual_elements(topic)
                    w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                    img_url = get_img_url(visual_elements, w, h, STYLE_PRESETS[chosen_style])
                    
                    st.divider()
                    st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                    if "9:16" in chosen_size:
                        c1, c2, c3 = st.columns([1, 1.2, 1])
                        with c2: st.image(img_url, use_container_width=True)
                    else:
                        st.image(img_url, use_container_width=True)
                    
                    st.markdown(f'<div style="text-align:center;"><a href="{img_url}" target="_blank" style="color:#FF4B4B; font-weight:bold; text-decoration:none;">📥 ดาวน์โหลดภาพขนาดเต็ม</a></div>', unsafe_allow_html=True)
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)

# --- 6.2 เสกรูปภาพอย่างเดียว ---
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    st.header("🎨 AI ศิลปินเสกรูปภาพ (เลือกสไตล์ได้ตามใจ)")
    img_desc = st.text_area("อยากได้รูปอะไรคะ?")
    col_a, col_b = st.columns(2)
    with col_a: style = st.selectbox("เลือกสไตล์:", list(STYLE_PRESETS.keys()))
    with col_b: size = st.selectbox("เลือกขนาด:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    
    if st.button("✨ เริ่มวาดรูป"):
        with st.spinner("🎨 กำลังบรรเลงงานศิลปะ..."):
            visual_elements = translate_to_visual_elements(img_desc)
            w, h = (540, 960) if "9:16" in size else (960, 540) if "16:9" in size else (768, 768)
            final_url = get_img_url(visual_elements, w, h, STYLE_PRESETS[style])
            
            if "9:16" in size:
                c1, c2, c3 = st.columns([1, 1.2, 1])
                with c2: st.image(final_url, use_container_width=True)
            else:
                st.image(final_url, use_container_width=True)
            st.markdown(f'[📥 ดาวน์โหลดรูปภาพ]({final_url})')