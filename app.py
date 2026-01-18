import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v6.1", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. สูตรลับภาพสวยสมจริง (ปรับปรุงใหม่ให้เข้มข้นขึ้น) ---
# เพิ่มคำว่า "natural light", "photorealistic", "cinematic shading" เพื่อลดความเพี้ยน
PRO_PHOTO_SUFFIX = ", professional photography, real human hands working, smartphone repair tools, macro shot, photorealistic, authentic workshop environment, natural lighting, cinematic shading, 8k, sharp focus, NO ROBOTS, NO CGI, NO DISTORTION"

STYLE_PRESETS = {
    "สไตล์ปกติ (ช่างซ่อมสมจริง)": PRO_PHOTO_SUFFIX,
    "ภาพถ่ายระดับโปร (Macro)": ", extreme macro shot of internal phone components, realistic metal textures, shallow depth of field, natural light, NO ROBOTS",
    "ฉากหลังสินค้า Affiliate": ", high-end product photography on a minimalist wooden desk, soft window light, bokeh background, 8k",
    "ไทยโมเดิร์น": ", Thai local repair shop, bustling atmosphere, warm realistic lighting, documentary photograph style"
}

# --- 3. ระบบ AI (หัวใจสำคัญของการแก้ภาพเพี้ยน) ---
def translate_to_visual_elements(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    # คำสั่งใหม่: บังคับให้ลิสต์เฉพาะสิ่งที่ตาเห็น ห้ามใส่นามธรรม
    instruction = """Your task: List physical, visible objects and actions for a realistic photograph based on the user's topic.
    Rules:
    1. ONLY use concrete nouns and verbs (e.g., "technician holding screwdriver," "broken iPhone screen on mat").
    2. DO NOT use abstract words (e.g., "amazing repair," "conceptual").
    3. Output ONLY the list, no intro sentence.
    Topic: """
    
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(instruction + text)
            # ล้างข้อความให้สะอาดที่สุด
            clean_text = res.text.replace('"', '').replace("'", "").replace("-", "").strip()
            return clean_text
        except: continue
    # ตัวสำรอง
    return GoogleTranslator(source='th', target='en').translate(text)

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

# --- 4. ฟังก์ชันสร้าง URL รูปภาพ (เพิ่ม Prefix บังคับภาพถ่าย) ---
def get_img_url(visual_elements, width, height, style_suffix):
    # ใส่คำนำหน้าว่า "A detailed photograph of" เพื่อบังคับสไตล์ตั้งแต่ต้น
    full_prompt = f"A detailed photograph of {visual_elements} {style_suffix}"
    encoded = urllib.parse.quote(full_prompt)
    seed = int(time.time())
    # เพิ่ม quality=100 เพื่อขอคุณภาพสูงสุด
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model=flux&quality=100"

# --- 5. Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v6.1")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา"])
    st.divider()
    st.caption("v6.1 | Pure Photography Fix")

# --- 6. โซนการทำงาน ---

# --- 6.1 Magic Content (ชุดใหญ่) ---
if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package (ภาพสมจริง ไม่เพี้ยน)")
    topic = st.text_input("คุณอยากทำคอนเทนต์เรื่องอะไร?", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: chosen_style = st.selectbox("เลือกสไตล์ภาพหน้าปก:", list(STYLE_PRESETS.keys()))
    with col_s2: chosen_size = st.selectbox("ขนาดภาพที่ต้องการ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("กรุณาใส่หัวข้อค่ะ")
        else:
            with st.spinner("⏳ กำลังเสกเนื้อหาและภาพถ่ายคุณภาพสูง..."):
                # 1. คิดเนื้อหา
                text_res = generate_thai_content(f"ทำคอนเทนต์เรื่อง '{topic}': 1.ชื่อคลิป Viral 5 แบบ, 2.แคปชั่นป้ายยา Affiliate, 3.สคริปต์การถ่ายทำ")
                
                if text_res == "QUOTA_FULL":
                    st.error("⚠️ โควต้า Gemini เต็มค่ะ รบกวนรอ 1 นาทีนะคะ")
                else:
                    # 2. เสกรูปภาพ (ใช้ Logic ใหม่ที่บังคับความสมจริง)
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

# --- 6.2 เสกรูปภาพอย่างเดียว (อัปเกรดให้ใช้ Logic ใหม่ด้วย) ---
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    st.header("🎨 AI ศิลปินเสกรูปภาพ (โหมดภาพถ่ายสมจริง)")
    img_desc = st.text_area("อยากได้รูปอะไรคะ?")
    col_a, col_b = st.columns(2)
    with col_a: style = st.selectbox("เลือกสไตล์:", list(STYLE_PRESETS.keys()))
    with col_b: size = st.selectbox("เลือกขนาด:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    
    if st.button("✨ เริ่มวาดรูป"):
        with st.spinner("🎨 กำลังวาดภาพถ่าย..."):
            visual_elements = translate_to_visual_elements(img_desc)
            w, h = (540, 960) if "9:16" in size else (960, 540) if "16:9" in size else (768, 768)
            final_url = get_img_url(visual_elements, w, h, STYLE_PRESETS[style])
            
            if "9:16" in size:
                c1, c2, c3 = st.columns([1, 1.2, 1])
                with c2: st.image(final_url, use_container_width=True)
            else:
                st.image(final_url, use_container_width=True)
            st.markdown(f'[📥 ดาวน์โหลดรูปภาพ]({final_url})')