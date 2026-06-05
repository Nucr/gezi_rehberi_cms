# -*- coding: utf-8 -*-
"""
=======================================================
  YZ Destekli Gezi Rehberi - Streamlit Frontend
  BIP210 Final Projesi
=======================================================
Çalıştırma: streamlit run app.py

Bu arayüz:
  - Strapi API'den şehir ve mekan verilerini çeker (GET)
  - Kullanıcının şehir seçmesini sağlar
  - TR / EN dil desteği sunar (i18n)
  - YZ tarafından üretilmiş görselleri ve açıklamaları gösterir
  - Modern, premium bir tasarımla verileri listeler
=======================================================
"""

import streamlit as st
import requests
import os
from html import escape

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
/* ── Google Font ── */


/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}

/* ── Dark Background ── */
.stApp {
    background: linear-gradient(135deg, #0d0d1a 0%, #0f172a 50%, #0d0d1a 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    border-right: 1px solid rgba(99, 102, 241, 0.2);
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* ── Sidebar selectbox & radio ── */
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(99, 102, 241, 0.1) !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 10px !important;
    color: #fff !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #cbd5e1 !important;
}

/* ── Hero Section ── */
.hero-section {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 70%, #6366f1 100%);
    border-radius: 20px;
    padding: 50px 40px;
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 25px 50px rgba(99, 102, 241, 0.3);
}
.hero-section::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-section::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: -5%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(167, 139, 250, 0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 3em;
    font-weight: 900;
    color: #ffffff;
    margin: 0 0 10px 0;
    text-shadow: 0 2px 20px rgba(0,0,0,0.3);
    position: relative;
    z-index: 1;
}
.hero-subtitle {
    font-size: 1.2em;
    color: rgba(255,255,255,0.8);
    margin: 0 0 20px 0;
    font-weight: 400;
    position: relative;
    z-index: 1;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
    color: #fff;
    padding: 6px 18px;
    border-radius: 50px;
    font-size: 0.85em;
    font-weight: 500;
    position: relative;
    z-index: 1;
}

/* ── City Info Card ── */
.city-card {
    background: linear-gradient(135deg, rgba(30,27,75,0.8) 0%, rgba(49,46,129,0.6) 100%);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 28px;
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(99,102,241,0.15);
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

/* ── Section Header ── */
.section-header {
    font-size: 1.4em;
    font-weight: 700;
    color: #e2e8f0;
    margin: 10px 0 20px 0;
    padding-left: 14px;
    border-left: 4px solid #6366f1;
}

/* ── Place Card ── */
.place-card {
    background: linear-gradient(145deg, rgba(15,23,42,0.95) 0%, rgba(17,24,39,0.9) 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 20px;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.place-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(99,102,241,0.25);
    border-color: rgba(99,102,241,0.5);
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
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3em;
}

/* ── Stats Bar ── */
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

/* ── Language Badge ── */
.lang-badge {
    display: inline-block;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    padding: 4px 14px;
    border-radius: 50px;
    font-size: 0.8em;
    font-weight: 700;
    letter-spacing: 1px;
}

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 30px 0 10px 0;
    color: #334155;
    font-size: 0.85em;
    border-top: 1px solid rgba(99,102,241,0.1);
    margin-top: 40px;
}

/* ── Error / Warning boxes ── */
.custom-error {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 12px;
    padding: 16px 20px;
    color: #fca5a5;
    font-size: 0.95em;
}
.custom-warning {
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 12px;
    padding: 16px 20px;
    color: #fcd34d;
    font-size: 0.95em;
}

/* ── Hide Streamlit branding ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ─── YARDIMCI FONKSİYONLAR ────────────────────────────────────────────────────

def score_to_stars(score):
    """Sayısal puanı yıldız gösterimine çevirir (⭐ karakterleriyle)."""
    if not score:
        return "☆☆☆☆☆", 0
    full_stars  = max(0, min(5, int(round(float(score)))))
    empty_stars = 5 - full_stars
    return ("★" * full_stars) + ("☆" * empty_stars), float(score)


def normalize_entry(entry):
    """Strapi v4/v5 cevaplarını tek düz formata indirger."""
    if not isinstance(entry, dict):
        return {}
    attrs = entry.get("attributes")
    if isinstance(attrs, dict):
        normalized = {"id": entry.get("id"), "documentId": entry.get("documentId")}
        normalized.update(attrs)
        return normalized
    return entry


def normalize_relation(value):
    """Relation/media alanlarında data sarmalayıcısı varsa kaldırır."""
    if isinstance(value, dict) and "data" in value:
        value = value.get("data")
    if isinstance(value, list):
        return [normalize_entry(item) for item in value if item]
    return normalize_entry(value) if isinstance(value, dict) else value


def dedupe_entries(entries):
    """Aynı Strapi documentId ile gelen taslak/yayın tekrarlarını tekilleştirir."""
    unique = {}
    for item in entries:
        key = item.get("documentId") or item.get("id")
        if key is None:
            continue
        current = unique.get(key)
        if current is None or (not current.get("publishedAt") and item.get("publishedAt")):
            unique[key] = item
    return list(unique.values())


def image_url_from_cover(cover):
    """Strapi media cevabından mutlak görsel URL'si üretir."""
    cover = normalize_relation(cover)
    if isinstance(cover, list):
        cover = cover[0] if cover else None
    if not isinstance(cover, dict):
        return None

    formats = cover.get("formats") or {}
    preferred = formats.get("medium") or formats.get("small") or formats.get("thumbnail")
    url = (preferred or cover).get("url")
    if not url:
        return None
    return url if url.startswith(("http://", "https://")) else STRAPI_URL + url


def parse_rich_text(desc):
    """Strapi Rich Text (blok formatı) veya düz metni ayrıştırır."""
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
    """Public izin kapalıysa Render'da STRAPI_API_TOKEN ile okuma yapılabilir."""
    if STRAPI_API_TOKEN:
        return {"Authorization": f"Bearer {STRAPI_API_TOKEN}"}
    return {}


def fetch_places(locale="tr"):
    """
    Strapi API'den tüm mekanları çeker.
    locale parametresiyle TR veya EN içerik alınabilir.
    """
    try:
        url = (
            f"{STRAPI_URL}/api/places"
            f"?locale={locale}"
            f"&populate[0]=cover"
            f"&populate[1]=city"
            f"&pagination[pageSize]=200"
        )
        res = requests.get(url, headers=api_headers(), timeout=10)
        res.raise_for_status()
        return dedupe_entries([normalize_entry(item) for item in res.json().get("data", [])])
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code in (401, 403):
            return None
        return []
    except requests.ConnectionError:
        return None
    except Exception:
        return []


def fetch_cities(locale="tr"):
    """Strapi API'den tüm şehirleri çeker."""
    try:
        url = (
            f"{STRAPI_URL}/api/cities"
            f"?locale={locale}"
            f"&pagination[pageSize]=100"
        )
        res = requests.get(url, headers=api_headers(), timeout=10)
        res.raise_for_status()
        return dedupe_entries([normalize_entry(item) for item in res.json().get("data", [])])
    except requests.HTTPError:
        return []
    except Exception:
        return []


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🌍 Gezi Rehberi")
    st.markdown("---")

    # Dil seçimi
    st.markdown("**🔤 Dil / Language**")
    lang_choice = st.radio(
        label="",
        options=["🇹🇷 Türkçe", "🇬🇧 English"],
        index=0,
        label_visibility="collapsed"
    )
    locale = "tr" if "Türkçe" in lang_choice else "en"
    st.markdown("---")

    # Veriler yükleniyor bildirimi
    st.markdown("**📡 Veri Kaynağı**")
    st.markdown(
        f"<small style='color:#64748b;'>Strapi CMS<br/>{STRAPI_URL}</small>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown(
        "<small style='color:#374151;'>BIP210 Final Projesi<br/>YZ Destekli Gezi Rehberi</small>",
        unsafe_allow_html=True
    )


# ─── VERİ YÜKLEME ─────────────────────────────────────────────────────────────

places = fetch_places(locale)
cities_data = fetch_cities(locale)

# ─── HERO SECTION ─────────────────────────────────────────────────────────────

hero_title    = "YZ Destekli Gezi Rehberi" if locale == "tr" else "AI-Powered Travel Guide"
hero_subtitle = (
    "Yapay Zekâ ile zenginleştirilmiş içerikler, AI tarafından üretilmiş görseller"
    if locale == "tr" else
    "AI-enriched content, AI-generated images from around Turkey"
)
badge_text = "🤖 Yapay Zekâ Destekli" if locale == "tr" else "🤖 AI Powered"

st.markdown(f"""
<div class="hero-section">
    <div class="hero-title">{hero_title}</div>
    <div class="hero-subtitle">{hero_subtitle}</div>
    <div class="hero-badge">{badge_text}</div>
</div>
""", unsafe_allow_html=True)


# ─── BAĞLANTI KONTROLÜ ────────────────────────────────────────────────────────

if places is None:
    st.markdown(f"""
    <div class="custom-error">
        ⚠️ <strong>Strapi'ye bağlanılamadı!</strong><br/>
        Lütfen Strapi'nin çalıştığından emin olun: <code>{escape(STRAPI_URL)}</code>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not places:
    st.markdown(f"""
    <div class="custom-warning">
        📭 <strong>Henüz mekan verisi yok.</strong><br/>
        {'Önce <code>python main.py</code> komutunu çalıştırarak verileri yükleyin.' if locale == 'tr' else 'Run <code>python main.py</code> first to populate the database.'}
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─── ŞEHİR HARİTASI ───────────────────────────────────────────────────────────

city_map = {}
for p in places:
    city = normalize_relation(p.get("city"))
    if city and isinstance(city, dict):
        city_name = city.get("name", "")
        city_id   = city.get("documentId") or city.get("id")
        if city_name and city_id and city_name not in city_map:
            city_map[city_name] = {
                "id": city_id,
                "country": city.get("country", ""),
                "description": city.get("description", "")
            }

if not city_map:
    st.markdown('<div class="custom-warning">⚠️ Şehir verisi bulunamadı.</div>', unsafe_allow_html=True)
    st.stop()

city_names = sorted(list(city_map.keys()))


# ─── SIDEBAR: ŞEHİR SEÇİMİ ───────────────────────────────────────────────────

with st.sidebar:
    st.markdown("---")
    select_label = "📍 Şehir Seçin" if locale == "tr" else "📍 Select City"
    selected_city = st.selectbox(select_label, city_names, key="city_selector")

    # İstatistikler
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


# ─── SEÇİLEN ŞEHİR BİLGİSİ ───────────────────────────────────────────────────

selected_info = city_map.get(selected_city, {})
city_desc     = parse_rich_text(selected_info.get("description", ""))
city_country  = selected_info.get("country", "")

st.markdown(f"""
<div class="city-card">
    <div class="city-card-country">📌 {escape(city_country)}</div>
    <div class="city-card-title">🏙️ {escape(selected_city)}</div>
    <div class="city-card-desc">{escape(city_desc if city_desc else ('Bu şehir hakkında açıklama eklenmemiş.' if locale == "tr" else 'No description available for this city.'))}</div>
</div>
""", unsafe_allow_html=True)


# ─── MEKANLARI FİLTRELE ───────────────────────────────────────────────────────

selected_city_id = selected_info.get("id")
filtered_places  = [
    p for p in places
    if normalize_relation(p.get("city"))
    and (normalize_relation(p.get("city")).get("documentId") or normalize_relation(p.get("city")).get("id")) == selected_city_id
]

header_text = (
    f"📍 {escape(selected_city)} Mekanları ({len(filtered_places)} yer)"
    if locale == "tr" else
    f"📍 Places in {escape(selected_city)} ({len(filtered_places)} places)"
)
st.markdown(f'<div class="section-header">{header_text}</div>', unsafe_allow_html=True)

if not filtered_places:
    st.markdown(f"""
    <div class="custom-warning">
        🔍 {'Bu şehre ait mekan bulunamadı.' if locale == 'tr' else 'No places found for this city.'}
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─── MEKAN KARTLARI ───────────────────────────────────────────────────────────

COLS = 3
cols = st.columns(COLS)

for idx, place in enumerate(filtered_places):
    col = cols[idx % COLS]
    with col:
        # Görsel
        img_url = image_url_from_cover(place.get("cover"))
        if img_url:
            st.image(img_url, use_container_width=True)
        else:
            st.markdown(
                '<div class="no-image-box">🗺️</div>',
                unsafe_allow_html=True
            )

        # İsim, puan ve açıklama
        place_name  = place.get("name", "—")
        place_score = place.get("score")
        place_desc  = parse_rich_text(place.get("description", ""))

        stars, score_val = score_to_stars(place_score)
        score_display = f"{score_val:.1f}" if score_val else ""
        no_desc_text = (
            "Açıklama henüz eklenmemiş." if locale == "tr"
            else "No description available."
        )

        st.markdown(f"""
        <div class="place-card-body">
            <div class="place-card-name">{escape(str(place_name))}</div>
            <div class="place-card-stars">
                {stars}
                <span class="place-card-score">{score_display}</span>
            </div>
            <div class="place-card-desc">{escape(place_desc if place_desc else no_desc_text)}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")


# ─── FOOTER ───────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="footer">
    🌍 <strong>YZ Destekli Gezi Rehberi</strong> &nbsp;|&nbsp; BIP210 Final Projesi<br/>
    Görseller: Pollinations AI &nbsp;|&nbsp; Çeviri: deep-translator &nbsp;|&nbsp; Backend: Strapi CMS
</div>
""", unsafe_allow_html=True)
