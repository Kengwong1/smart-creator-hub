import streamlit as st
import requests
import io
from PIL import Image
import urllib.parse
import random
import pandas as pd

# --- 1. SETUP & UI CONFIG ---
st.set_page_config(page_title="Creator Hub v12.8", page_icon="🎨", layout="centered")

# --- 2. ENGINE (v12.8: มาตรฐาน Pro + Fast Mode) ---
def generate_image_v5(prompt_text, width, height, model_type):
    quality_prompts = "high resolution, photorealistic, cinematic lighting, sharp focus, 8k"
    full_prompt = f"{prompt_text}, {quality_prompts}"
    encoded_prompt = urllib.parse.quote(full_prompt)
    
    random_seed = random.randint(1, 1000000)
    # เลือกระหว่าง 'flux' (สวยกริบ) หรือ 'turbo' (ไวกริ๊บ)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model={model_type}&nologo=true&seed={random_seed}"
    
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        return None
    except:
        return None

# --- 3. MAIN INTERFACE ---
st.title("🎨 AI สร้างภาพมาตรฐานโปร (v12.8)")

with st.expander("⚙️ ตั้งค่าขนาดและโหมดความเร็ว"):
    mode = st.radio("🚀 โหมดการสร้าง:", ["เน้นสวยละเอียด (Flux - ช้าหน่อย)", "เน้นด่วนทันใจ (Turbo - ไวมาก)"], index=0)
    model_key = "flux" if "Flux" in mode else "turbo"
    
    target_size = st.selectbox(
        "เลือกขนาดมาตรฐาน (Canva/CapCut):",
        [
            "TikTok / Reels / Shorts (แนวตั้ง 9:16)",
            "YouTube / Facebook Video (แนวนอน 16:9)",
            "Instagram Feed / Profile (จัตุรัส 1:1)",
            "Canva Presentation / สื่อเรียน (4:3)"
        ]
    )

# ล็อกขนาดตามมาตรฐานสากล
if "9:16" in target_size: w, h = 720, 1280
elif "16:9" in target_size: w, h = 1280, 720
elif "4:3" in target_size: w, h = 1024, 768
else: w, h = 1024, 1024

prompt = st.text_area("อธิบายภาพที่ต้องการ:", placeholder="เช่น: A modern luxury coffee shop, warm atmosphere")

if st.button("✨ เนรมิตภาพ"):
    if prompt:
        with st.spinner(f"⏳ กำลังใช้โหมด {model_key} วาดภาพให้คุณเก่งนะคะ..."):
            img = generate_image_v5(prompt, w, h, model_key)
            if img:
                st.image(img, width=450, caption=f"สไตล์: {target_size} | โหมด: {model_key}")
                
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("📥 ดาวน์โหลดไฟล์จริงไปใช้ตัดต่อ", buf.getvalue(), "creative_work.png", "image/png")
            else:
                st.error("ขออภัยค่ะ ระบบคิวเต็ม ลองกดใหม่อีกครั้งนะคะ")
    else:
        st.warning("ช่วยพิมพ์คำอธิบายภาพก่อนนะค่ะ")