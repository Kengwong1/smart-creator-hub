import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v4.8", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. สไตล์ภาพ (Visual Presets) ---
STYLE_PRESETS = {
    "สไตล์ปกติ (สมจริงพื้นฐาน)": ", real human hands repairing smartphone, close-up photography, authentic tools, detailed screen, 8k, sharp focus, no robots",
    "ช่างซ่อมยุคอวกาศ (Cyber Repair)": ", cyberpunk workshop, neon glowing circuits, detailed mechanical arms repairing phone, 8k cinematic",
    "ฉากหลังสินค้า Affiliate (Studio)": ", product photography, iphone on marble stand, soft studio lighting, blurred background, high quality",
    "ไทยโมเดิร์น (Thai Art)": ", Thai traditional gold pattern, artistic, elegant, masterpiece, 8k",
    "ภาพถ่ายระดับโปร (Pro Photo)": ", shot on 85mm lens, realistic skin texture, professional workstation, cinematic lighting, ultra-detailed"
}

# --- 3. ระบบ AI และแปลภาษา ---
def translate_visual(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    sys_prompt = f"Convert this topic into a detailed photography prompt about: {text}. Must include 'technician hands', 'smartphone parts', 'tools'. Realistic style, not cartoon."
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(sys_prompt)
            return res.text
        except: continue
    try:
        return GoogleTranslator(source='th', target='en').translate(text) + ", real human hands, smartphone repair, photorealistic, 8k"
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
    # ใช้ nologo=true เพื่อลบโลโก้ และ model=flux
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

# --- 5. Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v4.8")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio(
        "เลือกเครื่องมือ:", 
        ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิป", "💬 ตอบคอมเมนต์"]
    )
    st.divider()
    st.caption("v4.8 | Safety Display Fix")

# --- 6. โซนการทำงาน ---

# --- 6.1 Magic Content ---
if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package")
    topic = st.text_input("หัวข้อคอนเทนต์:", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: chosen_style = st.selectbox("เลือกสไตล์ภาพ:", list(STYLE_PRESETS.keys()))
    with col_s2: chosen_size = st.selectbox("เลือกขนาด:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("ใส่หัวข้อก่อนนะคะ")
        else:
            with st.spinner("⏳ กำลังปรุงคอนเทนต์..."):
                text_res = generate_thai_content(f"ทำคอนเทนต์เรื่อง '{topic}': 1.ชื่อคลิป Viral 5 แบบ, 2.แคปชั่นป้ายยา Affiliate, 3.สคริปต์การถ่ายทำ")
                
                if text_res == "QUOTA_FULL":
                    st.error("โควต้าเต็ม รอ 1 นาทีนะคะ")
                else:
                    eng_p = translate_visual(topic)
                    w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                    img_url = get_img_url(eng_p, w, h, STYLE_PRESETS[chosen_style])
                    
                    st.divider()
                    st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                    
                    # --- ใช้ st.image แบบพื้นฐานที่สุด เพื่อความชัวร์ 100% ---
                    if "9:16" in chosen_size:
                        c1, c2, c3 = st.columns([1, 1, 1]) # จัดกลาง
                        with c2:
                            st.image(img_url, use_container_width=True)
                    else:
                        st.image(img_url, use_container_width=True)
                    
                    # ปุ่มดาวน์โหลดแบบธรรมดา (ปลอดภัยกว่า)
                    st.markdown(f"**[📥 คลิกเพื่อดาวน์โหลดภาพขนาดเต็ม]({img_url})**")
                    
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)

# --- 6.2 เสกรูปภาพอย่างเดียว ---
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    st.header("🎨 AI ศิลปินเสกรูป")
    img_desc = st.text_area("อยากได้รูปอะไรคะ?")
    col_a, col_b = st.columns(2)
    with col_a: style = st.selectbox("เลือกสไตล์:", list(STYLE_PRESETS.keys()))
    with col_b: size = st.selectbox("เลือกขนาด:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    
    if st.button("✨ เริ่มวาดรูป"):
        with st.spinner("🎨 กำลังวาด..."):
            eng_p = translate_visual(img_desc)
            w, h = (540, 960) if "9:16" in size else (960, 540) if "16:9" in size else (768, 768)
            img_url = get_img_url(eng_p, w, h, STYLE_PRESETS[style])
            
            if "9:16" in size:
                c1, c2, c3 = st.columns([1, 1, 1])
                with c2: st.image(img_url, use_container_width=True)
            else:
                st.image(img_url, use_container_width=True)
            st.markdown(f"**[📥 คลิกเพื่อดาวน์โหลดภาพขนาดเต็ม]({img_url})**")

# --- 6.3 - 6.6 เมนูย่อยอื่นๆ ---
elif menu == "🎬 วางแผนคอนเทนต์":
    st.header("🎬 วางแผนคอนเทนต์")
    topic = st.text_input("หัวข้อ:")
    if st.button("✨ วางแผน"):
        res = generate_thai_content(f"วางแผนคอนเทนต์: {topic}")
        if res == "QUOTA_FULL": st.error("โควต้าเต็ม")
        else: st.markdown(res)

elif menu == "💰 เขียนแคปชั่นป้ายยา":
    st.header("💰 เขียนแคปชั่น")
    topic = st.text_area("ข้อมูลสินค้า:")
    if st.button("💸 เสกแคปชั่น"):
        res = generate_thai_content(f"เขียนแคปชั่นป้ายยา: {topic}")
        if res == "QUOTA_FULL": st.error("โควต้าเต็ม")
        else: st.code(res)

elif menu == "🔍 ตั้งชื่อคลิป":
    st.header("🔍 ตั้งชื่อคลิป")
    topic = st.text_input("เนื้อหา:")
    if st.button("🚀 คิดชื่อ"):
        res = generate_thai_content(f"คิดชื่อคลิป Viral 5 แบบ: {topic}")
        if res == "QUOTA_FULL": st.error("โควต้าเต็ม")
        else: st.markdown(res)

elif menu == "💬 ตอบคอมเมนต์":
    st.header("💬 ตอบคอมเมนต์")
    topic = st.text_area("ข้อความ:")
    style = st.select_slider("สไตล์", options=["สุภาพ", "เป็นกันเอง", "กวนๆ"])
    if st.button("💭 คิดคำตอบ"):
        res = generate_thai_content(f"ตอบคอมเมนต์ '{topic}' สไตล์ {style}")
        if res == "QUOTA_FULL": st.error("โควต้าเต็ม")
        else: st.code(res)