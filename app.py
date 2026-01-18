import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v4", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. พจนานุกรมคีย์เวิร์ดวิเศษ (Style Dictionary) ---
STYLE_PRESETS = {
    "สไตล์ปกติ (ตามใจ AI)": "",
    "ช่างซ่อมยุคอวกาศ (Cyber Repair)": ", cyberpunk, intricate circuitry, neon internal glow, macro lens, 8k, futuristic workshop",
    "ฉากหลังสินค้า Affiliate (Studio)": ", soft cinematic studio lighting, minimalist marble stand, bokeh background, high-end commercial, clean aesthetic",
    "ไทยโมเดิร์น (พญานาค/ปลากัด)": ", Thai traditional Naga motif, iridescent scales, golden filigree, bioluminescent energy, digital art masterpiece",
    "ภาพถ่ายสมจริง (Photorealistic)": ", hyper-realistic, shot on 85mm lens, sharp focus, natural textures, DSLR quality",
    "แนวอนิเมะ (Anime Style)": ", high-quality anime illustration, vibrant colors, Makoto Shinkai style, detailed background"
}

# --- 3. ฟังก์ชันแปลภาษาและเรียกใช้ Gemini ---
def call_ai(prompt_text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(prompt_text)
            return res.text
        except: continue
    # ถ้า Gemini เต็ม ใช้ Google Translate แทน (Bypass)
    try:
        return GoogleTranslator(source='th', target='en').translate(prompt_text)
    except: return prompt_text

# --- 4. ฟังก์ชันเสกรูปภาพ ---
def get_img_url(prompt, width, height, style_suffix):
    full_prompt = prompt + style_suffix
    encoded = urllib.parse.quote(full_prompt)
    seed = int(time.time())
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

# --- 5. Sidebar ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v4")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผน & แคปชั่น"])
    st.divider()
    st.caption("v4.0 | Power by Pollinations & Gemini")

# --- 6. ระบบการทำงาน ---

# --- 6.1 Magic Content (รวมร่างทุกอย่าง) ---
if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package (จบในคลิกเดียว)")
    st.write("พิมพ์แค่หัวข้อเดียว AI จะเสกทั้งรูป หน้าปก แคปชั่น และแผนการทำคลิปให้ครบค่ะ!")
    
    topic = st.text_input("คุณอยากทำคอนเทนต์เรื่องอะไร?", placeholder="เช่น รีวิวซ่อมจอ iPhone 15 หรือ แนะนำพัดลมจิ๋วหน้าคอม")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        chosen_style = st.selectbox("เลือกสไตล์ภาพหน้าปก:", list(STYLE_PRESETS.keys()))
    with col_s2:
        chosen_size = st.selectbox("ขนาดภาพที่ต้องการ:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic:
            st.warning("ใส่หัวข้อก่อนนะคะคุณเก่ง")
        else:
            with st.spinner("⏳ กำลังเตรียมแพ็กเกจคอนเทนต์ให้คุณเก่ง..."):
                # 1. เสกรูปภาพ
                eng_p = call_ai(f"Detailed image prompt for: {topic}")
                w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                img_url = get_img_url(eng_p, w, h, STYLE_PRESETS[chosen_style])
                
                # 2. เสกเนื้อหา (ชื่อคลิป, แคปชั่น, แผน)
                text_res = call_ai(f"ทำคอนเทนต์เรื่อง '{topic}' ช่วยคิด 1.ชื่อคลิป Viral, 2.แคปชั่นป้ายยา Affiliate, 3.ลำดับการถ่ายทำ (Script)")
                
                # แสดงผล
                st.divider()
                st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                c1, c2, c3 = st.columns([1, 2, 1]) if "9:16" in chosen_size else st.columns([0.1, 5, 0.1])
                with c2:
                    st.markdown(f'<div style="text-align:center;"><img src="{img_url}" style="width:100%; border-radius:15px; box-shadow: 0px 10px 30px rgba(0,0,0,0.3);"></div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="text-align:center; margin-top:15px;"><a href="{img_url}" target="_blank" style="padding:10px 20px; background-color:#FF4B4B; color:white; border-radius:8px; text-decoration:none; font-weight:bold;">📥 ดาวน์โหลดภาพหน้าปก</a></div>', unsafe_allow_html=True)
                
                st.divider()
                st.subheader("📝 รายละเอียดคอนเทนต์")
                st.markdown(text_res)

# --- 6.2 เสกรูปอย่างเดียว ---
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    st.header("🎨 AI ศิลปินเสกรูป (พร้อมปุ่มสไตล์วิเศษ)")
    img_input = st.text_area("อยากได้รูปอะไรคะ?", placeholder="หุ่นยนต์แมวซ่อมมือถือ")
    
    c1, c2 = st.columns(2)
    with c1:
        style = st.selectbox("เลือกสไตล์วิเศษ:", list(STYLE_PRESETS.keys()))
    with c2:
        size = st.selectbox("เลือกขนาด:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
        
    if st.button("✨ เริ่มวาดรูป"):
        with st.spinner("🎨 กำลังบรรเลงศิลปะ..."):
            eng_prompt = call_ai(f"Detailed image prompt for: {img_input}")
            w, h = (540, 960) if "9:16" in size else (960, 540) if "16:9" in size else (768, 768)
            final_url = get_img_url(eng_prompt, w, h, STYLE_PRESETS[style])
            
            st.markdown(f'<div style="display:flex; justify-content:center;"><img src="{final_url}" style="max-width:100%; max-height:75vh; border-radius:12px; box-shadow:0px 8px 25px rgba(0,0,0,0.3);"></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align:center; margin-top:20px;"><a href="{final_url}" target="_blank" style="padding:10px 20px; background-color:#FF4B4B; color:white; border-radius:8px; text-decoration:none;">📥 ดาวน์โหลดรูปภาพ</a></div>', unsafe_allow_html=True)

# --- 6.3 วางแผน & แคปชั่น ---
elif menu == "🎬 วางแผน & แคปชั่น":
    st.header("🎬 ผู้ช่วยคิดงานคอนเทนต์ & Affiliate")
    action = st.selectbox("ต้องการให้ช่วยอะไรดีคะ?", ["เขียนแคปชั่นป้ายยาแรงๆ", "วางแผนสคริปต์วิดีโอ", "คิดชื่อคลิปดึงดูดใจ", "ตอบคอมเมนต์แฟนคลับ"])
    txt_input = st.text_area("ใส่รายละเอียดงานของคุณเก่งเลยค่ะ:")
    
    if st.button("✨ ให้ AI จัดการ"):
        with st.spinner("⏳ กำลังประมวลผล..."):
            res = call_ai(f"ทำเรื่อง '{action}' จากข้อมูลนี้: {txt_input}")
            st.code(res) if "แคปชั่น" in action or "ตอบคอมเมนต์" in action else st.markdown(res)