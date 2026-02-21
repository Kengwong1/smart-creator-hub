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
    .api-box {
        background: #0d0d1a;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .api-title {
        color: #aaa;
        font-size: 13px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'quota_used' not in st.session_state:
    st.session_state.quota_used = 0
if 'is_pro' not in st.session_state:
    st.session_state.is_pro = False
if 'gemini_key' not in st.session_state:
    st.session_state.gemini_key = ""
if 'model' not in st.session_state:
    st.session_state.model = None

FREE_LIMIT = 5

# --- FUNCTIONS ---
def init_gemini(api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-8b')
        return model, True
    except:
        return None, False

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
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text[:3000]
    except:
        return None

def analyze_with_ai(model, platform, page_text, url):
    prompt = f"""คุณคือ "Krobjang AI" ผู้เชี่ยวชาญด้านการตลาดดิจิทัลและ TikTok Affiliate ที่เก่งที่สุดในประเทศไทย

วิเคราะห์สินค้าจาก{platform}:
URL: {url}
ข้อมูล: {page_text if page_text else 'วิเคราะห์จาก URL'}

ตอบเป็นภาษาไทย 100% เท่านั้น ห้ามใช้ภาษาอื่นแม้แต่คำเดียว แบ่งเป็น 4 ส่วน:

1.) จุดเด่นของสินค้า
- บอกจุดเด่น 3 ข้อ เฉพาะเจาะจงกับสินค้านี้เท่านั้น

2.) แคปชั่นทำเงิน
เขียนแคปชั่น 1 ประโยคที่ดึงดูดใจ ใช้จิตวิทยาการตลาด กระตุ้นให้อยากซื้อทันที ใช้ Emoji เหมาะสม ห้ามพูดทั่วไป ต้องเฉพาะกับสินค้านี้เท่านั้น

3.) Hashtag แนะนำ
แนะนำ 6-8 hashtag ที่ตรงกับสินค้าและกลุ่มเป้าหมายจริงๆ

4.) คำแนะนำเพิ่มเติม
เทคนิคเพิ่มยอดขาย 2 ข้อ อิงจากข้อมูลจริงที่เห็น"""

    response = model.generate_content(prompt)
    return response.text

def parse_result(text):
    result = {'points': '', 'caption': '', 'hashtags': '', 'tips': ''}
    points_match = re.search(r'1[.)]\s*จุดเด่น[^\n]*\n([\s\S]*?)(?=\n2[.)]|\Z)', text)
    caption_match = re.search(r'2[.)]\s*แคปชั่น[^\n]*\n([\s\S]*?)(?=\n3[.)]|\Z)', text)
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

# --- GEMINI API KEY INPUT ---
with st.expander("🔑 ใส่ Gemini API Key ของคุณ (จำเป็น)", expanded=not st.session_state.gemini_key):
    st.markdown("""
    <div class="api-title">
    ต้องมี Gemini API Key ฟรีก่อนใช้งาน<br>
    👉 สมัครฟรีได้ที่ <a href="https://aistudio.google.com" target="_blank">aistudio.google.com</a> → Get API Key
    </div>
    """, unsafe_allow_html=True)
    
    api_key_input = st.text_input(
        "Gemini API Key:",
        type="password",
        placeholder="AIza...",
        value=st.session_state.gemini_key,
        label_visibility="collapsed"
    )
    
    if st.button("✅ บันทึก API Key", key="save_api"):
        if api_key_input.startswith("AIza"):
            model_test, ok = init_gemini(api_key_input)
            if ok:
                st.session_state.gemini_key = api_key_input
                st.session_state.model = model_test
                st.success("✅ API Key ใช้งานได้ครับ!")
            else:
                st.error("❌ API Key ไม่ถูกต้อง ลองใหม่ครับ")
        else:
            st.error("❌ API Key ต้องขึ้นต้นด้วย AIza...")

st.markdown("")

# License Key input (Pro)
with st.expander("🏆 มี License Key Pro? กดที่นี่"):
    key_input = st.text_input("ใส่ License Key:", placeholder="KROB-XXXX-XXXX-XXXX", label_visibility="collapsed")
    if st.button("ยืนยัน Key", key="verify_key"):
        valid_keys = st.secrets.get("LICENSE_KEYS", "").split(",")
        if key_input.strip() in [k.strip() for k in valid_keys]:
            st.session_state.is_pro = True
            st.success("✅ เปิดใช้งาน Pro แล้ว! ไม่จำกัดครั้งครับ")
        else:
            st.error("❌ Key ไม่ถูกต้อง ติดต่อเราทาง Line ครับ")

st.markdown("")

# URL Input
url_input = st.text_input(
    "วางลิงก์สินค้าที่นี่:",
    placeholder="https://www.tiktok.com/... หรือ https://shopee.co.th/...",
)

# Analyze button
if st.button("🚀 วิเคราะห์เลย!", key="analyze"):
    if not st.session_state.gemini_key:
        st.warning("⚠️ กรุณาใส่ Gemini API Key ก่อนนะครับ (ฟรี สมัครได้ที่ aistudio.google.com)")
    elif not url_input:
        st.warning("⚠️ กรุณาใส่ลิงก์สินค้าก่อนนะครับ")
    else:
        platform = detect_platform(url_input)
        if not platform:
            st.error("❌ รองรับเฉพาะ TikTok, Shopee และ Lazada ครับ")
        elif not st.session_state.is_pro and st.session_state.quota_used >= FREE_LIMIT:
            st.error("🔒 ใช้ครบโควต้าวันนี้แล้วครับ (5 ครั้ง/วัน)")
            st.info("อัปเกรดเป็น Pro เพื่อใช้งานไม่จำกัด → [ติดต่อทาง Line](https://line.me/ti/p/@vfk5903b)")
        else:
            # init model ถ้ายังไม่ได้ init
            if not st.session_state.model:
                st.session_state.model, _ = init_gemini(st.session_state.gemini_key)
            
            with st.spinner(f"⏳ กำลังวิเคราะห์จาก {platform}..."):
                page_text = fetch_page_text(url_input)
                raw_result = analyze_with_ai(st.session_state.model, platform, page_text, url_input)
                parsed = parse_result(raw_result)
                if not st.session_state.is_pro:
                    st.session_state.quota_used += 1

            st.success(f"✅ วิเคราะห์เสร็จแล้วครับ! (จาก {platform})")
            st.divider()

            if parsed['points']:
                st.markdown('<div class="result-box"><div class="result-title">✨ จุดเด่นของสินค้า</div>' +
                    parsed['points'].replace('\n', '<br>') + '</div>', unsafe_allow_html=True)

            if parsed['caption']:
                st.markdown('<div class="result-box"><div class="result-title">✏️ แคปชั่นทำเงิน</div>' +
                    f'<div class="caption-text">{parsed["caption"]}</div></div>', unsafe_allow_html=True)
                st.code(parsed['caption'], language=None)

            if parsed['hashtags']:
                st.markdown('<div class="result-box"><div class="result-title">#️⃣ Hashtag แนะนำ</div>' +
                    f'<div class="hashtag-text">{parsed["hashtags"]}</div></div>', unsafe_allow_html=True)
                st.code(parsed['hashtags'], language=None)

            if parsed['caption'] and parsed['hashtags']:
                full_text = f"{parsed['caption']}\n\n{parsed['hashtags']}"
                st.code(full_text, language=None)
                st.caption("👆 Copy แคปชั่น + Hashtag พร้อมโพสต์ได้เลยครับ")

            if parsed['tips']:
                st.info(f"💡 **คำแนะนำ:** {parsed['tips']}")

st.divider()
st.markdown("""
<div style='text-align:center; color:#666; font-size:13px;'>
    🆓 Free: 5 ครั้ง/วัน · ⭐ Pro: 149 บาท/เดือน<br>
    <a href="https://line.me/ti/p/@vfk5903b" style="color:#fe2c55;">💬 ซื้อ Pro หรือสอบถามทาง Line</a>
</div>
""", unsafe_allow_html=True)
