import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re

# --- 1. CONFIG ---
st.set_page_config(page_title="SME Pro Studio v15.1", page_icon="🧼", layout="centered")

# --- 2. BACKEND: PROMPT ENGINEERING (สูตรลับช่างภาพ) ---
THEMES = {
    "✨ หรูหรา (Luxury)": "placed on a black marble table, golden lighting, elegant atmosphere, bokeh background, high-end product photography",
    "🌿 ธรรมชาติ (Organic)": "placed on a natural stone, surrounded by green leaves and water ripples, soft sunlight, organic style, fresh feeling",
    "⚪ มินิมอล (Minimal)": "placed on a clean white podium, soft pastel background, studio lighting, minimal aesthetic, clean composition",
    "🏮 ตรุษจีน/มงคล (Chinese New Year)": "red background with gold accents, chinese lanterns, festive atmosphere, lucky style, bright lighting",
    "🏙️ นีออน (Cyberpunk)": "neon lights background, blue and pink lighting, futuristic product shot, reflection on glass floor"
}

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

def create_pro_prompt(product_input, theme_key):
    # 1. แปลคำศัพท์
    product_eng = product_input
    for thai, eng in LOCAL_DICT.items():
        if thai in product_eng: product_eng = product_eng.replace(thai, eng)
    
    if bool(re.search('[ก-ฮ]', product_eng)) and gemini_ready:
        try:
            response = model_gemini.generate_content(f"Translate product name to English: {product_eng}")
            product_eng = response.text.strip()
        except:
            pass

    # 2. --- จุดแก้สำคัญ (v15.1 Shape Fixer) ---
    # ถ้าเป็นสบู่ ให้เพิ่มคำสั่งบังคับทรงสี่เหลี่ยมสมมาตร
    shape_fix = ""
    if "soap" in product_eng.lower():
        shape_fix = ", perfectly shaped rectangular bar, symmetrical form, sharp edges, clean uniform shape"

    # 3. ผสมสูตร
    theme_prompt = THEMES[theme_key]
    # เอา shape_fix ไปวางต่อท้ายชื่อสินค้าทันที
    full_prompt = f"Professional product photography of {product_eng}{shape_fix}, {theme_prompt}, 8k resolution, sharp focus, commercial advertisement"
    return full_prompt, product_eng

# --- 3. UI ---
st.title("🛍️ SME Pro Studio (v15.1: แก้ทรงสบู่)")
st.caption("เพิ่มระบบล็อกรูปทรงสบู่ให้ตรงเป๊ะ ไม่เบี้ยว")

with st.sidebar:
    st.header("📸 ตั้งค่าสตูดิโอ")
    size_choice = st.selectbox("ขนาดภาพ:", ["สี่เหลี่ยม (IG/Shopee)", "แนวตั้ง (TikTok/Reels)", "แนวนอน (FB Cover)"])
    selected_theme = st.selectbox("เลือกบรรยากาศร้าน:", list(THEMES.keys()))

user_product = st.text_input("สินค้าของคุณคืออะไร:", placeholder="เช่น สบู่สมุนไพร, ขวดน้ำหอม")

if "แนวตั้ง" in size_choice: w, h = 720, 1280
elif "แนวนอน" in size_choice: w, h = 1280, 720
else: w, h = 1024, 1024

if st.button("✨ ถ่ายรูปสินค้าทันที"):
    if user_product:
        # สร้าง Prompt
        final_prompt, eng_name = create_pro_prompt(user_product, selected_theme)
        
        # สร้าง URL (ใช้ Flux)
        seed = random.randint(1, 999999)
        encoded = urllib.parse.quote(final_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&model=flux&nologo=true&seed={seed}"
        
        # แสดงผล
        st.success(f"📸 กำลังถ่ายภาพ: **{user_product}** (ระบบล็อกทรงแล้ว)")
        st.caption(f"🔒 Prompt ที่ใช้: ...{eng_name}, perfectly shaped rectangular bar, symmetrical...")

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
        st.warning("กรุณาพิมพ์ชื่อสินค้าก่อนนะคะ")