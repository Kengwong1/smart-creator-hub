import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import urllib.parse
from deep_translator import GoogleTranslator
import random

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Smart Creator Hub v6.0", page_icon="🎬", layout="wide")
load_dotenv()

# --- 2. พจนานุกรมคีย์เวิร์ดวิเศษ (เน้นสมจริง & ห้ามหุ่นยนต์) ---
STYLE_PRESETS = {
    "สไตล์ปกติ (ช่างซ่อมสมจริง)": "professional macro photography of real human hands repairing smartphone, detailed electronic components, precision tools, professional workbench, natural lighting, 8k ultra detailed, photorealistic, sharp focus",
    "ภาพถ่ายระดับโปร (Macro)": "extreme macro photography, smartphone internal parts close-up, realistic textures and materials, cinematic dramatic lighting, 85mm lens f1.8, professional product shot, ultra sharp 8k",
    "ฉากหลังสินค้า Affiliate": "premium product photography, smartphone on elegant minimalist wooden desk, soft natural window light, beautiful bokeh background, commercial advertising quality, professional studio shot",
    "ไทยโมเดิร์น (สไตล์ช่างไทย)": "authentic Thai local mobile phone repair shop, realistic atmosphere, traditional Thai workspace, natural lighting, detailed workstation with tools, photorealistic 8k"
}

# --- 3. ระบบ AI และแปลภาษา ---

# ฟังก์ชันแปลและแต่ง Prompt (ปรับปรุงใหม่)
def translate_visual(text):
    """แปลและสร้าง prompt ที่ชัดเจนขึ้น"""
    keys = st.secrets.get("GEMINI_KEYS", [])
    
    # คำสั่งที่ชัดเจนกว่าเดิม
    instruction = """Create a detailed image generation prompt in English. 
Rules:
- Describe EXACTLY what you see (real human hands, tools, objects)
- Use photography terms (macro, bokeh, lighting, angle)
- Be specific about colors, textures, composition
- NO abstract concepts, NO robots, NO sci-fi
- Keep it natural and realistic

Thai text: """
    
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')  # ใช้โมเดลใหม่
            res = model.generate_content(instruction + text)
            return res.text.strip()
        except Exception as e:
            st.warning(f"Gemini API issue: {str(e)[:50]}")
            continue
    
    # ตัวแปลสำรองที่ดีขึ้น
    try:
        translated = GoogleTranslator(source='th', target='en').translate(text)
        # เพิ่มคำสำคัญที่ทำให้ภาพชัดเจนขึ้น
        enhanced = f"{translated}, professional photography, realistic scene, natural lighting, high detail, 8k resolution, photorealistic"
        return enhanced
    except:
        # ถ้าทุกอย่างล้มเหลว ใช้ภาษาไทยตรงๆ
        return f"{text}, professional photo, realistic, 8k"

# ฟังก์ชันคิดเนื้อหาภาษาไทย
def generate_thai_content(prompt_text):
    keys = st.secrets.get("GEMINI_KEYS", [])
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            res = model.generate_content(f"{prompt_text} (โปรดตอบเป็นภาษาไทยอย่างละเอียดและเป็นธรรมชาติ)")
            return res.text
        except:
            continue
    return "QUOTA_FULL"

# --- 4. ฟังก์ชันสร้าง URL รูปภาพ (ปรับปรุงให้เสถียร) ---
def get_img_url(prompt, width, height, style_suffix):
    """สร้าง URL ภาพพร้อมการจัดการที่ดีขึ้น"""
    # รวม prompt + style และทำความสะอาด
    full_prompt = f"{prompt}. {style_suffix}"
    
    # ลบอักขระแปลกๆ ที่อาจทำให้เกิดปัญหา
    full_prompt = full_prompt.replace('\n', ' ').replace('  ', ' ').strip()
    
    # Encode อย่างปลอดภัย
    encoded = urllib.parse.quote(full_prompt, safe='')
    
    # ใช้ seed แบบสุ่มที่ควบคุมได้
    seed = random.randint(1000, 999999)
    
    # สร้าง URL พร้อม parameters ที่ครบถ้วน
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&enhance=true&model=flux"
    
    return url

