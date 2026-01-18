import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v6.0", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. สูตรลับภาพสวย (ตัวเดียวกับที่หมวดเสกรูปใช้แล้วเวิร์ก) ---
PRO_PHOTO_SUFFIX = ", professional photography, real human hands, smartphone repair tools, macro shot, highly detailed, 8k, sharp focus, NO ROBOTS, authentic workbench"

# --- 3. ระบบสมอง AI (All-in-One Call) ---

def generate_magic_content(topic):
    keys = st.secrets.get("GEMINI_KEYS", [])
    # สั่งให้ Gemini ทำงานทุกอย่างในครั้งเดียวเพื่อประหยัดโควต้า
    sys_prompt = f"""
    You are an expert content creator. For the topic: "{topic}", please provide:
    1. A professional English photography prompt for the cover image (Focus on real technician hands and tools, no robots).
    2. 5 Viral Thai titles.
    3. Thai Affiliate caption.
    4. Detailed Thai shooting script.
    
    Format your response exactly like this:
    IMAGE_PROMPT: [Your English Prompt Here]
    CONTENT: [Your Thai Content Here]
    """
    
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-flash-latest')
            res = model.generate_content(sys_prompt)
            full_text = res.text
            
            # แยกคำสั่งรูปภาพกับเนื้อหาออกจากกัน
            if "IMAGE_PROMPT:" in full_text and "CONTENT:" in full_text:
                parts = full_text.split("CONTENT:")
                img_p = parts[0].replace("IMAGE_PROMPT:", "").strip()
                content = parts[1].strip()
                return img_p, content
            return topic, full_text # กรณีฉุกเฉิน
        except: continue
    return "ERROR", "QUOTA_FULL"

# ฟังก์ชันเสกรูปภาพ (ใช้ Logic เดียวกันทั้งแอป)
def get_img_url(prompt, width, height):
    # ล้างเครื่องหมายคำพูดที่อาจทำให้ลิงก์พัง
    clean_prompt = prompt.replace('"', '').replace("'", "").strip()
    encoded = urllib.parse.quote(clean_prompt + PRO_PHOTO_SUFFIX)
    seed = int(time.time()) 
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

# --- 4. Sidebar เมนู ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v6.0")
    st.write(f"สวัสดีค่ะคุณเก่ง ✨")
    menu = st.radio("เลือกเครื่องมือ:", ["✨ Magic Content (ชุดใหญ่)", "🎨 เสกรูปภาพอย่างเดียว", "🎬 วางแผน & แคปชั่น"])
    st.divider()
    st.caption("v6.0 | All-in-One Saver")

# --- 5. โซนการทำงาน ---

if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package (ประหยัดโควต้า & ภาพสวย)")
    topic = st.text_input("คุณอยากทำคอนเทนต์เรื่องอะไร?", placeholder="เช่น รีวิวซ่อมจอ iPhone 15")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: chosen_size = st.selectbox("ขนาดภาพหน้าปก:", ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    with col_s2: chosen_seed = st.number_input("Seed (เลขเดิมรูปเดิม):", value=int(time.time()))

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic: st.warning("กรุณาใส่หัวข้อคอนเทนต์ค่ะ")
        else:
            with st.spinner("⏳ กำลังใช้ระบบ All-in-One ผลิตงานคุณภาพให้คุณเก่ง..."):
                # เรียก AI ครั้งเดียว ได้ทั้งรูปและเนื้อหา
                img_prompt, text_res = generate_magic_content(topic)
                
                if text_res == "QUOTA_FULL":
                    st.error("⚠️ โควต้าเต็มค่ะ รบกวนรอ 1 นาทีนะคะ")
                else:
                    # สร้างรูปภาพจาก Prompt ที่ AI แต่งให้
                    w, h = (540, 960) if "9:16" in chosen_size else (960, 540) if "16:9" in chosen_size else (768, 768)
                    img_url = get_img_url(img_prompt, w, h)
                    
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

# --- 6.2 เสกรูปภาพอย่างเดียว (สูตรเดิมที่คุณเก่งชอบ) ---
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    st.header("🎨 AI ศิลปินเสกรูปภาพ")
    img_desc = st.text_area("อยากได้รูปอะไรคะ?")
    if st.button("✨ เริ่มวาดรูป"):
        with st.spinner("🎨 กำลังวาด..."):
            # ใช้ Logic การดึงรูปตัวเดียวกันเป๊ะๆ
            final_url = get_img_url(img_desc, 768, 768)
            st.image(final_url, use_container_width=True)
            st.markdown(f'[📥 ดาวน์โหลดรูปภาพ]({final_url})')