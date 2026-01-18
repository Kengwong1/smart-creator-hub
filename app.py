import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v6.4", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. คลังสไตล์ภาพ (v6.4 ปรับจูนเพื่อลดความเพี้ยน) ---
# เพิ่มคีย์เวิร์ดป้องกันภาพเบี้ยว (Negative Prompts ในตัว)
NEGATIVE_PROMPT = "deformed, distorted, extra fingers, mutated hands, messy, blurry, low quality, grainy, out of focus"

STYLE_PRESETS = {
    "📸 ภาพถ่ายสมจริง (Realistic)": f", professional macro photography, real human hands, smartphone repair, clean tools, sharp focus, 8k, authentic lighting, stable shapes, {NEGATIVE_PROMPT}",
    "🎨 การ์ตูน / อนิเมะ (Anime)": f", vibrant anime style, clean lines, high quality 2D art, {NEGATIVE_PROMPT}",
    "🧸 3D แอนิเมชั่น (Pixar Style)": f", cute 3D character style, Pixar inspired, octane render, soft studio lighting, high detailed 3D, {NEGATIVE_PROMPT}",
    "🖼️ ภาพวาดดิจิทัล (Digital Art)": f", modern digital illustration, flat art style, professional vector look, {NEGATIVE_PROMPT}",
    "🖌️ ภาพวาดสีน้ำมัน (Oil Painting)": f", masterpiece oil painting, brush strokes, artistic lighting, {NEGATIVE_PROMPT}",
    "🚀 ไซเบอร์พังค์ (Cyberpunk)": f", futuristic neon lights, tech atmosphere, cinematic colors, {NEGATIVE_PROMPT}",
    "📝 ภาพสเก็ตช์ (Pencil Sketch)": f", hand-drawn pencil sketch, graphite shading, paper texture, detailed lines, {NEGATIVE_PROMPT}"
}

# --- 3. ระบบ AI ---
def translate_to_visual_elements(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    # สั่งให้ AI ลิสต์ของให้น้อยลงแต่ชัดเจนขึ้น เพื่อลดความมั่วของภาพ
    instruction = """Convert this topic into a SIMPLE list of 3-4 physical objects. 
    Be very specific and simple. NO ABSTRACT WORDS. Output ONLY the list.
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
            res = model.generate_content(f"ทำคอนเทนต์เรื่อง '{topic}': 1.ชื่อคลิป Viral 5 แบบ, 2.แคปชั่นป้ายยา Affiliate, 3.สคริปต์การถ่ายทำ (ตอบเป็นภาษาไทยอย่างละเอียด)")
            return res.text
        except: continue
    return "QUOTA_FULL"

# --- 4. ฟังก์ชันสร้าง URL รูปภาพ ---
def get_img_url(visual_elements, width, height, style_suffix):
    full_prompt = f"A professional photo of {visual_elements} {style_suffix}"
    encoded = urllib.parse.quote(full_prompt)
    seed = int(time.time())
    # เน้น Model: Flux ซึ่งเสถียรกว่ารุ่นเก่าๆ
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

# --- 5. Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v6.4")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา"])
    st.divider()
    st.caption("v6.4 | Clean Focus Update")

# --- 6. โซนการทำงาน ---

if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content (เน้นภาพสะอาด ไม่เพี้ยน)")
    topic = st.text_input("คุณอยากทำคอนเทนต์เรื่องอะไร?", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: chosen_style = st.selectbox("เลือกสไตล์ภาพหน้าปก:", list(STYLE_PRESETS.keys()))
    with col_s2: chosen_size = st.selectbox("ขนาดภาพที่ต้องการ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("กรุณาใส่หัวข้อค่ะ")
        else:
            with st.spinner("⏳ กำลังเสกเนื้อหาและปรับจูนรูปภาพให้เป๊ะ..."):
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
                        with c2: st.image(img_url, use_container_width=True, caption="ระบบปรับจูนความคมชัดและลดความเพี้ยนแล้วค่ะ")
                    else:
                        st.image(img_url, use_container_width=True, caption="ระบบปรับจูนความคมชัดและลดความเพี้ยนแล้วค่ะ")
                    
                    st.markdown(f'<div style="text-align:center;"><a href="{img_url}" target="_blank" style="color:#FF4B4B; font-weight:bold; text-decoration:none;">📥 ดาวน์โหลดภาพขนาดเต็ม</a></div>', unsafe_allow_html=True)
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)

# (หมวดอื่นๆ คงเดิม)