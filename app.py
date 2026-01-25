import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re
from PIL import Image
import requests
from io import BytesIO

# --- 1. CONFIG ---
st.set_page_config(page_title="SME Pro Studio v16.1", page_icon="🛍️", layout="wide")

# --- CSS HACK: บังคับเมาส์รูปมือ + จัดการขนาดภาพ ---
st.markdown("""
<style>
    /* บังคับให้ปุ่มและ Selectbox มีเมาส์รูปมือ */
    div[data-baseweb="select"] > div, button {
        cursor: pointer !important;
    }
    /* ปรับแต่ง Slider ให้ดูง่ายขึ้น */
    div.stSlider > div[data-baseweb="slider"] > div {
        background-color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC ---
THEMES = {
    "✨ หรูหรา (Luxury)": "placed on a black marble table, golden lighting, elegant atmosphere, bokeh background",
    "🌿 ธรรมชาติ (Organic)": "placed on a natural stone, surrounded by green leaves, soft sunlight, organic style",
    "⚪ มินิมอล (Minimal)": "placed on a clean white podium, soft pastel background, studio lighting, minimal aesthetic",
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
st.title("🛍️ SME Pro Studio (v16.1: หมุนโลโก้ + UI ใหม่)")

col1, col2 = st.columns([1, 1.5]) # ปรับสัดส่วนใหม่ให้ซ้ายขวาพอๆ กัน

with col1:
    st.info("🎨 1. สร้างภาพสินค้า")
    selected_theme = st.selectbox("เลือกธีม:", list(THEMES.keys()))
    user_product = st.text_input("สินค้า:", placeholder="เช่น สบู่, ขวดครีม")
    
    if st.button("✨ สร้างภาพพื้นหลัง (กดเลย)"):
        if user_product:
            with st.spinner("⏳ กำลังจัดแสง..."):
                final_prompt = create_pro_prompt(user_product, selected_theme)
                seed = random.randint(1, 999999)
                encoded = urllib.parse.quote(final_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&nologo=true&seed={seed}"
                
                st.session_state.generated_image = load_image_from_url(image_url)
                st.success("✅ ได้ภาพแล้ว! ไปแปะโลโก้กันต่อ")

with col2:
    st.success("🖼️ 2. แต่งภาพ & แปะโลโก้")
    
    if 'generated_image' in st.session_state:
        # แสดงผลลัพธ์ (จำกัดความกว้างไว้ที่ 500px เพื่อไม่ให้ล้นจอ)
        st.write("ตัวอย่างภาพปัจจุบัน:")
        preview_container = st.empty()
        
        # ส่วนอัปโหลด
        uploaded_logo = st.file_uploader("เลือกไฟล์โลโก้ (PNG พื้นใส)", type=["png", "jpg"])
        
        bg_image = st.session_state.generated_image.copy()
        
        if uploaded_logo:
            logo = Image.open(uploaded_logo)
            
            # --- แผงควบคุม (Control Panel) ---
            with st.expander("🎛️ ปรับแต่งโลโก้ (กดเพื่อเปิด)", expanded=True):
                c1, c2 = st.columns(2)
                with c1: 
                    logo_size = st.slider("🔍 ขนาด", 10, 500, 150)
                    rotation = st.slider("🔄 หมุน (องศา)", -180, 180, 0)
                with c2: 
                    x_pos = st.slider("↔️ แนวนอน", 0, 1024, 512)
                    y_pos = st.slider("↕️ แนวตั้ง", 0, 1024, 512)
            
            # 1. ปรับขนาด
            logo.thumbnail((logo_size, logo_size))
            
            # 2. หมุนภาพ (ใช้ expand=True เพื่อไม่ให้ขอบขาด)
            logo = logo.rotate(-rotation, expand=True, resample=Image.BICUBIC)
            
            # 3. แปะลงภาพ
            # คำนวณจุดกึ่งกลางใหม่หลังจากหมุน
            logo_w, logo_h = logo.size
            bg_w, bg_h = bg_image.size
            offset = (x_pos - logo_w//2, y_pos - logo_h//2)
            
            try:
                bg_image.paste(logo, offset, logo)
            except:
                bg_image.paste(logo, offset)
        
        # แสดงภาพในกรอบที่ขนาดกำลังดี (width=500)
        preview_container.image(bg_image, width=500, caption="ภาพตัวอย่าง (ย่อขนาดให้ดูง่าย)")
        
        # ปุ่มดาวน์โหลด
        buf = BytesIO()
        bg_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="💾 ดาวน์โหลดภาพขนาดจริง (High Quality)",
            data=byte_im,
            file_name="final_product.png",
            mime="image/png",
            use_container_width=True
        )
    else:
        st.markdown(
            """
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; color: #555;'>
                👈 สร้างภาพที่ฝั่งซ้ายก่อนนะครับ<br>
                แล้วพื้นที่แต่งภาพจะปรากฏตรงนี้
            </div>
            """, unsafe_allow_html=True
        )