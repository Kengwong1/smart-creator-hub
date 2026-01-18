import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v4.1", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. คีย์เวิร์ดวิเศษ (Style Presets) ---
STYLE_PRESETS = {
    "สไตล์ปกติ (ตามใจ AI)": "",
    "ช่างซ่อมยุคอวกาศ (Cyber Repair)": ", cyberpunk, intricate circuitry, neon internal glow, macro lens, 8k, futuristic workshop",
    "ฉากหลังสินค้า Affiliate (Studio)": ", soft cinematic studio lighting, minimalist marble stand, bokeh background, high-end commercial, clean aesthetic",
    "ไทยโมเดิร์น (พญานาค/ปลากัด)": ", Thai traditional Naga motif, iridescent scales, golden filigree, bioluminescent energy, digital art masterpiece",
    "ภาพถ่ายสมจริง (Photorealistic)": ", hyper-realistic, shot on 85mm lens, sharp focus, natural textures, DSLR quality"
}

# --- 3. ฟังก์ชัน AI แยกส่วนการทำงาน ---

# ฟังก์ชัน A: สำหรับแปลภาษาเสกรูป (ใช้ Google Translate ได้ถ้า Gemini เต็ม)
def translate_for_image(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(f"Translate this to a detailed English image prompt: {text}")
            return res.text
        except: continue
    return GoogleTranslator(source='th', target='en').translate(text)

# ฟังก์ชัน B: สำหรับคิดคอนเทนต์ (ต้องใช้ Gemini เท่านั้นเพื่อให้ได้ภาษาไทยที่ฉลาด)
def generate_content_thai(prompt_text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            # บังคับให้ตอบเป็นภาษาไทยเสมอ
            full_prompt = f"{prompt_text} (โปรดตอบเป็นภาษาไทยอย่างละเอียดและน่าสนใจ)"
            res = model.generate_content(full_prompt)
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
    st.title("🎬 Smart Creator Hub v4.1")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผน & แคปชั่น"])
    st.caption("v4.1 | Fix Thai Content Logic")

# --- 6. ระบบการทำงาน ---

if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package (ภาษาไทยสมบูรณ์)")
    topic = st.text_input("คุณอยากทำคอนเทนต์เรื่องอะไร?", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: chosen_style = st.selectbox("เลือกสไตล์ภาพหน้าปก:", list(STYLE_PRESETS.keys()))
    with col_s2: chosen_size = st.selectbox("ขนาดภาพที่ต้องการ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic:
            st.warning("ใส่หัวข้อก่อนนะคะ")
        else:
            with st.spinner("⏳ กำลังใช้ AI คิดเนื้อหาและเสกรูปให้คุณเก่ง..."):
                # 1. เสกเนื้อหา (ต้องได้ภาษาไทย)
                content_p = f"ช่วยคิดคอนเทนต์เรื่อง '{topic}' โดยระบุ: 1.ชื่อคลิปที่น่าสนใจ 5 แบบ, 2.แคปชั่นป้ายยา Affiliate สำหรับ Facebook, 3.บทพูดหรือลำดับการถ่ายทำ (Script)"
                text_res = generate_content_thai(content_p)
                
                if text_res == "QUOTA_FULL":
                    st.error("⚠️ ตอนนี้โควต้า Gemini เต็มค่ะ รบกวนรอ 1-2 นาทีแล้วกดใหม่นะคะ (โหมดเนื้อหาต้องใช้ AI คิดเท่านั้นค่ะ)")
                else:
                    # 2. เสกรูปภาพ (ใช้ตัวแปลสำรองได้ถ้าจำเป็น)
                    eng_p = translate_for_image(topic)
                    w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                    img_url = get_img_url(eng_p, w, h, STYLE_PRESETS[chosen_style])
                    
                    # แสดงผล
                    st.divider()
                    st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                    c1, c2, c3 = st.columns([1, 2, 1]) if "9:16" in chosen_size else st.columns([0.1, 5, 0.1])
                    with c2:
                        st.markdown(f'<div style="text-align:center;"><img src="{img_url}" style="width:100%; border-radius:15px; box-shadow: 0px 10px 30px rgba(0,0,0,0.3);"></div>', unsafe_allow_html=True)
                    
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์ (ภาษาไทย)")
                    st.info("คุณเก่งสามารถก๊อปปี้เนื้อหาด้านล่างไปใช้ได้เลยค่ะ")
                    st.markdown(text_res)
                    st.markdown(f'<div style="text-align:center; margin-top:15px;"><a href="{img_url}" target="_blank" style="padding:10px 20px; background-color:#FF4B4B; color:white; border-radius:8px; text-decoration:none; font-weight:bold;">📥 ดาวน์โหลดภาพหน้าปก</a></div>', unsafe_allow_html=True)

# (ส่วนเมนูอื่นๆ ปรับปรุงให้ใช้ generate_content_thai เช่นกันค่ะ)