import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import re

# --- CONFIG ---
st.set_page_config(
    page_title="Krobjang AI — วิเคราะห์สินค้า TikTok Affiliate",
    page_icon="🤖",
    layout="centered"
)

# --- CSS ---
st.markdown("""
<style>
    .main { max-width: 680px; margin: 0 auto; }
    .result-box {
        background: #1a1a2e;
        border: 1px solid #fe2c55;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .result-title {
        color: #fe2c55;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .caption-text {
        font-size: 16px;
        line-height: 1.7;
        color: #ffffff;
    }
    .hashtag-text {
        color: #6eb5ff;
        font-size: 14px;
        line-height: 1.8;
    }
    .badge-free {
        background: #333;
        color: #aaa;
        padding: 2px 10px;
        border-radius: 50px;
        font-size: 12px;
    }
    .badge-pro {
        background: linear-gradient(135deg, #fe2c55, #ff6b35);
        color: white;
        padding: 2px 10px;
        border-radius: 50px;
        font-size: 12px;
    }
    div[data-testid="stButton"] button {
        background: linear-gradient(135deg, #fe2c55, #ff6b35);
        color: white;
        border: none;
        border-radius: 50px;
        font-weight: bold;
        padding: 12px 24px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- GEMINI SETUP ---
try:
    genai.configure(api_key=st.secrets["GEMINI_KEYS"])
    model = genai.GenerativeModel('gemini-1.0-pro')
    gemini_ready = True
except:
    gemini_ready = False

# --- SESSION STATE ---
if 'quota_used' not in st.session_state:
    st.session_state.quota_used = 0
if 'is_pro' not in st.session_state:
    st.session_state.is_pro = False

FREE_LIMIT = 5

# --- FUNCTIONS ---
def detect_platform(url):
    if 'tiktok.com' in url:
        return 'TikTok'
    elif 'shopee.co.th' in url:
        return 'Shopee'
    elif 'lazada.co.th' in url:
        return 'Lazada'
    return None

def fetch_page_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(res.text, 'html.parser')
        # ดึงแค่ text ที่เป็นประโยชน์
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text[:3000]  # จำกัดไม่เกิน 3000 ตัวอักษร
    except Exception as e:
        return None

def analyze_with_ai(platform, page_text, url):
    prompt = f"""คุณคือผู้เชี่ยวชาญด้าน TikTok Affiliate Marketing ในไทย

วิเคราะห์สินค้าจาก{platform} จากข้อมูลด้านล่างนี้:
URL: {url}
ข้อมูล: {page_text if page_text else 'ไม่สามารถดึงข้อมูลได้ วิเคราะห์จาก URL'}

ตอบเป็นภาษาไทย แบ่งเป็น 4 ส่วนนี้เท่านั้น:

1.) จุดเด่นของสินค้า
- บอกจุดเด่น 3 ข้อ สั้นๆ กระชับ

2.) ไอเดียแคปชั่นทำเงิน
เขียนแคปชั่นพร้อมโพสต์ได้เลย ใช้จิตวิทยาการตลาด กระตุ้นให้อยากซื้อ ใช้ Emoji เหมาะสม

3.) Hashtag แนะนำ
แนะนำ 5-7 hashtag ที่เหมาะกับสินค้าและ TikTok ไทย

