import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v5.8", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. ชุดคีย์เวิร์ดมาตรฐาน (ตัวเดียวกับหมวดที่เสกภาพเก่ง) ---
PRO_PHOTO_SUFFIX = ", professional photography, real human hands, smartphone repair tools, macro shot, highly detailed, 8k, sharp focus, NO ROBOTS"

# --- 3. ระบบ AI ---
def translate_to_pro_prompt(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    # บังคับให้ Gemini ตอบเฉพาะคำแปล "ห้ามมีน้ำ"
    instruction = "Translate to a professional English image prompt (SHORT AND CLEAN ONLY, NO INTRO, NO QUOTES): "
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(instruction + text)
            # ล้างขยะออกจากคำแปล (กันเหนียว)
            clean_text = res.text.replace('"', '').replace("'", "").replace("Prompt:", "").strip()
            return clean_text
        except: continue
    return GoogleTranslator(source='th', target='en').translate(text)

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
    st.title("🎬 Smart Creator Hub v5.8")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา"])
    st.divider()
    st.caption("v5.8 | Direct Link Recovery")

# --- 5. โซนการทำงาน ---

if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package")
    topic = st.text_input("คุณอยากทำคอนเทนต์เรื่องอะไร?", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: chosen_size = st.selectbox("ขนาดภาพหน้าปก:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    with col_s2: chosen_seed = st.number_input("Seed (เปลี่ยนเลขเพื่อเปลี่ยนรูป):", value=int(time.time()))

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("กรุณาใส่หัวข้อค่ะ")
        else:
            with st.spinner("⏳ กำลังใช้สมอง AI ผลิตคอนเทนต์..."):
                # 1. คิดเนื้อหา
                text_res = generate_thai_content(f"ทำคอนเทนต์เรื่อง '{topic}': 1.ชื่อคลิป Viral 5 แบบ, 2.แคปชั่นป้ายยา Affiliate, 3.สคริปต์การถ่ายทำ")
                
                if text_res == "QUOTA_FULL":
                    st.error("⚠️ โควต้าเต็ม รบกวนรอ 1 นาทีนะคะ")
                else:
                    # 2. เสกรูปภาพ (ใช้ Logic เดียวกับหมวดเสกรูปอย่างเดียวเป๊ะๆ)
                    eng_p = translate_to_pro_prompt(topic)
                    w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                    
                    # สร้างลิงก์แบบสะอาดที่สุด
                    full_prompt = urllib.parse.quote(f"{eng_p}{PRO_PHOTO_SUFFIX}")
                    final_url = f"https://image.pollinations.ai/prompt/{full_prompt}?width={w}&height={h}&seed={chosen_seed}&nologo=true&model=flux"
                    
                    st.divider()
                    st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                    
                    # แสดงรูปภาพด้วยคำสั่งมาตรฐาน (ที่เคยสำเร็จ)
                    if "9:16" in chosen_size:
                        c1, c2, c3 = st.columns([1, 1.2, 1])
                        with c2: st.image(final_url, use_container_width=True)
                    else:
                        st.image(final_url, use_container_width=True)
                    
                    st.markdown(f'[📥 **ดาวน์โหลดรูปภาพ**]({final_url})')
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)

# (หมวดเสกรูปอย่างเดียวก็ใช้ translate_to_pro_prompt เช่นกันค่ะ)
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    img_desc = st.text_area("อยากได้รูปอะไรคะ?")
    if st.button("✨ เริ่มวาดรูป"):
        with st.spinner("🎨 กำลังวาด..."):
            eng_p = translate_to_pro_prompt(img_desc)
            final_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(eng_p + PRO_PHOTO_SUFFIX)}?width=768&height=768&seed={int(time.time())}&model=flux"
            st.image(final_url, use_container_width=True)
            st.markdown(f'[📥 ดาวน์โหลดรูปภาพ]({final_url})')