import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v4.3", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. พจนานุกรมคีย์เวิร์ดวิเศษ (Style Presets) ---
STYLE_PRESETS = {
    "สไตล์ปกติ (ตามใจ AI)": "",
    "ช่างซ่อมยุคอวกาศ (Cyber Repair)": ", cyberpunk, intricate circuitry, neon internal glow, macro lens, 8k, futuristic workshop",
    "ฉากหลังสินค้า Affiliate (Studio)": ", soft cinematic studio lighting, minimalist marble stand, bokeh background, high-end commercial, clean aesthetic",
    "ไทยโมเดิร์น (พญานาค/ปลากัด)": ", Thai traditional Naga motif, iridescent scales, golden filigree, bioluminescent energy, digital art masterpiece",
    "ภาพถ่ายสมจริง (Photorealistic)": ", hyper-realistic, shot on 85mm lens, sharp focus, natural textures, DSLR quality"
}

# เครื่องปรุงรสพิเศษสำหรับระบบสำรอง
MAGIC_SAUCE = ", cinematic lighting, hyper-realistic, highly detailed, 8k, masterpiece, sharp focus"

# --- 3. ฟังก์ชัน AI แปลภาษาและคิดเนื้อหา ---

# สำหรับแปลภาษาเสกรูป (ระบบอมตะ 2 ชั้น)
def translate_for_image(text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(f"Translate to English image prompt: {text}")
            return res.text
        except: continue
    # ถ้า Gemini เต็ม ใช้ Google Translate + เครื่องปรุงพิเศษ
    try:
        translated = GoogleTranslator(source='th', target='en').translate(text)
        return translated + MAGIC_SAUCE
    except: return text + MAGIC_SAUCE

# สำหรับคิดเนื้อหาไทย (ต้องใช้สมอง Gemini)
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

# --- 5. Sidebar เมนู (กลับมาครบแล้วค่ะ!) ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v4.3")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio(
        "เลือกเครื่องมือ:", 
        ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผนคอนเทนต์", "💰 เขียนแคปชั่นป้ายยา", "🔍 ตั้งชื่อคลิป", "💬 ตอบคอมเมนต์"]
    )
    st.divider()
    st.caption("v4.3 | Complete Masterpiece Edition")

# --- 6. โซนการทำงาน ---

