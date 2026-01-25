import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re

# --- 1. CONFIG ---
st.set_page_config(page_title="SME Pro Studio v15.0", page_icon="🛍️", layout="centered")

# --- 2. BACKEND: PROMPT ENGINEERING (สูตรลับช่างภาพ) ---
# เราไม่ได้แค่แปล แต่เรา "เสกฉาก" ให้ด้วย
THEMES = {
    "✨ หรูหรา (Luxury)": "placed on a black marble table, golden lighting, elegant atmosphere, bokeh background, high-end product photography",
    "🌿 ธรรมชาติ (Organic)": "placed on a natural stone, surrounded by green leaves and water ripples, soft sunlight, organic style, fresh feeling",
    "⚪ มินิมอล (Minimal)": "placed on a clean white podium, soft pastel background, studio lighting, minimal aesthetic, clean composition",
    "🏮 ตรุษจีน/มงคล (Chinese New Year)": "red background with gold accents, chinese lanterns, festive atmosphere, lucky style, bright lighting",
    "🏙️ นีออน (Cyberpunk)": "neon lights background, blue and pink lighting, futuristic product shot, reflection on glass floor"
}

# ระบบแปลภาษา (เน้นคำศัพท์สินค้า)
LOCAL_DICT = {
    "สบู่": "soap bar", "ครีม": "cream jar", "เซรั่ม": "serum bottle", 
    "ลิปสติก": "lipstick", "กาแฟ": "coffee cup", "เสื้อ": "t-shirt",
    "กระเป๋า": "handbag", "รองเท้า": "sneakers", "น้ำหอม": "perfume bottle"
}

try:
    genai.configure(api_key=st.secrets["GEMINI_KEYS"])
    model_gemini = genai.GenerativeModel('gemini-1.5-flash')
    gemini_ready = True
except:
    gemini_ready = False

def create_pro_prompt(product, theme_key):
    # 1. แปลคำศัพท์สินค้า
    for thai, eng in LOCAL_DICT.items():
        if thai in product: product = product.replace(thai, eng)
    
    # 2. ถ้ายังเป็นไทย ให้ Gemini ช่วยแปล
    if bool(re.search('[ก-ฮ]', product)) and gemini_ready:
        try:
            response = model_gemini.generate_content(f"Translate product name to English: {product}")
            product = response.text.strip()
        except:
            pass # ถ้าแปลไม่ได้ ก็ส่งไปทั้งอย่างนั้น (เสี่ยงดวง)

    # 3. ผสมสูตร (Product + Theme)
    theme_prompt = THEMES[theme_key]
    full_prompt = f"Professional product photography of {product}, {theme_prompt}, 8k resolution, sharp focus, commercial advertisement"
    return full_prompt

# --- 3. UI ออกแบบมาเพื่อแม่ค้า ---
st.title("🛍️ SME Pro Studio (AI ช่างภาพสินค้า)")
st.caption("ช่วยแม่ค้าไทย ถ่ายรูปสินค้าให้ปัง ใน 3 วินาที")

with st.sidebar:
    st.header("📸 ตั้งค่าสตูดิโอ")
    size_choice = st.selectbox("ขนาดภาพ:", ["สี่เหลี่ยม (IG/Shopee)", "แนวตั้ง (TikTok/Reels)", "แนวนอน (FB Cover)"])

# 1. เลือกฉาก (ใช้ง่ายๆ เป็น Radio หรือ Selectbox)
selected_theme = st.selectbox("เลือกบรรยากาศร้าน:", list(THEMES.keys()))

# 2. พิมพ์ชื่อสินค้า
user_product = st.text_input("สินค้าของคุณคืออะไร:", placeholder="เช่น สบู่สมุนไพร, ขวดน้ำหอม, แก้วกาแฟ")

# คำนวณขนาด
if "แนวตั้ง" in size_choice: w, h = 720, 1280
elif "แนวนอน" in size_choice: w, h = 1280, 720
else: w, h = 1024, 1024

if st.button("✨ ถ่ายรูปสินค้าทันที"):
    if user_product:
        # สร้าง Prompt เทพๆ
        final_prompt = create_pro_prompt(user_product, selected_theme)
        
        # สร้าง URL (ใช้ Turbo เพื่อความไว หรือ Flux เพื่อความสวย)
        # แนะนำใช้ Flux สำหรับงานสินค้า เพราะแสงเงาจะสวยกว่ามาก
        seed = random.randint(1, 999999)
        encoded = urllib.parse.quote(final_prompt)
        # บังคับใช้ Flux เพื่อคุณภาพสูงสุด (ยอมช้านิดนึงแต่คุ้ม)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&model=flux&nologo=true&seed={seed}"
        
        # แสดงผล
        st.success(f"📸 กำลังถ่ายภาพ: **{user_product}** ในฉาก **{selected_theme}**")
        
        # ใช้ไม้ตาย Direct Link (เพื่อความชัวร์ 100%)
        st.markdown(f'''
            <a href="{image_url}" target="_blank">
                <button style="background-color: #28a745; color: white; padding: 15px; width: 100%; border: none; border-radius: 10px; font-size: 18px; cursor: pointer;">
                    🚀 คลิกเพื่อดูภาพสินค้าขนาดใหญ่ (High Quality)
                </button>
            </a>
        ''', unsafe_allow_html=True)
        
        st.caption("👇 ตัวอย่าง (ถ้าเน็ตแรงจะขึ้นตรงนี้):")
        st.markdown(f'<img src="{image_url}" width="100%" style="border-radius:10px;">', unsafe_allow_html=True)
        
    else:
        st.warning("กรุณาพิมพ์ชื่อสินค้าก่อนนะคะ เช่น 'สบู่ผิวขาว'")