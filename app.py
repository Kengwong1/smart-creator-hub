import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v5.6", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. ชุดคีย์เวิร์ดมาตรฐาน (ตัวเดียวกับหมวดเสกรูปที่ภาพสวย) ---
# เราจะใช้ชุดนี้ร่วมกันทั้งแอปเพื่อให้ภาพออกมาคุณภาพเดียวกันค่ะ
PRO_PHOTO_SUFFIX = ", professional photography, real human hands, smartphone repair tools, macro shot, highly detailed, 8k, sharp focus, authentic workshop, NO ROBOTS"

STYLE_PRESETS = {
    "สไตล์ปกติ (ช่างซ่อมสมจริง)": PRO_PHOTO_SUFFIX,
    "ภาพถ่ายระดับโปร (Macro)": ", high-detail macro shot, internal phone hardware, realistic textures, cinematic lighting, NO ROBOTS",
    "ฉากหลังสินค้า Affiliate": ", high-end product photography, smartphone on minimalist desk, soft light, bokeh, 8k",
    "ไทยโมเดิร์น": ", Thai local repair shop atmosphere, realistic, 8k"
}

# --- 3. ระบบ AI และการแปลภาษา (ตัวรับงานหลัก) ---
def translate_to_pro_prompt(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    # บังคับให้ AI แปลเป็น "คำสั่งสำหรับถ่ายภาพหน้าปกคอนเทนต์จริง"
    instruction = "Convert this topic into a professional photography prompt for a YouTube thumbnail. Focus on REAL HUMAN HANDS and REPAIR TOOLS. No sci-fi, no robots. Topic: "
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(instruction + text)
            return res.text
        except: continue
    return GoogleTranslator(source='th', target='en').translate(text) + PRO_PHOTO_SUFFIX

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

# --- 4. ฟังก์ชันสร้าง URL รูปภาพ ---
def get_img_url(prompt, width, height, style_suffix):
    full_prompt = prompt + style_suffix
    encoded = urllib.parse.quote(full_prompt)
    seed = int(time.time())
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

# --- 5. Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v5.6")
    st.write(f"ยินดีต้อนรับค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา"])
    st.divider()
    st.caption("v5.6 | Synchronized Image Engine")

# --- 6. โซนการทำงาน ---

# --- 6.1 Magic Content (ชุดใหญ่) ---
if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package (ภาพสวยมาตรฐานช่าง)")
    topic = st.text_input("คุณอยากทำคอนเทนต์เรื่องอะไร?", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: chosen_style = st.selectbox("เลือกสไตล์ภาพหน้าปก:", list(STYLE_PRESETS.keys()))
    with col_s2: chosen_size = st.selectbox("ขนาดภาพที่ต้องการ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("กรุณาใส่หัวข้อคอนเทนต์ค่ะ")
        else:
            with st.spinner("⏳ กำลังใช้ระบบเสกรูปตัวท็อปผลิตงานให้คุณเก่ง..."):
                # ส่วนเนื้อหา
                text_res = generate_thai_content(f"ทำคอนเทนต์เรื่อง '{topic}': 1.ชื่อคลิป Viral 5 แบบ, 2.แคปชั่นป้ายยา Affiliate, 3.สคริปต์การถ่ายทำ")
                
                if text_res == "QUOTA_FULL":
                    st.error("⚠️ โควต้า Gemini เต็มค่ะ รบกวนรอ 1 นาทีนะคะ")
                else:
                    # ส่วนรูปภาพ (ดึงเอา Logic ของหมวดเสกรูปมาใช้ตรงๆ เลยค่ะ)
                    eng_p = translate_to_pro_prompt(topic)
                    w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                    img_url = get_img_url(eng_p, w, h, STYLE_PRESETS[chosen_style])
                    
                    st.divider()
                    st.subheader("🖼️ ภาพหน้าปกคอนเทนต์ (เสกด้วยระบบเดียวกับหมวดรูปภาพ)")
                    if "9:16" in chosen_size:
                        c1, c2, c3 = st.columns([1, 1.2, 1])
                        with c2: st.image(img_url, use_container_width=True)
                    else: st.image(img_url, use_container_width=True)
                    
                    st.markdown(f'<div style="text-align:center;"><a href="{img_url}" target="_blank" style="color:#FF4B4B; font-weight:bold; text-decoration:none;">📥 ดาวน์โหลดภาพหน้าปก</a></div>', unsafe_allow_html=True)
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)

# --- 6.2 เสกรูปภาพอย่างเดียว ---
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    st.header("🎨 AI ศิลปินเสกรูปภาพ (หมวดภาพสวยต้นแบบ)")
    img_desc = st.text_area("อยากได้รูปอะไรคะ?")
    col_a, col_b = st.columns(2)
    with col_a: style = st.selectbox("เลือกสไตล์:", list(STYLE_PRESETS.keys()))
    with col_b: size = st.selectbox("เลือกขนาด:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    
    if st.button("✨ เริ่มวาดรูป"):
        with st.spinner("🎨 กำลังวาดรูปคุณภาพสูง..."):
            # ใช้ Logic เดียวกับหมวดชุดใหญ่เป๊ะๆ
            eng_p = translate_to_pro_prompt(img_desc)
            w, h = (540, 960) if "9:16" in size else (960, 540) if "16:9" in size else (768, 768)
            final_url = get_img_url(eng_p, w, h, STYLE_PRESETS[style])
            
            if "9:16" in size:
                c1, c2, c3 = st.columns([1, 1.2, 1])
                with c2: st.image(final_url, use_container_width=True)
            else: st.image(final_url, use_container_width=True)
            st.markdown(f'[📥 ดาวน์โหลดรูปภาพ]({final_url})')