import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re
from PIL import Image
import requests
from io import BytesIO
from streamlit_image_coordinates import streamlit_image_coordinates

# --- 1. CONFIG ---
st.set_page_config(page_title="SME Pro Studio v16.4", page_icon="🧼", layout="wide")

# --- CSS ---
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
    
    # --- จุดแก้สำคัญ (Geometry Lock) ---
    shape_fix = ""
    if "soap" in product_eng.lower():
        # เปลี่ยนคำสั่ง: บังคับเป็น "กล่องสี่เหลี่ยมแข็ง (Cuboid)" และ "Mockup" เพื่อให้เหลี่ยมคม
        shape_fix = ", rectangular cuboid shape, sharp straight edges, symmetrical perspective, product packaging mockup, front view"
    elif "box" in product_eng.lower() or "กล่อง" in product_input:
         shape_fix = ", rectangular box, sharp corners, straight lines, packaging mockup"

    theme_prompt = THEMES[theme_key]
    
    # ย้าย shape_fix ไปไว้หน้าสุด เพื่อให้ AI ให้ความสำคัญสูงสุด
    # และเพิ่ม 'telephoto lens' เพื่อลดการบิดเบี้ยวของภาพ (Perspective Distortion)
    full_prompt = f"Professional product photography of {product_eng}{shape_fix}, {theme_prompt}, blank product surface, no text, no label, 8k resolution, telephoto lens, architectural symmetry"
    return full_prompt

def load_image_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

# --- INIT SESSION STATE ---
if 'logo_x' not in st.session_state: st.session_state.logo_x = 512
if 'logo_y' not in st.session_state: st.session_state.logo_y = 512

# --- 3. UI ---
st.title("🛍️ SME Pro Studio (v16.4: ล็อกทรงสบู่คมกริบ)")

main_col1, main_col2 = st.columns([1, 2])

# === ฝั่งซ้าย: สร้างภาพ ===
with main_col1:
    st.info("🎨 1. สร้างภาพสินค้า")
    selected_theme = st.selectbox("เลือกธีม:", list(THEMES.keys()))
    user_product = st.text_input("สินค้า:", placeholder="เช่น สบู่, ครีม")
    
    if st.button("✨ สร้างฉากใหม่", use_container_width=True):
        if user_product:
            with st.spinner("⏳ กำลังจัดแสงและล็อกรูปทรง..."):
                final_prompt = create_pro_prompt(user_product, selected_theme)
                seed = random.randint(1, 999999)
                encoded = urllib.parse.quote(final_prompt)
                # ใช้ Flux เหมือนเดิม
                image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&nologo=true&seed={seed}"
                
                st.session_state.generated_image = load_image_from_url(image_url)
                st.session_state.logo_x = 512
                st.session_state.logo_y = 512
                st.success("✅ ได้ภาพทรงสวยแล้ว!")

# === ฝั่งขวา: แต่งภาพ ===
with main_col2:
    st.success("🖼️ 2. แปะโลโก้ (จิ้มบนภาพเพื่อวาง)")
    
    if 'generated_image' in st.session_state:
        uploaded_logo = st.file_uploader("เลือกไฟล์โลโก้ (PNG พื้นใส)", type=["png", "jpg"])
        bg_image = st.session_state.generated_image.copy()
        
        edit_c1, edit_c2 = st.columns([1.5, 1])
        
        with edit_c2:
            st.write("🎛️ **ปรับขนาด/หมุน**")
            if uploaded_logo:
                logo_size = st.slider("🔍 ขนาด", 10, 500, 150)
                rotation = st.slider("🔄 หมุน", -180, 180, 0)
                st.info("💡 **วิธีใช้:** จิ้มบนภาพซ้ายมือ เพื่อวางโลโก้ได้เลยครับ")
            else:
                st.info("👈 อัปโหลดโลโก้ก่อนนะครับ")

        with edit_c1:
            if uploaded_logo:
                logo = Image.open(uploaded_logo)
                logo.thumbnail((logo_size, logo_size))
                logo = logo.rotate(-rotation, expand=True, resample=Image.BICUBIC)
                
                logo_w, logo_h = logo.size
                offset = (st.session_state.logo_x - logo_w//2, st.session_state.logo_y - logo_h//2)
                
                try:
                    bg_image.paste(logo, offset, logo)
                except:
                    bg_image.paste(logo, offset)
            
            # Click-to-place Widget
            coords = streamlit_image_coordinates(bg_image, use_column_width=True)
            
            if coords:
                st.session_state.logo_x = coords["x"]
                st.session_state.logo_y = coords["y"]
                st.rerun()

            buf = BytesIO()
            bg_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button(label="💾 บันทึกภาพ", data=byte_im, file_name="final_product.png", mime="image/png", use_container_width=True)
            
    else:
        st.markdown("<div style='text-align:center; padding:50px; color:#aaa;'>👈 สร้างภาพที่ฝั่งซ้ายก่อนนะครับ</div>", unsafe_allow_html=True)