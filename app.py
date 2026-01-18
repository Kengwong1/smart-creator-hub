import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v7.1", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. สูตรลับภาพสวยระดับ Masterpiece (เน้นฮาร์ดแวร์แม่นยำ) ---
LUXURY_TECH_SUFFIX = (
    ", high-end commercial photography, technical precision, accurate smartphone architecture, "
    "triple-lens camera system, delicate internal flex cables, logic board details, ray tracing, "
    "global illumination, studio lighting, 8k, sharp focus, hyper-realistic, masterpiece, NO DEFORMED PARTS"
)

# --- 3. ระบบ AI (ตัวลับ: สั่งให้ Gemini เขียนบรรยายฮาร์ดแวร์) ---
def generate_technical_prompt(text):
    try:
        keys = st.secrets.get("GEMINI_KEYS", [])
        if not keys: return text
        genai.configure(api_key=keys[0])
        model = genai.GenerativeModel('gemini-flash-latest')
        # สั่งให้ Gemini บรรยายสิ่งที่ต้องมีในภาพอย่างละเอียด (เช่น ถ้าซ่อมไอโฟน ต้องมีกล้อง มีบอร์ด)
        instruction = (
            "As a technical photographer, describe the visual elements of this topic for an AI image generator. "
            "Focus on realistic hardware parts, correct shapes, and professional lighting. "
            "Keep it under 50 words. Topic: "
        )
        res = model.generate_content(instruction + text)
        clean_text = res.text.replace('"', '').replace("'", "").strip()
        return clean_text
    except:
        return GoogleTranslator(source='th', target='en').translate(text)

def generate_thai_content(topic):
    keys = st.secrets.get("GEMINI_KEYS", [])
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(f"{topic} (โปรดตอบเป็นภาษาไทยอย่างละเอียด)")
            return res.text
        except: continue
    return "QUOTA_FULL"

def get_img_url(technical_prompt, width, height):
    # รวมคำบรรยายจาก Gemini + สูตรลับความหรูหรา
    full_prompt = f"{technical_prompt} {LUXURY_TECH_SUFFIX}"
    encoded = urllib.parse.quote(full_prompt)
    seed = int(time.time())
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model=flux&quality=100"

# --- 4. Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v7.1")
    st.write("ยินดีต้อนรับค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา"])
    st.divider()
    st.caption("v7.1 | Technical Detailer Upgrade")

# --- 5. โซนการทำงาน ---

if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package (ความแม่นยำสูง)")
    topic = st.text_input("คุณอยากทำคอนเทนต์เรื่องอะไร?", placeholder="เช่น รีวิวซ่อมจอ iPhone 15 Pro Max")
    
    col1, col2 = st.columns(2)
    with col1: chosen_size = st.selectbox("ขนาดภาพ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    with col2: st.info("ระบบจะใช้ Gemini ช่วยออกแบบฮาร์ดแวร์ให้สมจริงที่สุดค่ะ")

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("กรุณาใส่หัวข้อค่ะ")
        else:
            with st.spinner("⏳ Gemini กำลังจำลองภาพฮาร์ดแวร์และเนื้อหา..."):
                text_res = generate_thai_content(f"ทำคอนเทนต์เรื่อง '{topic}': 1.ชื่อคลิป Viral 5 แบบ, 2.แคปชั่นป้ายยา Affiliate, 3.สคริปต์การถ่ายทำ")
                
                if text_res == "QUOTA_FULL":
                    st.error("โควต้าเต็ม รบกวนรอ 1 นาทีนะคะ")
                else:
                    # ใช้ระบบใหม่: ให้ Gemini ร่างรายละเอียดภาพให้ก่อน
                    tech_p = generate_technical_prompt(topic)
                    w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                    img_url = get_img_url(tech_p, w, h)
                    
                    st.divider()
                    st.subheader("🖼️ ภาพหน้าปกคอนเทนต์ (Technical Detail)")
                    # จัดวางขนาด Compact ตาม v7.0
                    if "9:16" in chosen_size:
                        c_a, c_b, c_c = st.columns([1.5, 1, 1.5])
                        with c_b: st.image(img_url)
                    else:
                        c_a, c_b, c_c = st.columns([1, 2, 1])
                        with c_b: st.image(img_url)
                        
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)

# (หมวดอื่นๆ คงเดิม แต่ใช้ระบบ Technical Detailer เหมือนกันค่ะ)
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    st.header("🎨 AI ศิลปินเสกรูปภาพ (โหมดสมจริงพิเศษ)")
    img_desc = st.text_area("อยากได้รูปอะไรคะ?")
    if st.button("✨ เริ่มวาดรูป"):
        with st.spinner("🎨 กำลังประมวลผลฮาร์ดแวร์..."):
            tech_p = generate_technical_prompt(img_desc)
            img_url = get_img_url(tech_p, 768, 768)
            st.image(img_url)
            st.markdown(f'[📥 ดาวน์โหลดรูปภาพ]({img_url})')