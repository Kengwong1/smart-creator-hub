import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re
from PIL import Image
import requests
from io import BytesIO

# --- 1. CONFIG ---
st.set_page_config(page_title="SME Pro Studio v16.2", page_icon="🛍️", layout="wide")

# --- CSS: บังคับเมาส์รูปมือ + จัด Font ---
st.markdown("""
<style>
    div[data-baseweb="select"] > div, button { cursor: pointer !important; }
    .stSlider { padding-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC ---
THEMES = {
    "✨ หรูหรา (Luxury)": "placed on a black marble table, golden lighting, elegant atmosphere",
    "🌿 ธรรมชาติ (Organic)": "placed on a natural stone, surrounded by green leaves, soft sunlight",
    "⚪ มินิมอล (Minimal)": "placed on a clean white podium, soft pastel background, studio lighting",
    "🏙️ นีออน (Cyberpunk)": "neon lights background, blue and pink lighting, futuristic product shot"
}

LOCAL_DICT = {"สบู่": "soap bar", "ครีม": "cream jar", "เซรั่ม": "serum bottle", "น้ำหอม": "perfume bottle"}

try:
    genai.configure(api_key=st.secrets["GEMINI_KEYS"])
    model_gemini = genai.GenerativeModel('gemini-1.5-flash')
    gemini_ready = True
except:
    gemini_ready = False

def create_pro_prompt(product_input, theme_key):
    product_eng = product_input
    for thai, eng in LOCAL_DICT.items():
        if thai in product_eng: product_eng = product_eng.replace(thai, eng)
    
    shape_fix = ""
    if "soap" in product_eng.lower():
        shape_fix = ", perfectly shaped rectangular bar, symmetrical form"
    
    theme_prompt = THEMES[theme_key]
    full_prompt = f"Professional product photography of {product_eng}{shape_fix}, {theme_prompt}, blank product surface, no text, no label, 8k resolution"
    return full_prompt

def load_image_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

# --- 3. UI ---
st.title("🛍️ SME Pro Studio (v16.2: ปรับแต่งง่าย)")

# แบ่งหน้าจอใหญ่: ซ้าย (สร้าง) vs ขวา (แต่ง)
main_col1, main_col2 = st.columns([1, 2])

# === ฝั่งซ้าย: สร้างภาพ (Create) ===
with main_col1:
    st.info("🎨 1. สร้างภาพสินค้า")
    selected_theme = st.selectbox("เลือกธีม:", list(THEMES.keys()))
    user_product = st.text_input("สินค้า:", placeholder="เช่น สบู่, ครีม")
    
    if st.button("✨ สร้างฉากใหม่", use_container_width=True):
        if user_product:
            with st.spinner("⏳ กำลังเนรมิตฉาก..."):
                final_prompt = create_pro_prompt(user_product, selected_theme)
                seed = random.randint(1, 999999)
                encoded = urllib.parse.quote(final_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&nologo=true&seed={seed}"
                
                st.session_state.generated_image = load_image_from_url(image_url)
                st.success("✅ ภาพมาแล้ว!")

# === ฝั่งขวา: แต่งภาพ (Edit) ===
with main_col2:
    st.success("🖼️ 2. แปะโลโก้ & จบงาน")
    
    if 'generated_image' in st.session_state:
        uploaded_logo = st.file_uploader("เลือกไฟล์โลโก้ (PNG พื้นใส)", type=["png", "jpg"])
        
        bg_image = st.session_state.generated_image.copy()
        
        # แบ่งครึ่งในโซนแต่งภาพ: ซ้าย(รูป) - ขวา(ปุ่มปรับ)
        edit_c1, edit_c2 = st.columns([1.5, 1])
        
        # เตรียมตัวแปรปรับค่า
        logo_size = 150
        rotation = 0
        x_pos = 512
        y_pos = 512
        
        # --- โซนปุ่มปรับ (อยู่ทางขวา) ---
        with edit_c2:
            st.write("🎛️ **แผงควบคุม**")
            if uploaded_logo:
                logo_size = st.slider("🔍 ขนาด", 10, 500, 150)
                rotation = st.slider("🔄 หมุน", -180, 180, 0)
                x_pos = st.slider("↔️ แนวนอน", 0, 1024, 512)
                y_pos = st.slider("↕️ แนวตั้ง", 0, 1024, 512)
            else:
                st.info("👈 อัปโหลดโลโก้ก่อนนะครับ ถึงจะปรับค่าได้")

        # --- โซนรูปภาพ (อยู่ทางซ้าย) ---
        with edit_c1:
            if uploaded_logo:
                logo = Image.open(uploaded_logo)
                
                # 1. ปรับขนาด
                logo.thumbnail((logo_size, logo_size))
                # 2. หมุน
                logo = logo.rotate(-rotation, expand=True, resample=Image.BICUBIC)
                
                # 3. แปะ
                logo_w, logo_h = logo.size
                offset = (x_pos - logo_w//2, y_pos - logo_h//2)
                try:
                    bg_image.paste(logo, offset, logo)
                except:
                    bg_image.paste(logo, offset)
            
            # แสดงภาพ (ขนาดพอดีตา ไม่ต้องเลื่อน)
            st.image(bg_image, caption="ภาพตัวอย่าง", use_container_width=True)
            
            # ปุ่มดาวน์โหลด (อยู่ใต้ภาพเลย สะดวกๆ)
            buf = BytesIO()
            bg_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button(
                label="💾 บันทึกภาพ (High Quality)",
                data=byte_im,
                file_name="final_product.png",
                mime="image/png",
                use_container_width=True
            )
            
    else:
        st.markdown("<div style='text-align:center; padding:50px; color:#aaa;'>👈 สร้างภาพที่ฝั่งซ้ายก่อนนะครับ</div>", unsafe_allow_html=True)