# ฟังก์ชันแสดงภาพพร้อม error handling
def display_image_safe(img_url, caption="รูปภาพ", size_mode="9:16"):
    """แสดงภาพพร้อมจัดการ error"""
    try:
        if "9:16" in size_mode:
            c1, c2, c3 = st.columns([1, 1.2, 1])
            with c2:
                st.image(img_url, caption=caption, use_container_width=True)
        else:
            st.image(img_url, caption=caption, use_container_width=True)
        
        # ปุ่มดาวน์โหลดที่เด่นชัด
        st.markdown(f'''
        <div style="text-align:center; margin-top:10px;">
            <a href="{img_url}" target="_blank" 
               style="background:#FF4B4B; color:white; padding:10px 20px; 
                      border-radius:5px; text-decoration:none; font-weight:bold;">
                📥 ดาวน์โหลดภาพขนาดเต็ม
            </a>
        </div>
        ''', unsafe_allow_html=True)
        
        # แสดง URL สำหรับ debug
        with st.expander("🔧 ดู URL ภาพ (สำหรับ debug)"):
            st.code(img_url, language="text")
            
    except Exception as e:
        st.error(f"⚠️ ไม่สามารถโหลดภาพได้: {str(e)}")
        st.info("💡 ลองคลิกปุ่มสร้างใหม่อีกครั้งนะคะ")

# --- 5. Sidebar เมนู (ครบ 6 ฟีเจอร์) ---
with st.sidebar:
    st.title("🎬 Smart Creator Hub v6.0")
    st.success(f"✨ สวัสดีค่ะคุณเก่ง")
    
    menu = st.radio(
        "เลือกเครื่องมือ:", 
        ["✨ Magic Content (ชุดใหญ่)", 
         "🎨 เสกรูปภาพอย่างเดียว", 
         "🎬 วางแผนคอนเทนต์", 
         "💰 เขียนแคปชั่นป้ายยา", 
         "🔍 ตั้งชื่อคลิป", 
         "💬 ตอบคอมเมนต์"]
    )
    
    st.divider()
    
    # เพิ่มเคล็ดลับการใช้งาน
    with st.expander("💡 เคล็ดลับ"):
        st.caption("""
        - ใส่รายละเอียดให้ชัดเจน จะได้ภาพตรงใจ
        - ถ้าภาพไม่ชอบ ลองกดสร้างใหม่
        - ภาษาไทยใช้ได้เลย AI แปลให้
        """)
    
    st.caption("v6.0 | Enhanced Pro Mode 🚀")

# --- 6. โซนการทำงาน ---

