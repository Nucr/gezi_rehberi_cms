# -*- coding: utf-8 -*-
"""
=======================================================
  YZ Destekli Gezi Rehberi - Streamlit Frontend
  BIP210 Final Projesi
=======================================================
Çalıştırma: streamlit run app.py
"""

import streamlit as st
import requests
import os
from html import escape
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

# Local ortamdaki .env dosyasını yükle (eğer varsa)
load_dotenv()

# ─── AYARLAR ──────────────────────────────────────────────────────────────────
STRAPI_URL = os.getenv("STRAPI_URL", "https://gezi-rehberi-3ucn.onrender.com").rstrip("/")
STRAPI_API_TOKEN = os.getenv("STRAPI_API_TOKEN", "").strip()

# ─── SAYFA YAPISI ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gezi Rehberi | AI Destekli Seyahat",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── PREMIUM CSS ──────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}
.stApp {
    background: linear-gradient(135deg, #0d0d1a 0%, #0f172a 50%, #0d0d1a 100%);
    min-height: 100vh;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    border-right: 1px solid rgba(99, 102, 241, 0.2);
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(99, 102, 241, 0.1) !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 10px !important;
    color: #fff !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #cbd5e1 !important;
}
.hero-section {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 70%, #6366f1 100%);
    border-radius: 20px;
    padding: 50px 40px;
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 25px 50px rgba(99, 102, 241, 0.3);
}
.hero-title {
    font-size: 3em;
    font-weight: 900;
    color: #ffffff;
    margin: 0 0 10px 0;
    text-shadow: 0 2px 20px rgba(0,0,0,0.3);
}
.hero-subtitle {
    font-size: 1.2em;
    color: rgba(255,255,255,0.8);
    margin: 0 0 20px 0;
    font-weight: 400;
}
.city-card {
    background: linear-gradient(135deg, rgba(30,27,75,0.8) 0%, rgba(49,46,129,0.6) 100%);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 28px;
    backdrop-filter: blur(20px);
}
.city-card-title {
    font-size: 1.8em;
    font-weight: 800;
    color: #a5b4fc;
    margin: 0 0 8px 0;
}
.city-card-country {
    font-size: 0.9em;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 600;
    margin-bottom: 10px;
}
.city-card-desc {
    font-size: 1em;
    color: #cbd5e1;
    line-height: 1.7;
}
.section-header {
    font-size: 1.4em;
    font-weight: 700;
    color: #e2e8f0;
    margin: 10px 0 20px 0;
    padding-left: 14px;
    border-left: 4px solid #6366f1;
}
.place-card-body {
    padding: 18px 20px 20px 20px;
}
.place-card-name {
    font-size: 1.15em;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0 0 8px 0;
}
.place-card-stars {
    color: #f59e0b;
    font-size: 0.95em;
    margin-bottom: 10px;
    letter-spacing: 2px;
}
.place-card-score {
    color: #94a3b8;
    font-size: 0.82em;
    margin-left: 6px;
    font-weight: 500;
}
.place-card-desc {
    font-size: 0.9em;
    color: #94a3b8;
    line-height: 1.6;
    margin: 0;
}
.no-image-box {
    background: linear-gradient(135deg, #1e1b4b, #312e81);
    height: 230px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3em;
    border-radius: 12px;
}
.stat-box {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    margin-bottom: 10px;
}
.stat-number {
    font-size: 2em;
    font-weight: 800;
    color: #818cf8;
}
.stat-label {
    font-size: 0.8em;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}
.footer {
    text-align: center;
    padding: 30px 0 10px 0;
    color: #334155;
    font-size: 0.85em;
    border-top: 1px solid rgba(99,102,241,0.1);
    margin-top: 40px;
}
.custom-error {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 12px;
    padding: 16px 20px;
    color: #fca5a5;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ─── ÖNBELLEKLİ GÜVENLİ ÇEVİRİ FONKSİYONU ─────────────────────────────────────
@st.cache_data(show_spinner=False)
def safe_translate(text, target_lang="en"):
    if not text or target_lang == "tr":
        return text
    try:
        return GoogleTranslator(source='tr', target=target_lang).translate(str(text))
    except Exception:
        return text

# ─── YARDIMCI FONKSİYONLAR ────────────────────────────────────────────────────
def score_to_stars(score):
    if not score:
        return "☆☆☆☆☆", 0
    full_stars  = max(0, min(5, int(round(float(score)))))
    empty_stars = 5 - full_stars
    return ("★" * full_stars) + ("☆" * empty_stars), float(score)

def normalize_entry(entry):
    if not isinstance(entry, dict):
        return {}
    attrs = entry.get("attributes")
    if isinstance(attrs, dict):
        normalized = {"id": entry.get("id"), "documentId": entry.get("documentId")}
        normalized.update(attrs)
        return normalized
    return entry

def normalize_relation(value):
    if isinstance(value, dict) and "data" in value:
        value = value.get("data")
    if isinstance(value, list):
        return [normalize_entry(item) for item in value if item]
    return normalize_entry(value) if isinstance(value, dict) else value

def dedupe_entries(entries):
    unique = {}
    for item in entries:
        key = item.get("documentId") or item.get("id")
        if key is None:
            continue
        current = unique.get(key)
        if current is None or (not current.get("publishedAt") and item.get("publishedAt")):
            unique[key] = item
    return list(unique.values())

def extract_url_from_anywhere(data):
    """Verilen veri yapısı ne kadar derin olursa olsun içindeki görsel linkini kazır."""
    if not data:
        return None
    if isinstance(data, str):
        if data.startswith(("http://", "https://", "/")):
            return data
    if isinstance(data, dict):
        # Klasik alanları tara
        for key in ["url", "image_url", "path"]:
            if isinstance(data.get(key), str):
                return data.get(key)
        # İç içe geçmiş formatları tara
        formats = data.get("formats", {})
        if isinstance(formats, dict):
            for f_size in ["large", "medium", "small", "thumbnail"]:
                f_data = formats.get(f_size)
                if isinstance(f_data, dict) and isinstance(f_data.get("url"), str):
                    return f_data.get("url")
        # Alt kırılımlarda rekürsif ara
        for k, v in data.items():
            res = extract_url_from_anywhere(v)
            if res:
                return res
    if isinstance(data, list):
        for item in data:
            res = extract_url_from_anywhere(item)
            if res:
                return res
    return None

def image_url_from_cover(cover):
    """Geliştirilmiş Akıllı Görsel Yakalayıcı"""
    url = extract_url_from_anywhere(cover)
    if not url:
        return None
        
    url_str = str(url)
    if url_str.startswith(("http://", "https://")):
        return url_str
        
    return STRAPI_URL + url_str if url_str.startswith("/") else url_str

def parse_rich_text(desc):
    if isinstance(desc, list):
        parts = []
        for block in desc:
            for child in block.get("children", []):
                text = child.get("text", "").strip()
                if text:
                    parts.append(text)
        return " ".join(parts)
    elif isinstance(desc, str):
        return desc.strip()
    return ""

def api_headers():
    if STRAPI_API_TOKEN:
        return {"Authorization": f"Bearer {STRAPI_API_TOKEN}"}
    return {}

@st.cache_data(show_spinner=False)
def fetch_places(locale="tr"):
    try:
        # Sorguyu populate=* yaparak tüm ilişkileri (cover medyasını derinlemesine) çekmeye zorluyoruz
        url = f"{STRAPI_URL}/api/places?locale={locale}&populate=*&pagination[pageSize]=200"
        headers = api_headers()
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return dedupe_entries([normalize_entry(item) for item in res.json().get("data", [])])
    except Exception as e:
        st.sidebar.error(f"API Bağlantı Hatası: {e}")
        if 'res' in locals():
            st.sidebar.error(f"Sunucu Yanıtı ({res.status_code}): {res.text[:150]}")
        return []

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌍 Gezi Rehberi")
    st.markdown("---")

    st.markdown("**🔤 Dil / Language**")
    lang_choice = st.radio(
        label="Dil Seçimi",
        options=["🇹🇷 Türkçe", "🇬🇧 English"],
        index=0,
        label_visibility="collapsed"
    )
    locale = "tr" if "Türkçe" in lang_choice else "en"
    st.markdown("---")

    st.markdown("**📡 Veri Kaynağı**")
    st.markdown(f"<small style='color:#64748b;'>Strapi CMS<br/>{STRAPI_URL}</small>", unsafe_allow_html=True)
    st.markdown("---")

# ─── VERİ YÜKLEME (HER ZAMAN TR - TAM LİSTE) ──────────────────────────────────
places = fetch_places("tr")

if not places:
    st.markdown(f'<div class="custom-error">⚠️ Veriler yüklenemedi. Lütfen Strapi backendinizin ayakta olduğundan emin olun.</div>', unsafe_allow_html=True)
    st.stop()

# ─── ŞEHİR MAPLEME YAPISI ─────────────────────────────────────────────────────
city_map = {}
for p in places:
    city = normalize_relation(p.get("city"))
    if city and isinstance(city, dict):
        original_city_name = city.get("name", "")
        city_id = city.get("documentId") or city.get("id")
        
        if original_city_name and city_id:
            display_city_name = safe_translate(original_city_name, locale) if locale == "en" else original_city_name
            
            if display_city_name not in city_map:
                city_map[display_city_name] = {
                    "id": city_id,
                    "original_name": original_city_name,
                    "country": city.get("country", "Türkiye"),
                    "description": city.get("description", "")
                }

city_names = sorted(list(city_map.keys()))

# ─── SIDEBAR: ŞEHİR SEÇİMİ VE SKORLAR ─────────────────────────────────────────
with st.sidebar:
    select_label = "📍 Şehir Seçin" if locale == "tr" else "📍 Select City"
    selected_city = st.selectbox(select_label, city_names, key="city_selector")

    st.markdown("---")
    city_count = len(city_map)
    place_count = len(places)
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{city_count}</div>
        <div class="stat-label">{'Şehir' if locale == 'tr' else 'Cities'}</div>
    </div>
    <div class="stat-box">
        <div class="stat-number">{place_count}</div>
        <div class="stat-label">{'Mekan' if locale == 'tr' else 'Places'}</div>
    </div>
    """, unsafe_allow_html=True)

# ─── HERO SECTION ─────────────────────────────────────────────────────────────
hero_title    = "YZ Destekli Gezi Rehberi" if locale == "tr" else "AI-Powered Travel Guide"
hero_subtitle = "Yapay Zekâ zenginleştirmeli içerikler ve akıllı rehber." if locale == "tr" else "AI-enriched content and smart travel assistant."
st.markdown(f'<div class="hero-section"><div class="hero-title">{hero_title}</div><div class="hero-subtitle">{hero_subtitle}</div></div>', unsafe_allow_html=True)

# ─── SEÇİLEN ŞEHİR DETAYLARI ──────────────────────────────────────────────────
selected_info = city_map.get(selected_city, {})
city_desc     = parse_rich_text(selected_info.get("description", ""))
city_country  = selected_info.get("country", "")

display_country = safe_translate(city_country, locale)
display_desc = safe_translate(city_desc, locale)

st.markdown(f"""
<div class="city-card">
    <div class="city-card-country">📌 {escape(display_country)}</div>
    <div class="city-card-title">🏙️ {escape(selected_city)}</div>
    <div class="city-card-desc">{escape(display_desc if display_desc else ('Açıklama yok.' if locale == 'tr' else 'No description.'))}</div>
</div>
""", unsafe_allow_html=True)

# ─── MEKANLARI FİLTRELE ───────────────────────────────────────────────────────
selected_city_id = selected_info.get("id")
filtered_places  = [
    p for p in places
    if normalize_relation(p.get("city"))
    and (normalize_relation(p.get("city")).get("documentId") or normalize_relation(p.get("city")).get("id")) == selected_city_id
]

header_text = f"📍 {escape(selected_city)} Mekanları ({len(filtered_places)} yer)" if locale == "tr" else f"📍 Places in {escape(selected_city)} ({len(filtered_places)} places)"
st.markdown(f'<div class="section-header">{header_text}</div>', unsafe_allow_html=True)

# ─── MEKAN KARTLARI DÖNGÜSÜ ───────────────────────────────────────────────────
COLS = 3
cols = st.columns(COLS)

for idx, place in enumerate(filtered_places):
    col = cols[idx % COLS]
    with col:
        # cover alanını derin tarama fonksiyonuna gönderiyoruz
        img_url = image_url_from_cover(place.get("cover"))
        
        if img_url:
            if img_url.count("https://") > 1:
                img_url = "https://" + img_url.split("https://")[-1]
            st.image(img_url, use_container_width=True)
        else:
            st.markdown('<div class="no-image-box">🗺️</div>', unsafe_allow_html=True)

        place_name  = place.get("name", "—")
        place_score = place.get("score")
        place_desc  = parse_rich_text(place.get("description", ""))

        display_place_name = safe_translate(place_name, locale)
        display_place_desc = safe_translate(place_desc, locale)

        stars, score_val = score_to_stars(place_score)
        score_display = f"{score_val:.1f}" if score_val else ""
        no_desc_text = "Açıklama henüz eklenmemiş." if locale == "tr" else "No description available."

        st.markdown(f"""
        <div class="place-card-body">
            <div class="place-card-name">{escape(str(display_place_name))}</div>
            <div class="place-card-stars">
                {stars} <span class="place-card-score">{score_display}</span>
            </div>
            <div class="place-card-desc">{escape(display_place_desc if display_place_desc else no_desc_text)}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown(f'<div class="footer">🌍 <strong>YZ Destekli Gezi Rehberi</strong> &nbsp;|&nbsp; BIP210 Final Projesi</div>', unsafe_allow_html=True)