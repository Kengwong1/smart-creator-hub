import streamlit as st
import random
import urllib.parse
import google.generativeai as genai
import re
from PIL import Image
import requests
from io import BytesIO

# --- 1. CONFIG ---
st.set_page_config(page_title="SME Pro Studio v16.0", page_icon="🛍️", layout="wide") # เปลี่ยนเป็น wide เพื่อให้ทำงานง่าย

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
    
    # เพิ่มคำสั่ง: ห้ามมีตัวหนังสือ (no text) เพื่อให้เราเอาโลโก้ไปแปะง่ายๆ
    shape_fix = ""
    if "soap" in product_eng.lower():
        shape_fix = ", perfectly shaped rectangular bar, symmetrical form"
    
    theme_prompt = THEMES[theme_key]
    full_prompt = f"Professional product photography of {product_eng}{shape_fix}, {theme_prompt}, blank product surface, no text, no label, 8k resolution"
    return full_prompt

# ฟังก์ชันโหลดภาพจาก URL มาเป็นภาพที่แก้ไขได้
def load_image_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

# --- 3. UI ---
st.title("🛍️ SME Pro Studio (v16.0: แปะโลโก้ได้เลย!)")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. สร้างภาพสินค้า")
    selected_theme = st.selectbox("เลือกธีม:", list(THEMES.keys()))
    user_product = st.text_input("สินค้า:", placeholder="เช่น สบู่, ขวดครีม")
    
    if st.button("✨ สร้างภาพพื้นหลัง"):
        if user_product:
            with st.spinner("กำลังจัดแสงและถ่ายภาพ..."):
                final_prompt = create_pro_prompt(user_product, selected_theme)
                seed = random.randint(1, 999999)
                encoded = urllib.parse.quote(final_prompt)
                # ใช้ Flux เพื่อความสวย
                image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&nologo=true&seed={seed}"
                
                # โหลดภาพเก็บไว้ใน Session State (ความจำชั่วคราว)
                st.session_state.generated_image = load_image_from_url(image_url)
                st.success("ได้ภาพแล้ว! ไปขั้นตอนที่ 2 เพื่อแปะโลโก้")

with col2:
    st.header("2. แปะโลโก้ (Brand)")
    
    # ถ้ามีภาพที่สร้างเสร็จแล้ว ให้แสดงเครื่องมือแต่งภาพ
    if 'generated_image' in st.session_state:
        # ส่วนอัปโหลดโลโก้
        uploaded_logo = st.file_uploader("อัปโหลดโลโก้ (พื้นใส PNG ดีที่สุด)", type=["png", "jpg", "jpeg"])
        
        # แสดงภาพพื้นหลัง (Product)
        bg_image = st.session_state.generated_image.copy() # ก๊อปปี้มาเพื่อไม่ให้ภาพต้นฉบับเสีย
        
        if uploaded_logo:
            # โหลดโลโก้
            logo = Image.open(uploaded_logo)
            
            # --- เครื่องมือปรับแต่ง (Sliders) ---
            st.write("🎛️ ปรับตำแหน่งโลโก้:")
            c1, c2, c3 = st.columns(3)
            with c1: logo_size = st.slider("ขนาด", 10, 500, 150)
            with c2: x_pos = st.slider("ซ้าย-ขวา", 0, 1024, 512)
            with c3: y_pos = st.slider("บน-ล่าง", 0, 1024, 512)
            
            # ปรับขนาดโลโก้
            logo.thumbnail((logo_size, logo_size))
            
            # แปะโลโก้ลงบนภาพ (Paste)
            # ต้องคำนวณตำแหน่งกึ่งกลางให้เป๊ะ
            bg_w, bg_h = bg_image.size
            logo_w, logo_h = logo.size
            offset = (x_pos - logo_w//2, y_pos - logo_h//2)
            
            # แปะแบบพื้นใส (Transparency Mask)
            try:
                bg_image.paste(logo, offset, logo)
            except:
                # กรณีไฟล์โลโก้ไม่มีพื้นใส (JPG) ให้แปะทับเลย
                bg_image.paste(logo, offset)
        
        # แสดงผลลัพธ์สุดท้าย
        st.image(bg_image, caption="ภาพสินค้าพร้อมขาย", use_container_width=True)
        
        # ปุ่มดาวน์โหลด (แปลงภาพเป็นปุ่มให้กด)
        buf = BytesIO()
        bg_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="📥 ดาวน์โหลดภาพนี้ไปขายของ!",
            data=byte_im,
            file_name="my_product_final.png",
            mime="image/png"
        )
    else:
        st.info("👈 กรุณาสร้างภาพที่ฝั่งซ้ายก่อนนะครับ")