# --- 6.1 Magic Content ---
if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package (จบในคลิกเดียว)")
    topic = st.text_input("คุณอยากทำคอนเทนต์เรื่องอะไร?", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: chosen_style = st.selectbox("เลือกสไตล์ภาพหน้าปก:", list(STYLE_PRESETS.keys()))
    with col_s2: chosen_size = st.selectbox("ขนาดภาพที่ต้องการ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("กรุณาใส่หัวข้อคอนเทนต์ค่ะ")
        else:
            with st.spinner("⏳ กำลังผลิตคอนเทนต์คุณภาพให้คุณเก่ง..."):
                # 1. คิดเนื้อหาไทย
                text_res = generate_thai_content(f"ช่วยคิดคอนเทนต์เรื่อง '{topic}': 1.ชื่อคลิป Viral 5 แบบ, 2.แคปชั่นป้ายยา Affiliate, 3.สคริปต์การถ่ายทำ")
                
                if text_res == "QUOTA_FULL":
                    st.error("⚠️ โควต้า Gemini เต็มค่ะ รบกวนรอ 1 นาทีนะคะ (ส่วนเนื้อหาต้องใช้สมอง AI คิดเท่านั้นค่ะ)")
                else:
                    # 2. เสกรูปหน้าปก
                    eng_p = translate_for_image(topic)
                    w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                    img_url = get_img_url(eng_p, w, h, STYLE_PRESETS[chosen_style])
                    
                    st.divider()
                    st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                    # จัดวางตรงกลาง
                    c1, c2, c3 = st.columns([1, 2, 1]) if "9:16" in chosen_size else st.columns([0.1, 5, 0.1])
                    with c2:
                        st.markdown(f'<div style="text-align:center;"><img src="{img_url}" style="width:100%; border-radius:15px; box-shadow: 0px 10px 30px rgba(0,0,0,0.3);"></div>', unsafe_allow_html=True)
                    
                    st.divider()
                    st.subheader("📝 รายละเอียดคอนเทนต์")
                    st.markdown(text_res)
                    st.markdown(f'<div style="text-align:center; margin-top:20px;"><a href="{img_url}" target="_blank" style="padding:10px 20px; background-color:#FF4B4B; color:white; border-radius:8px; text-decoration:none; font-weight:bold;">📥 ดาวน์โหลดภาพหน้าปก</a></div>', unsafe_allow_html=True)

# --- 6.2 เสกรูปอย่างเดียว ---
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    st.header("🎨 AI ศิลปินเสกรูปภาพ (ระบบแปลไทยอมตะ)")
    img_desc = st.text_area("อยากได้รูปอะไรคะ? (พิมพ์ไทยได้เลย)", height=100)
    
    col_a, col_b = st.columns(2)
    with col_a: style = st.selectbox("เลือกสไตล์วิเศษ:", list(STYLE_PRESETS.keys()))
    with col_b: size = st.selectbox("เลือกขนาดภาพ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    
    if st.button("✨ เริ่มวาดรูป"):
        with st.spinner("🎨 กำลังสร้างงานศิลปะ..."):
            eng_prompt = translate_for_image(img_desc)
            w, h = (540, 960) if "9:16" in size else (960, 540) if "16:9" in size else (768, 768)
            final_url = get_img_url(eng_prompt, w, h, STYLE_PRESETS[style])
            
            # แสดงผลจัดกลาง
            html_img = f'<div style="display:flex; justify-content:center;"><img src="{final_url}" style="max-width:100%; max-height:75vh; border-radius:12px; box-shadow:0px 8px 25px rgba(0,0,0,0.3);"></div>'
            if "9:16" in size:
                c1, c2, c3 = st.columns([1, 2, 1])
                with c2: st.markdown(html_img, unsafe_allow_html=True)
            else: st.markdown(html_img, unsafe_allow_html=True)
            
            st.markdown(f'<div style="text-align:center; margin-top:20px;"><a href="{final_url}" target="_blank" style="padding:10px 20px; background-color:#FF4B4B; color:white; border-radius:8px; text-decoration:none;">📥 ดาวน์โหลดรูปภาพ</a></div>', unsafe_allow_html=True)

# --- หมวดหมู่อื่นๆ ---
elif menu == "🎬 วางแผนคอนเทนต์":
    st.header("🎬 วางแผนสคริปต์คอนเทนต์")
    topic = st.text_input("หัวข้อที่ต้องการวางแผน:")
    if st.button("✨ วางแผน"):
        res = generate_thai_content(f"ช่วยวางแผนคอนเทนต์เรื่อง: {topic}")
        if res == "QUOTA_FULL": st.error("โควต้าเต็ม รอ 1 นาทีนะคะ")
        else: st.markdown(res)

elif menu == "💰 เขียนแคปชั่นป้ายยา":
    st.header("💰 เขียนแคปชั่น Affiliate")
    details = st.text_area("ข้อมูลสินค้า:")
    if st.button("💸 เสกแคปชั่น"):
        res = generate_thai_content(f"เขียนแคปชั่นป้ายยาแรงๆ จากข้อมูลนี้: {details}")
        if res == "QUOTA_FULL": st.error("โควต้าเต็ม รอ 1 นาทีนะคะ")
        else: st.code(res)

elif menu == "🔍 ตั้งชื่อคลิป":
    st.header("🔍 ตั้งชื่อคลิปให้น่าคลิก")
    topic_name = st.text_input("เนื้อหาคลิปโดยสรุป:")
    if st.button("🚀 เสกชื่อคลิป"):
        res = generate_thai_content(f"คิดชื่อคลิป Viral 5 แบบ สำหรับเรื่อง: {topic_name}")
        if res == "QUOTA_FULL": st.error("โควต้าเต็ม รอ 1 นาทีนะคะ")
        else: st.markdown(res)

elif menu == "💬 ตอบคอมเมนต์":
    st.header("💬 ผู้ช่วยตอบคอมเมนต์")
    comment = st.text_area("ข้อความจากแฟนคลับ:")
    style = st.select_slider("เลือกสไตล์", options=["สุภาพ", "เป็นกันเอง", "กวนๆ"])
    if st.button("💭 คิดคำตอบ"):
        res = generate_thai_content(f"ตอบคอมเมนต์ '{comment}' ในสไตล์ {style}")
        if res == "QUOTA_FULL": st.error("โควต้าเต็ม รอ 1 นาทีนะคะ")
        else: st.code(res)