# --- 6.1 Magic Content (ชุดใหญ่) ---
if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package (จบในคลิกเดียว)")
    
    topic = st.text_input("คุณอยากทำคอนเทนต์เรื่องอะไร?", 
                          placeholder="เช่น รีวิวซ่อมจอ iPhone 15 Pro Max ด้วยมืออาชีพ")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: 
        chosen_style = st.selectbox("เลือกสไตล์ภาพหน้าปก:", list(STYLE_PRESETS.keys()))
    with col_s2: 
        chosen_size = st.selectbox("ขนาดภาพที่ต้องการ:", 
                                   ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่", type="primary"):
        if not topic:
            st.warning("⚠️ กรุณาใส่หัวข้อคอนเทนต์ค่ะ")
        else:
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # 1. คิดเนื้อหาไทย
                status_text.text("⏳ กำลังคิดเนื้อหา...")
                progress_bar.progress(25)
                
                text_res = generate_thai_content(
                    f"ทำคอนเทนต์เรื่อง '{topic}': "
                    f"1.ชื่อคลิป Viral 5 แบบ, "
                    f"2.แคปชั่นป้ายยา Affiliate พร้อม CTA, "
                    f"3.สคริปต์การถ่ายทำแบบละเอียด"
                )
                
                if text_res == "QUOTA_FULL":
                    st.error("⚠️ โควต้า Gemini เต็มค่ะ รบกวนรอ 1-2 นาทีนะคะ")
                    st.stop()
                
                # 2. เสกรูปหน้าปก
                status_text.text("🎨 กำลังสร้างภาพระดับโปร...")
                progress_bar.progress(50)
                
                eng_prompt = translate_visual(topic)
                
                # กำหนดขนาดตามที่เลือก
                if "9:16" in chosen_size:
                    w, h = 1080, 1920  # เพิ่มความละเอียด
                elif "16:9" in chosen_size:
                    w, h = 1920, 1080
                else:
                    w, h = 1024, 1024
                
                progress_bar.progress(75)
                img_url = get_img_url(eng_prompt, w, h, STYLE_PRESETS[chosen_style])
                
                progress_bar.progress(100)
                status_text.text("✅ เสร็จสมบูรณ์!")
                time.sleep(0.5)
                status_text.empty()
                progress_bar.empty()
                
                # แสดงผลลัพธ์
                st.divider()
                st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")
                
                display_image_safe(img_url, f"ภาพหน้าปก: {topic}", chosen_size)
                
                st.divider()
                st.subheader("📝 รายละเอียดคอนเทนต์")
                st.markdown(text_res)
                
                # ปุ่มสร้างใหม่
                if st.button("🔄 สร้างภาพใหม่ (แบบเดิม)"):
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")
                st.info("💡 ลองกดปุ่มอีกครั้งนะคะ")

# --- 6.2 เสกรูปภาพอย่างเดียว ---
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    st.header("🎨 AI ศิลปินเสกรูป (Photography Mode)")
    
    img_desc = st.text_area(
        "อยากได้รูปอะไรคะ? (ยิ่งบรรยายละเอียดยิ่งดี)",
        placeholder="ตัวอย่าง: มือช่างกำลังถอดหน้าจอ iPhone ด้วยไขควง บนโต๊ะทำงานสีขาว มีแสงธรรมชาติส่องมา",
        height=100
    )
    
    col_a, col_b = st.columns(2)
    with col_a: 
        style = st.selectbox("เลือกสไตล์:", list(STYLE_PRESETS.keys()))
    with col_b: 
        size = st.selectbox("เลือกขนาด:", 
                           ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"])
    
    if st.button("✨ เริ่มวาดรูป", type="primary"):
        if not img_desc:
            st.warning("⚠️ กรุณาบอกว่าอยากได้รูปแบบไหนค่ะ")
        else:
            with st.spinner("🎨 กำลังบรรเลงศิลปะระดับโปร..."):
                try:
                    eng_prompt = translate_visual(img_desc)
                    
                    st.info(f"🔍 Prompt ที่ใช้: {eng_prompt[:100]}...")
                    
                    if "9:16" in size:
                        w, h = 1080, 1920
                    elif "16:9" in size:
                        w, h = 1920, 1080
                    else:
                        w, h = 1024, 1024
                    
                    final_url = get_img_url(eng_prompt, w, h, STYLE_PRESETS[style])
                    
                    st.success("✅ สร้างเสร็จแล้วค่ะ!")
                    display_image_safe(final_url, img_desc, size)
                    
                    # ปุ่มสร้างแบบอื่น
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 สร้างภาพใหม่"):
                            st.rerun()
                    with col2:
                        if st.button("🎲 สุ่มสไตล์ใหม่"):
                            st.session_state['random_style'] = random.choice(list(STYLE_PRESETS.keys()))
                            st.rerun()
                            
                except Exception as e:
                    st.error(f"❌ ไม่สามารถสร้างภาพได้: {str(e)}")

# --- 6.3 - 6.6 เมนูอื่นๆ (ปรับปรุง UI) ---
elif menu == "🎬 วางแผนคอนเทนต์":
    st.header("🎬 AI วางแผนสคริปต์")
    st.write("ให้ AI ช่วยวางแผนคอนเทนต์ตั้งแต่ต้นจนจบ")
    
    topic = st.text_input("หัวข้อคอนเทนต์:", 
                         placeholder="เช่น รีวิวการซ่อมมือถือในร้าน")
    
    if st.button("✨ วางแผนเลย", type="primary"):
        if topic:
            with st.spinner("💭 กำลังคิด..."):
                res = generate_thai_content(
                    f"วางแผนคอนเทนต์อย่างละเอียด: {topic} "
                    f"(โครงสร้าง, Hook, เนื้อหา, CTA)"
                )
                if res != "QUOTA_FULL": 
                    st.markdown(res)
                else: 
                    st.error("⚠️ รอ 1-2 นาทีนะคะ")

elif menu == "💰 เขียนแคปชั่นป้ายยา":
    st.header("💰 เสกแคปชั่นป้ายยาสไตล์ Viral")
    
    details = st.text_area("ข้อมูลสินค้า/บริการ:", 
                          placeholder="ตัวอย่าง: บริการซ่อมมือถือทุกรุ่น ราคาเริ่มต้น 500 บาท รับประกัน 30 วัน")
    
    if st.button("💸 เสกแคปชั่น", type="primary"):
        if details:
            with st.spinner("✍️ กำลังเขียน..."):
                res = generate_thai_content(
                    f"เขียนแคปชั่นป้ายยาแรงๆ สไตล์ Viral พร้อม Emoji และ CTA: {details}"
                )
                if res != "QUOTA_FULL": 
                    st.success("✅ เสร็จแล้วค่ะ!")
                    st.code(res, language="markdown")
                else: 
                    st.error("⚠️ รอ 1-2 นาทีนะคะ")

elif menu == "🔍 ตั้งชื่อคลิป":
    st.header("🔍 ตั้งชื่อคลิปให้คนกดเข้ามา")
    
    topic_name = st.text_input("เนื้อหาในคลิป:", 
                               placeholder="เช่น สอนวิธีซ่อมหน้าจอแตกเองที่บ้าน")
    
    if st.button("🚀 คิดชื่อให้หน่อย", type="primary"):
        if topic_name:
            with st.spinner("🤔 กำลังคิด..."):
                res = generate_thai_content(
                    f"คิดชื่อคลิป Viral น่าคลิกมาก 5 แบบ สำหรับเนื้อหา: {topic_name}"
                )
                if res != "QUOTA_FULL": 
                    st.markdown(res)
                else: 
                    st.error("⚠️ รอ 1-2 นาทีนะคะ")

elif menu == "💬 ตอบคอมเมนต์":
    st.header("💬 ผู้ช่วยตอบคอมเมนต์แฟนคลับ")
    
    comment = st.text_area("ข้อความจากแฟนคลับ:", 
                          placeholder="วางคอมเมนต์ที่ต้องการตอบ")
    
    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("โทนการตอบ:", 
                           ["เป็นกันเอง", "สุภาพมาก", "ขำขัน", "มืออาชีพ"])
    
    if st.button("💭 คิดคำตอบ", type="primary"):
        if comment:
            with st.spinner("💬 กำลังคิด..."):
                res = generate_thai_content(
                    f"ตอบคอมเมนต์นี้แบบ{tone}: {comment} "
                    f"(ตอบให้เหมาะสม สร้างความผูกพัน)"
                )
                if res != "QUOTA_FULL": 
                    st.success("✅ คิดได้แล้วค่ะ!")
                    st.code(res, language="markdown")
                else: 
                    st.error("⚠️ รอ 1-2 นาทีนะคะ")