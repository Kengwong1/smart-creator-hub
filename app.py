import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v6.8", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. คลังสไตล์ภาพ (แก้ไขเฉพาะหมวดสมจริง) ---
STYLE_PRESETS = {
    # อัปเกรดสูตรหมวดนี้: เน้นสัดส่วนที่ถูกต้อง ห้ามบิดเบี้ยว
    "📸 ภาพถ่ายสมจริง (Realistic)": ", professional macro photography, photorealistic, physically correct proportions, accurate hardware shapes, precise mechanical details, authentic textures, natural lighting, 8k, sharp focus, NO DISTORTION, NO DEFORMED PARTS",
    
    # หมวดอื่นๆ คงเดิมตามที่คุณเก่งต้องการ
    "🧸 3D แอนิเมชั่น (Pixar Style)": ", cute 3D character style, Pixar inspired, octane render, soft studio lighting, high detailed 3D model",
    "🎨 การ์ตูน / อนิเมะ (Anime)": ", vibrant cartoon style, anime illustration, clean lines, colorful",
    "🚀 ไซเบอร์พังค์ (Cyberpunk)": ", futuristic neon lights, tech atmosphere, cinematic colors",
    "📝 ภาพสเก็ตช์ (Pencil Sketch)": ", hand-drawn pencil sketch, graphite shading, detailed lines"
}

# --- 3. ระบบ AI ---
def translate_to_visual(text):
    try:
        keys = st.secrets.get("GEMINI_KEYS", [])
        if not keys: return text
        genai.configure(api_key=keys[0])
        model = genai.GenerativeModel('gemini-flash-latest')
        res = model.generate_content(f"Convert to short English image visual elements: {text}")
        return res.text.replace('"', '').replace("'", "").strip()
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

def get_img_url(visual_elements, width, height, style_suffix):
    encoded = urllib.parse.quote(f"{visual_elements} {style_suffix}")
    seed = int(time.time())
    # ใช้โมเดล Flux และคุณภาพสูงสุด
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model=flux&quality=100"

# --- 4. Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v6.8")
    st.write("ยินดีต้อนรับค่ะ ✨")
    menu = st.radio(
        "เลือกเครื่องมือ:", 
        ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิป", "💬 ตอบคอมเมนต์"]
    )
    st.divider()
    st.caption("v6.8 | Fix Size & Realism")

# --- 5. โซนการทำงาน ---

# 5.1 หมวดชุดใหญ่
if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package")
    topic = st.text_input("คุณอยากทำคอนเทนต์เรื่องอะไร?", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    col1, col2 = st.columns(2)
    with col1: chosen_style = st.selectbox("เลือกสไตล์ภาพ:", list(STYLE_PRESETS.keys()))
    with col2: chosen_size = st.selectbox("ขนาดภาพ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("กรุณาใส่หัวข้อค่ะ")
        else:
            with st.spinner("⏳ กำลังทำงาน..."):
                text_res = generate_thai_content(f"ทำคอนเทนต์เรื่อง '{topic}': 1.ชื่อคลิป Viral 5 แบบ, 2.แคปชั่นป้ายยา Affiliate, 3.สคริปต์การถ่ายทำ")
                if text_res == "QUOTA_FULL": st.error("โควต้าเต็ม รบกวนรอ 1 นาทีนะคะ")
                else:
                    eng_p = translate_to_visual(topic)
                    w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                    img_url = get_img_url(eng_p, w, h, STYLE_PRESETS[chosen_style])
                    
                    st.divider()
                    st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                    # แก้ไข: เอา use_container_width ออก เพื่อให้ภาพขนาดพอดี ไม่ใหญ่เกินไป
                    if "9:16" in chosen_size:
                        c_a, c_b, c_c = st.columns([1, 1.2, 1])
                        with c_b:
                            st.image(img_url)
                    else:
                        st.image(img_url)
                        
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)

# 5.2 หมวดเสกรูป
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    st.header("🎨 AI ศิลปินเสกรูปภาพ")
    img_desc = st.text_area("อยากได้รูปอะไรคะ?")
    col_a, col_b = st.columns(2)
    with col_a: style = st.selectbox("เลือกสไตล์:", list(STYLE_PRESETS.keys()))
    with col_b: size = st.selectbox("เลือกขนาด:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    if st.button("✨ เริ่มวาดรูป"):
        with st.spinner("🎨 กำลังวาด..."):
            eng_p = translate_to_visual(img_desc)
            w, h = (540, 960) if "9:16" in size else (960, 540) if "16:9" in size else (768, 768)
            img_url = get_img_url(eng_p, w, h, STYLE_PRESETS[style])
            # แก้ไข: เอา use_container_width ออก
            st.image(img_url)
            st.markdown(f'[📥 ดาวน์โหลดรูปภาพ]({img_url})')

# 5.3 - 5.6 หมวดอื่นๆ (คงเดิม)
elif menu == "🎬 วางแผนคอนเทนต์":
    st.header("🎬 วางแผนสคริปต์และการถ่ายทำ")
    plan_topic = st.text_input("หัวข้อที่ต้องการวางแผน:")
    if st.button("✨ เริ่มวางแผน"):
        with st.spinner("⏳ AI กำลังคิดสคริปต์..."):
            res = generate_thai_content(f"เขียนสคริปต์วิดีโอละเอียดสำหรับเรื่อง: {plan_topic}")
            st.markdown(res)

elif menu == "💰 เขียนแคปชั่นป้ายยา":
    st.header("💰 เสกแคปชั่นป้ายยา Affiliate")
    prod_details = st.text_area("ใส่รายละเอียดสินค้า/จุดเด่น:")
    if st.button("💸 สร้างแคปชั่น"):
        with st.spinner("⏳ กำลังแต่งแคปชั่น..."):
            res = generate_thai_content(f"เขียนแคปชั่นป้ายยาสำหรับ: {prod_details}")
            st.code(res)

elif menu == "🔍 ตั้งชื่อคลิป":
    st.header("🔍 ตั้งชื่อคลิปให้คนอยากกดดู")
    video_topic = st.text_input("คลิปของคุณเกี่ยวกับอะไร:")
    if st.button("🚀 คิดชื่อคลิป"):
        with st.spinner("⏳ กำลังคิดชื่อ..."):
            res = generate_thai_content(f"คิดชื่อคลิป Viral 10 แบบสำหรับ: {video_topic}")
            st.markdown(res)

elif menu == "💬 ตอบคอมเมนต์":
    st.header("💬 ผู้ช่วยตอบคอมเมนต์แฟนคลับ")
    fan_comment = st.text_area("ก๊อปปี้คอมเมนต์มาวางที่นี่:")
    if st.button("💭 คิดคำตอบ"):
        with st.spinner("⏳ กำลังหาคำตอบที่ดูดี..."):
            res = generate_thai_content(f"ช่วยคิดคำตอบคอมเมนต์นี้ให้ดูเป็นกันเองและเป็นมืออาชีพ: {fan_comment}")
            st.code(res)