4.) คำแนะนำเพิ่มเติม
เทคนิคการโพสต์ให้ยอดขายดี 1-2 ข้อ"""

    response = model.generate_content(prompt)
    return response.text

def parse_result(text):
    result = {'points': '', 'caption': '', 'hashtags': '', 'tips': ''}
    
    points_match = re.search(r'1[.)]\s*จุดเด่น[^\n]*\n([\s\S]*?)(?=\n2[.)]|\Z)', text)
    caption_match = re.search(r'2[.)]\s*ไอเดียแคปชั่น[^\n]*\n([\s\S]*?)(?=\n3[.)]|\Z)', text)
    hashtag_match = re.search(r'3[.)]\s*Hashtag[^\n]*\n([\s\S]*?)(?=\n4[.)]|\Z)', text)
    tips_match = re.search(r'4[.)]\s*คำแนะนำ[^\n]*\n([\s\S]*?)(?=\n5[.)]|\Z)', text)
    
    if points_match: result['points'] = points_match.group(1).strip()
    if caption_match: result['caption'] = caption_match.group(1).strip()
    if hashtag_match: result['hashtags'] = hashtag_match.group(1).strip().replace('\n', ' ')
    if tips_match: result['tips'] = tips_match.group(1).strip()
    
    return result

# --- UI ---
st.markdown("## 🤖 Krobjang AI")
st.markdown("วิเคราะห์สินค้า ได้แคปชั่น + Hashtag พร้อมโพสต์ใน 10 วินาที")
st.divider()

# Quota badge
if st.session_state.is_pro:
    st.markdown('<span class="badge-pro">⭐ Pro — ไม่จำกัดครั้ง</span>', unsafe_allow_html=True)
else:
    remaining = FREE_LIMIT - st.session_state.quota_used
    st.markdown(f'<span class="badge-free">🆓 Free — เหลือ {remaining}/{FREE_LIMIT} ครั้งวันนี้</span>', unsafe_allow_html=True)

st.markdown("")

# License Key input (Pro)
with st.expander("🔑 มี License Key? กดที่นี่"):
    key_input = st.text_input("ใส่ License Key:", placeholder="KROB-XXXX-XXXX", label_visibility="collapsed")
    if st.button("ยืนยัน Key", key="verify_key"):
        # ตรวจสอบ Key (ใส่ Key จริงที่ต้องการได้ที่นี่)
        valid_keys = st.secrets.get("LICENSE_KEYS", "").split(",")
        if key_input.strip() in valid_keys:
            st.session_state.is_pro = True
            st.success("✅ เปิดใช้งาน Pro แล้ว!")
        else:
            st.error("❌ Key ไม่ถูกต้อง ติดต่อเราทาง Line ครับ")

st.markdown("")

# URL Input
platform_options = ['TikTok 🎵', 'Shopee 🛍️', 'Lazada 🟠']
url_input = st.text_input(
    "วางลิงก์สินค้าที่นี่:",
    placeholder="https://www.tiktok.com/... หรือ https://shopee.co.th/...",
    label_visibility="visible"
)

# Analyze button
if st.button("🚀 วิเคราะห์เลย!", key="analyze"):
    if not url_input:
        st.warning("⚠️ กรุณาใส่ลิงก์สินค้าก่อนนะครับ")
    elif not gemini_ready:
        st.error("❌ ระบบ AI ยังไม่พร้อม กรุณาติดต่อแอดมินครับ")
    else:
        platform = detect_platform(url_input)
        if not platform:
            st.error("❌ รองรับเฉพาะ TikTok, Shopee และ Lazada ครับ")
        elif not st.session_state.is_pro and st.session_state.quota_used >= FREE_LIMIT:
            st.error("🔒 ใช้ครบโควต้าวันนี้แล้วครับ (5 ครั้ง/วัน)")
            st.info("อัปเกรดเป็น Pro เพื่อใช้งานไม่จำกัด → [ติดต่อทาง Line](https://line.me/ti/p/@vfk5903b)")
        else:
            with st.spinner(f"⏳ กำลังวิเคราะห์จาก {platform}..."):
                page_text = fetch_page_text(url_input)
                raw_result = analyze_with_ai(platform, page_text, url_input)
                parsed = parse_result(raw_result)
                
                if not st.session_state.is_pro:
                    st.session_state.quota_used += 1

            st.success(f"✅ วิเคราะห์เสร็จแล้วครับ! (จาก {platform})")
            st.divider()

            # จุดเด่น
            if parsed['points']:
                st.markdown('<div class="result-box"><div class="result-title">✨ จุดเด่นของสินค้า</div>' +
                    parsed['points'].replace('\n', '<br>') + '</div>', unsafe_allow_html=True)

            # แคปชั่น
            if parsed['caption']:
                st.markdown('<div class="result-box"><div class="result-title">✏️ แคปชั่นทำเงิน</div>' +
                    f'<div class="caption-text">{parsed["caption"]}</div></div>', unsafe_allow_html=True)
                st.code(parsed['caption'], language=None)

            # Hashtag
            if parsed['hashtags']:
                st.markdown('<div class="result-box"><div class="result-title">#️⃣ Hashtag แนะนำ</div>' +
                    f'<div class="hashtag-text">{parsed["hashtags"]}</div></div>', unsafe_allow_html=True)
                st.code(parsed['hashtags'], language=None)

            # Copy ทั้งหมด
            if parsed['caption'] and parsed['hashtags']:
                full_text = f"{parsed['caption']}\n\n{parsed['hashtags']}"
                st.code(full_text, language=None)
                st.caption("👆 Copy แคปชั่น + Hashtag พร้อมโพสต์ได้เลยครับ")

            # Tips
            if parsed['tips']:
                st.info(f"💡 **คำแนะนำ:** {parsed['tips']}")

st.divider()
st.markdown("""
<div style='text-align:center; color:#666; font-size:13px;'>
    🆓 Free: 5 ครั้ง/วัน · ⭐ Pro: 149 บาท/เดือน<br>
    <a href="https://line.me/ti/p/@vfk5903b" style="color:#fe2c55;">💬 ติดต่อซื้อ Pro ผ่าน Line</a>
</div>
""", unsafe_allow_html=True)
