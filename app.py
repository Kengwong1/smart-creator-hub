import streamlit as st
import os
import time
import urllib.parse
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
import google.generativeai as genai

# ===============================
# 1. ตั้งค่าหน้าเว็บ
# ===============================
st.set_page_config(
    page_title="Smart Creator Hub v5.9",
    page_icon="🎬",
    layout="wide"
)
load_dotenv()

# ===============================
# 2. STYLE & PROMPT PRESET
# ===============================
PRO_PHOTO_SUFFIX = (
    ", professional photography, real human hands, smartphone repair tools, "
    "macro shot, highly detailed, 8k, sharp focus, NO ROBOTS, authentic workbench"
)

STYLE_PRESETS = {
    "สไตล์ปกติ (ช่างซ่อมสมจริง)": PRO_PHOTO_SUFFIX,
    "ภาพถ่ายระดับโปร (Macro)": ", high-detail macro shot, internal phone hardware, realistic textures, cinematic lighting, NO ROBOTS",
    "ฉากหลังสินค้า Affiliate": ", high-end product photography, smartphone on minimalist desk, soft light, bokeh, 8k",
    "ไทยโมเดิร์น": ", Thai local repair shop atmosphere, realistic, 8k"
}

# ===============================
# 3. Utility Functions
# ===============================
def get_gemini_keys():
    keys = st.secrets.get("GEMINI_KEYS", [])
    if isinstance(keys, str):
        keys = [keys]
    return keys


def translate_to_pro_prompt(text: str) -> str:
    keys = get_gemini_keys()
    instruction = (
        "Translate to a clean professional English image prompt. "
        "ONLY the translation, no explanations, no quotes, no bullet points."
    )

    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            res = model.generate_content(f"{instruction}\n{text}")

            clean = (
                res.text
                .replace('"', "")
                .replace("'", "")
                .replace("Prompt:", "")
                .replace("\n", " ")
                .strip()
            )

            if len(clean) > 5:
                return clean

        except Exception:
            continue

    # Fallback Translator
    return GoogleTranslator(source="th", target="en").translate(text)


def generate_thai_content(prompt_text: str):
    keys = get_gemini_keys()

    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            res = model.generate_content(
                f"{prompt_text}\n\nตอบเป็นภาษาไทย ใช้งานจริง รายละเอียดชัดเจน"
            )
            return res.text
        except Exception:
            continue

    return None


def get_img_url(prompt: str, width: int, height: int, style_suffix: str) -> str:
    full_prompt = f"{prompt}{style_suffix}"
    encoded = urllib.parse.quote(full_prompt)
    seed = time.time_ns()  # ป้องกันภาพซ้ำ
    return (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&seed={seed}"
        f"&nologo=true&model=flux"
    )

# ===============================
# 4. Sidebar
# ===============================
with st.sidebar:
    st.title("🎬 Smart Creator Hub v5.9")
    st.write("ยินดีต้อนรับค่ะคุณเก่ง ✨")
    menu = st.radio(
        "เลือกเครื่องมือ:",
        [
            "✨ Magic Content (ชุดใหญ่)",
            "🎨 เสกรูปภาพอย่างเดียว",
            "🎬 วางแผนคอนเทนต์",
            "💰 เขียนแคปชั่นป้ายยา",
        ],
    )
    st.divider()
    st.caption("v5.9 | Stable Prompt & Image Engine")

# ===============================
# 5. MAIN ZONE
# ===============================

# ---------- MAGIC CONTENT ----------
if menu == "✨ Magic Content (ชุดใหญ่)":
    st.header("✨ Magic Content Package")
    topic = st.text_input(
        "คุณอยากทำคอนเทนต์เรื่องอะไร?",
        placeholder="เช่น รีวิวซ่อมจอ iPhone 15"
    )

    col1, col2 = st.columns(2)
    with col1:
        chosen_style = st.selectbox(
            "เลือกสไตล์ภาพหน้าปก",
            list(STYLE_PRESETS.keys())
        )
    with col2:
        chosen_size = st.selectbox(
            "ขนาดภาพ",
            ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"]
        )

    if st.button("🚀 ผลิตคอนเทนต์ชุดใหญ่"):
        if not topic:
            st.warning("กรุณาใส่หัวข้อก่อนนะคะ")
            st.stop()

        with st.spinner("⏳ กำลังสร้างคอนเทนต์และภาพคุณภาพสูง..."):
            text_res = generate_thai_content(
                f"ทำคอนเทนต์เรื่อง '{topic}': "
                "1.ชื่อคลิป Viral 5 แบบ "
                "2.แคปชั่นป้ายยา Affiliate "
                "3.สคริปต์การถ่ายทำ"
            )

            if not text_res:
                st.error("⚠️ AI quota เต็ม หรือเชื่อมต่อไม่ได้ค่ะ")
                st.stop()

            eng_prompt = translate_to_pro_prompt(topic)

            if "9:16" in chosen_size:
                w, h = 540, 960
            elif "16:9" in chosen_size:
                w, h = 960, 540
            else:
                w, h = 768, 768

            img_url = get_img_url(
                eng_prompt, w, h, STYLE_PRESETS[chosen_style]
            )

            st.divider()
            st.subheader("🖼️ ภาพหน้าปกคอนเทนต์")

            if "9:16" in chosen_size:
                c1, c2, c3 = st.columns([1, 1.2, 1])
                with c2:
                    st.image(
                        img_url,
                        use_container_width=True,
                        caption="📸 ภาพ AI สำหรับคอนเทนต์นี้"
                    )
            else:
                st.image(
                    img_url,
                    use_container_width=True,
                    caption="📸 ภาพ AI สำหรับคอนเทนต์นี้"
                )

            st.markdown(
                f'<div style="text-align:center;">'
                f'<a href="{img_url}" target="_blank" '
                f'style="color:#FF4B4B;font-weight:bold;">'
                f'📥 ดาวน์โหลดภาพขนาดเต็ม</a></div>',
                unsafe_allow_html=True
            )

            st.divider()
            st.subheader("📝 รายละเอียดคอนเทนต์")
            st.markdown(text_res)

# ---------- IMAGE ONLY ----------
elif menu == "🎨 เสกรูปภาพอย่างเดียว":
    st.header("🎨 AI ศิลปินเสกรูปภาพ")
    img_desc = st.text_area("อยากได้รูปอะไรคะ?")

    col1, col2 = st.columns(2)
    with col1:
        style = st.selectbox(
            "เลือกสไตล์",
            list(STYLE_PRESETS.keys())
        )
    with col2:
        size = st.selectbox(
            "เลือกขนาด",
            ["แนวตั้ง (9:16)", "แนวนอน (16:9)", "จัตุรัส (1:1)"]
        )

    if st.button("✨ เริ่มวาดรูป"):
        if not img_desc:
            st.warning("กรุณาอธิบายภาพก่อนนะคะ")
            st.stop()

        with st.spinner("🎨 กำลังวาดรูปภาพ..."):
            eng_prompt = translate_to_pro_prompt(img_desc)

            if "9:16" in size:
                w, h = 540, 960
            elif "16:9" in size:
                w, h = 960, 540
            else:
                w, h = 768, 768

            final_url = get_img_url(
                eng_prompt, w, h, STYLE_PRESETS[style]
            )

            if "9:16" in size:
                c1, c2, c3 = st.columns([1, 1.2, 1])
                with c2:
                    st.image(final_url, use_container_width=True)
            else:
                st.image(final_url, use_container_width=True)

            st.markdown(f"[📥 ดาวน์โหลดรูปภาพ]({final_url})")
