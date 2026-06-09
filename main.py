# -*- coding: utf-8 -*-
"""
=======================================================
  YZ Destekli Gezi Rehberi - Otomasyon Motoru
  BIP210 Final Projesi
=======================================================
Çalıştırma: python main.py

Bu betik tek seferde şu işlemleri yapar:
  1. Strapi'ye JWT ile kimlik doğrulama
  2. Şehir ve mekan verilerini Strapi'ye yükler
  3. Pollinations AI ile her mekan için görsel üretir
  4. Görseli Strapi Media Library'ye yükler
  5. deep-translator ile açıklamayı İngilizceye çevirir
  6. Pollinations Text AI ile açıklamayı zenginleştirir
  7. İngilizce içeriği Strapi'de i18n locale olarak kaydeder
=======================================================
"""

import requests
import os
import time
import json
import hashlib
import re
from deep_translator import GoogleTranslator
from datetime import datetime
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Local ortamdaki .env dosyasını yükle (eğer varsa)
load_dotenv()

# --- AYARLAR -----------------------------------------------------------------
STRAPI_URL = os.getenv("STRAPI_URL", "https://gezi-rehberi-3ucn.onrender.com").rstrip("/")
STRAPI_EMAIL = os.getenv("STRAPI_EMAIL", "api@gezirehberi.com")
STRAPI_PASSWORD = os.getenv("STRAPI_PASSWORD", "GeziBip210!")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "").strip()

# Pollinations görsel üretim ayarları
POLLINATIONS_IMAGE_MODEL = os.getenv("POLLINATIONS_IMAGE_MODEL", "flux")
POLLINATIONS_IMAGE_WIDTH = int(os.getenv("POLLINATIONS_IMAGE_WIDTH", "800"))
POLLINATIONS_IMAGE_HEIGHT = int(os.getenv("POLLINATIONS_IMAGE_HEIGHT", "500"))

# --- ŞEHİR VE MEKAN VERİLERİ -------------------------------------------------
# Her şehir için 3 mekan ve açıklama tanımlanmıştır.
cities_data = [
    {
        "name": "İstanbul",
        "country": "Türkiye",
        "description": (
            "İki kıtayı birbirine bağlayan, binlerce yıllık tarihi ve kültürüyle "
            "dünyanın en büyüleyici metropollerinden biri."
        ),
        "places": [
            {
                "name": "Ayasofya",
                "description": (
                    "Bizans döneminden kalma, hem kilise hem cami olarak kullanılmış "
                    "eşsiz tarihi yapı. UNESCO Dünya Mirası Listesi'nde yer almaktadır."
                ),
                "score": 4.9
            },
            {
                "name": "Kapalıçarşı",
                "description": (
                    "Dünyanın en büyük ve en eski kapalı çarşılarından biri; "
                    "4000'den fazla dükkanıyla yüzyıllardır canlı bir ticaret merkezi."
                ),
                "score": 4.7
            },
            {
                "name": "Topkapı Sarayı",
                "description": (
                    "Osmanlı İmparatorluğu'nun yüzyıllarca yönetim merkezi; "
                    "hazine daireleri ve Harem bölümüyle görkemli bir saray kompleksi."
                ),
                "score": 4.8
            },
        ]
    },
    {
        "name": "Kapadokya",
        "country": "Türkiye",
        "description": (
            "Peri bacaları, sıcak hava balonları ve yeraltı şehirleriyle "
            "dünyanın hiçbir yerinde benzeri olmayan doğal bir harika."
        ),
        "places": [
            {
                "name": "Göreme Açık Hava Müzesi",
                "description": (
                    "İçinde freskleri korunmuş kaya kiliselerini barındıran "
                    "UNESCO Dünya Mirası alanı ve Kapadokya'nın simgesi."
                ),
                "score": 4.8
            },
            {
                "name": "Uçhisar Kalesi",
                "description": (
                    "Bölgenin en yüksek noktasından Erciyes Dağı ve peri bacalarına "
                    "uzanan 360 derecelik panoramik manzara sunan volkanik kaya kale."
                ),
                "score": 4.6
            },
            {
                "name": "Derinkuyu Yeraltı Şehri",
                "description": (
                    "MÖ 8. yüzyılda oyulmuş, 20.000 kişiyi barındırabilen "
                    "devasa yeraltı kompleksi; tarihin en etkileyici yapılarından biri."
                ),
                "score": 4.7
            },
        ]
    },
    {
        "name": "Antalya",
        "country": "Türkiye",
        "description": (
            "Akdeniz'in masmavi kıyısında antik Roma kentleri, "
            "turkuaz renkli sahiller ve zengin tarihiyle Türkiye'nin turizm başkenti."
        ),
        "places": [
            {
                "name": "Kaleiçi",
                "description": (
                    "Roma surlarıyla çevrili tarihi kent merkezi; "
                    "yat limanı, Ottoman mimarisi ve renkli çiçekli sokaklarıyla büyüleyici."
                ),
                "score": 4.6
            },
            {
                "name": "Düden Şelalesi",
                "description": (
                    "Akdeniz'e doğrudan dökülen nadide şelale; "
                    "turkuaz deniz ve yeşil doğanın birleştiği muhteşem manzara."
                ),
                "score": 4.5
            },
            {
                "name": "Aspendos Antik Tiyatrosu",
                "description": (
                    "MS 2. yüzyılda inşa edilmiş, 15.000 kişilik kapasitesiyle "
                    "dünyanın en iyi korunmuş Roma tiyatrolarından biri."
                ),
                "score": 4.8
            },
        ]
    },
    {
        "name": "İzmir",
        "country": "Türkiye",
        "description": (
            "Ege'nin incisi; tarihi limanı, canlı sokakları, antik kentleri ve "
            "sıcakkanlı insanlarıyla Türkiye'nin üçüncü büyük metropolü."
        ),
        "places": [
            {
                "name": "İzmir Saat Kulesi",
                "description": (
                    "Konak Meydanı'nda yer alan, 1901 yılında inşa edilmiş "
                    "ve İzmir'in en önemli simgesi olan zarif Osmanlı yapısı."
                ),
                "score": 4.7
            },
            {
                "name": "Efes Antik Kenti",
                "description": (
                    "Dünyanın en iyi korunmuş antik kentlerinden biri; Celcius Kütüphanesi "
                    "ve devasa antik tiyatrosuyla UNESCO Dünya Mirası Listesi'ndedir."
                ),
                "score": 4.9
            },
            {
                "name": "Tarihi Kemeraltı Çarşısı",
                "description": (
                    "Dünyanın en eski ve en büyük açık hava çarşılarından biri; "
                    "tarihi hanları, baharatçıları ve hareketli alışveriş sokaklarıyla ünlü."
                ),
                "score": 4.6
            },
        ]
    },
]


# --- FONKSİYONLAR -------------------------------------------------------------

def clear_database(token):
    """Veritabanındaki mükerrer verileri temizler (Mekanlar ve Şehirler silinir)."""
    headers = {"Authorization": f"Bearer {token}"}
    print("[BROOM] Veritabanı temizleniyor (mükerrer kayıtlar siliniyor)...")

    def collect_document_ids(collection):
        document_ids = set()
        for locale in ("tr", "en", "all"):
            for status in ("draft", "published"):
                page = 1
                while True:
                    params = {
                        "locale": locale,
                        "status": status,
                        "pagination[page]": page,
                        "pagination[pageSize]": 100,
                    }
                    res = requests.get(
                        f"{STRAPI_URL}/api/{collection}",
                        params=params,
                        headers=headers,
                        timeout=20,
                    )
                    if res.status_code != 200:
                        print(f"   [WARN] {collection} listeleme hatası: {res.status_code} - {res.text[:120]}")
                        break

                    payload = res.json()
                    for item in payload.get("data", []):
                        doc_id = item.get("documentId")
                        if doc_id:
                            document_ids.add(doc_id)

                    pagination = payload.get("meta", {}).get("pagination", {})
                    if page >= pagination.get("pageCount", 1):
                        break
                    page += 1
        return document_ids

    for collection, label in (("places", "mekan"), ("cities", "şehir")):
        try:
            document_ids = collect_document_ids(collection)
            deleted = 0
            for doc_id in document_ids:
                deleted_any = False
                for locale in ("tr", "en"):
                    res = requests.delete(
                        f"{STRAPI_URL}/api/{collection}/{doc_id}",
                        params={"locale": locale},
                        headers=headers,
                        timeout=20,
                    )
                    if res.status_code in (200, 202, 204, 404):
                        deleted_any = True
                    else:
                        print(f"   [WARN] {label} silme hatası ({doc_id}, {locale}): {res.status_code} - {res.text[:120]}")
                if deleted_any:
                    deleted += 1
            print(f"   [TRASH]  {deleted} adet {label} silindi.")
        except Exception as e:
            print(f"   [WARN] {label} temizleme hatası: {e}")

def string_to_blocks(text):
    """Metni Strapi v5 Blocks formatına dönüştürür."""
    return [
        {
            "type": "paragraph",
            "children": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
    ]

def get_jwt_token():
    """
    Strapi'ye e-posta ve şifre ile giriş yapar, JWT token döndürür.
    Bu token diğer tüm API çağrılarında Authorization başlığı olarak kullanılır.
    """
    print("[LOCK] Strapi'ye giriş yapılıyor...")
    res = requests.post(
        f"{STRAPI_URL}/api/auth/local",
        json={"identifier": STRAPI_EMAIL, "password": STRAPI_PASSWORD},
        timeout=15
    )
    res.raise_for_status()
    token = res.json()["jwt"]
    print("[OK] JWT token başarıyla alındı.")
    return token


def enrich_description_with_ai(place_name, city_name, original_desc):
    """
    Pollinations AI Text API kullanarak mekan açıklamasını zenginleştirir.
    Turistik ve bilgilendirici bir Türkçe açıklama üretir.
    """
    print(f"[AI] '{place_name}' için AI metin zenginleştirme yapılıyor...")
    prompt = (
        f"Sen bir profesyonel seyahat yazarısın. "
        f"Türkiye'nin {city_name} şehrindeki '{place_name}' mekanı hakkında "
        f"aşağıdaki bilgiye dayanarak turistik, bilgilendirici ve akıcı 2-3 cümlelik "
        f"bir Türkçe açıklama yaz. Sadece açıklamayı yaz, başka bir şey ekleme.\n"
        f"Mevcut bilgi: {original_desc}"
    )
    try:
        encoded_prompt = requests.utils.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai&seed={abs(hash(place_name)) % 9999}"
        res = requests.get(url, timeout=45)
        if res.status_code == 200 and len(res.text.strip()) > 20:
            enriched = res.text.strip()
            print(f"   [SPARKLE] Zenginleştirilmiş metin: {enriched[:80]}...")
            return enriched
    except Exception as e:
        print(f"   [WARN]  AI zenginleştirme başarısız, orijinal metin kullanılacak: {e}")
    return original_desc


def translate_to_english(text):
    """
    deep-translator kütüphanesi ile Türkçe metni İngilizceye çevirir.
    """
    try:
        translated = GoogleTranslator(source="tr", target="en").translate(text)
        print(f"   [WORLD] Çeviri tamamlandı: {translated[:70]}...")
        return translated
    except Exception as e:
        print(f"   [WARN]  Çeviri başarısız: {e}")
        return text


def _detect_place_scene(place_name, description=""):
    """Mekan adı ve açıklamasına göre görsel sahne tipini belirler."""
    text = f"{place_name} {description}".lower()
    rules = [
        (("kaleiçi", "old town", "marina"), "charming Antalya old town with Ottoman houses, cobblestone streets, Roman harbor and Mediterranean coast"),
        (("düden", "duden", "şelale", "selale", "waterfall"), "Lower Duden waterfall dropping from cliffs into turquoise Mediterranean sea in Antalya"),
        (("aspendos", "antik tiyatro", "ancient theater", "amphitheater"), "well-preserved Aspendos Roman amphitheater stone seating and stage architecture"),
        (("cami", "kilise", "ayasofya", "mosque", "church", "hagia"), "historic religious architecture with ornate details"),
        (("çarşı", "bazaar", "market", "kemeraltı", "kemeralti"), "vibrant traditional covered marketplace with lanterns"),
        (("saray", "palace", "topkapı"), "grand Ottoman palace courtyard and imperial architecture"),
        (("balon", "göreme", "peri", "cappadocia", "kapadokya"), "Cappadocia fairy chimneys with colorful hot air balloons at sunrise"),
        (("kale", "castle", "uçhisar"), "ancient rock castle on volcanic hill with panoramic valley view"),
        (("yeraltı", "underground", "derinkuyu"), "mysterious ancient underground city tunnels and stone chambers"),
        (("antik", "tiyatro", "theater", "efes", "ephesus", "aspendos"), "well-preserved ancient Roman ruins and amphitheater"),
        (("saat kulesi", "clock tower"), "iconic Ottoman clock tower in a lively city square"),
    ]
    for keywords, scene in rules:
        if any(keyword in text for keyword in keywords):
            return scene
    return "iconic Turkish tourist landmark with scenic landscape"


def build_image_prompt(place_name, city_name, description=""):
    """
    Mekanın yapısına uygun turistik/manzara görseli için İngilizce prompt üretir.
    Prompt; mekan adı, şehir ve açıklama içeriğiyle uyumludur.
    """
    scene = _detect_place_scene(place_name, description)
    short_desc = re.sub(r"\s+", " ", description.strip())[:180]
    context = f" Context: {short_desc}." if short_desc else ""
    return (
        f"Professional travel photography of {place_name} in {city_name}, Turkey. "
        f"{scene}.{context} "
        f"Golden hour lighting, wide-angle scenic composition, photorealistic, "
        f"National Geographic style, vibrant colors, no text, no watermark, no people close-up"
    )


def _is_valid_image(content):
    """Yanıtın gerçek bir JPEG/PNG görseli olduğunu doğrular."""
    if not content or len(content) < 5_000:
        return False
    if content[:3] == b"\xff\xd8\xff":
        return True
    if content[:4] == b"\x89PNG":
        return True
    return False


def _request_pollinations_image(prompt, seed):
    """Pollinations AI görsel API'sine istek gönderir (gen + image endpoint)."""
    encoded_prompt = requests.utils.quote(prompt)
    params = {
        "model": POLLINATIONS_IMAGE_MODEL,
        "width": POLLINATIONS_IMAGE_WIDTH,
        "height": POLLINATIONS_IMAGE_HEIGHT,
        "seed": seed,
        "enhance": "true",
        "nologo": "true",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    if POLLINATIONS_API_KEY:
        headers["Authorization"] = f"Bearer {POLLINATIONS_API_KEY}"
        params["key"] = POLLINATIONS_API_KEY

    endpoints = [
        f"https://gen.pollinations.ai/image/{encoded_prompt}",
        f"https://image.pollinations.ai/prompt/{encoded_prompt}",
    ]
    last_error = None
    for endpoint in endpoints:
        try:
            res = requests.get(endpoint, params=params, headers=headers, timeout=120)
            if res.status_code == 200 and _is_valid_image(res.content):
                return res.content, endpoint
            last_error = f"{endpoint} -> {res.status_code}: {res.text[:160]}"
        except Exception as e:
            last_error = f"{endpoint} -> {e}"
    raise RuntimeError(last_error or "Pollinations görsel üretimi başarısız")


def generate_image(place_name, city_name, description=""):
    """
    Pollinations AI ile mekana özel prompt kullanarak turistik/manzara görseli üretir.
    Üretilen görsel geçici dosyaya kaydedilir; Strapi'ye yüklendikten sonra silinir.
    """
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", place_name).strip("_") or "place"
    short_hash = hashlib.md5(f"{place_name}-{city_name}".encode()).hexdigest()[:8]
    filename = f"ai_{safe_name}_{short_hash}.jpg"

    prompt = build_image_prompt(place_name, city_name, description)
    seed = abs(hash(f"{place_name}-{city_name}")) % 999_999

    print(f"[PAINT] '{place_name}' için Pollinations AI görseli üretiliyor...")
    print(f"   [PROMPT] {prompt[:110]}...")

    for attempt in range(1, 4):
        try:
            image_bytes, endpoint = _request_pollinations_image(prompt, seed + attempt)
            with open(filename, "wb") as f:
                f.write(image_bytes)
            size = os.path.getsize(filename)
            print(f"   [OK] YZ görseli üretildi: {filename} ({size:,} bytes) [{endpoint.split('/')[2]}]")
            return filename
        except Exception as e:
            print(f"   [ERROR] Görsel üretim denemesi başarısız ({attempt}/3): {e}")
            error_text = str(e).lower()
            wait_seconds = 45 if "402" in error_text or "queue full" in error_text else 5 * attempt
            time.sleep(wait_seconds)

    if not POLLINATIONS_API_KEY:
        print(
            "   [WARN] POLLINATIONS_API_KEY tanımlı değil. "
            "Ücretsiz anahtar: https://enter.pollinations.ai"
        )
    return None

def upload_image_to_strapi(token, filename):
    """
    Yerel diskteki görsel dosyasını Strapi Media Library'ye yükler.
    Başarılı olursa Strapi'deki media ID'sini döndürür.
    """
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   [UP] Strapi'ye görsel yükleniyor: {filename}...")
    with open(filename, "rb") as f:
        res = requests.post(
            f"{STRAPI_URL}/api/upload",
            headers=headers,
            files={"files": (filename, f, "image/jpeg")},
            timeout=60
        )
    res.raise_for_status()
    response = res.json()
    image_id = response[0]["id"]
    print(f"   [OK] Görsel Strapi Media Library'ye yüklendi. ID: {image_id}")
    return image_id


def create_city(token, city_name, country, description):
    """
    Strapi'de yeni bir Şehir (City) kaydı oluşturur.
    Varsayılan dil olarak Türkçe (tr) kullanılır.
    Şehrin Strapi ID'sini döndürür.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "data": {
            "name": city_name,
            "country": country,
            "description": string_to_blocks(description),
            "publishedAt": datetime.utcnow().isoformat() + "Z"
        }
    }
    res = requests.post(f"{STRAPI_URL}/api/cities?locale=tr", headers=headers, json=data, timeout=15)
    res.raise_for_status()
    result = res.json()
    city_id = result["data"]["id"]
    doc_id  = result["data"].get("documentId", city_id)
    print(f"[CITY]  Şehir oluşturuldu: {city_name} (ID: {city_id})")
    return city_id, doc_id


def create_place(token, name, description, score, city_doc_id, image_id=None):
    """
    Strapi'de yeni bir Mekan (Place) kaydı oluşturur.
    Şehir ilişkisini ve kapak görselini bağlar.
    Mekanın Strapi ID'sini ve documentId'sini döndürür.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data_payload = {
        "name": name,
        "description": string_to_blocks(description),
        "score": score,
        "city": city_doc_id,
        "publishedAt": datetime.utcnow().isoformat() + "Z"
    }
    if image_id:
        data_payload["cover"] = image_id

    res = requests.post(
        f"{STRAPI_URL}/api/places?locale=tr",
        headers=headers,
        json={"data": data_payload},
        timeout=15
    )
    res.raise_for_status()
    result = res.json()
    place_id = result["data"]["id"]
    doc_id   = result["data"].get("documentId", place_id)
    print(f"   [PIN] Mekan oluşturuldu: {name} (ID: {place_id})")
    return place_id, doc_id


def create_place_localization(token, doc_id, en_name, en_description, score, city_doc_id, image_id=None):
    """
    Mevcut bir mekan için İngilizce (EN) i18n yerelleştirmesi oluşturur.
    Strapi v5 standardına göre aynı documentId üzerinden locale=en ile PUT yapılır.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "data": {
            "name": en_name,
            "description": string_to_blocks(en_description),
            "score": score,
            "city": city_doc_id,
            "publishedAt": datetime.utcnow().isoformat() + "Z"
        }
    }
    if image_id:
        data["data"]["cover"] = image_id
    res = requests.put(
        f"{STRAPI_URL}/api/places/{doc_id}?locale=en",
        headers=headers,
        json=data,
        timeout=15
    )
    if res.status_code in (200, 201):
        print(f"   [WORLD] İngilizce yerelleştirme başarıyla kaydedildi.")
    else:
        print(f"   [WARN]  İngilizce yerelleştirme kaydedilemedi: {res.status_code} - {res.text[:100]}")


def create_city_localization(token, doc_id, en_name, en_description, country):
    """
    Mevcut bir şehir için İngilizce (EN) i18n yerelleştirmesi oluşturur.
    Strapi v5 standardına göre aynı documentId üzerinden locale=en ile PUT yapılır.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "data": {
            "name": en_name,
            "country": country,
            "description": string_to_blocks(en_description),
            "publishedAt": datetime.utcnow().isoformat() + "Z"
        }
    }
    res = requests.put(
        f"{STRAPI_URL}/api/cities/{doc_id}?locale=en",
        headers=headers,
        json=data,
        timeout=15
    )
    if res.status_code in (200, 201):
        print(f"   [WORLD] Şehir İngilizce yerelleştirmesi kaydedildi.")
    else:
        print(f"   [WARN]  Şehir yerelleştirme hatası: {res.status_code} - {res.text[:100]}")


# --- ANA DÖNGÜ ---------------------------------------------------------------

def main():
    print("=" * 60)
    print("  [WORLD] YZ Destekli Gezi Rehberi - Otomasyon Başlatılıyor")
    print("=" * 60)

    # 1. JWT kimlik doğrulama
    token = get_jwt_token()
    if not POLLINATIONS_API_KEY:
        print(
            "[WARN] POLLINATIONS_API_KEY bulunamadı. Görsel üretimi için "
            "https://enter.pollinations.ai adresinden ücretsiz API anahtarı alıp "
            ".env dosyasına ekleyin."
        )
    print()
    
    # Tek tuşla tekrar çalıştırıldığında mükerrer kayıt oluşmasını engelle.
    clear_database(token)

    for city in cities_data:
        print(f"\n{'-'*50}")
        print(f"[CITY]  Şehir işleniyor: {city['name']}")
        print(f"{'-'*50}")

        # 2. Şehri Strapi'ye kaydet (Türkçe)
        city_id, city_doc_id = create_city(
            token,
            city["name"],
            city["country"],
            city["description"]
        )

        # 3. Şehir için İngilizce yerelleştirme oluştur
        en_city_name = translate_to_english(city["name"])
        en_city_desc = translate_to_english(city["description"])
        create_city_localization(token, city_doc_id, en_city_name, en_city_desc, city["country"])

        for place in city["places"]:
            print(f"\n  [GEAR]  Mekan işleniyor: {place['name']}")

            # 4. AI ile Türkçe açıklamayı zenginleştir
            enriched_desc = enrich_description_with_ai(
                place["name"], city["name"], place["description"]
            )

            # 5. İngilizce çeviri yap
            print(f"   [LANG] İngilizceye çevriliyor...")
            en_name = translate_to_english(place["name"])
            en_desc = translate_to_english(enriched_desc)

            # 6. Pollinations AI ile mekana özel görsel üret
            img_file = generate_image(place["name"], city["name"], enriched_desc)

            # 7. Görseli Strapi Media Library'ye yükle
            image_id = None
            if img_file and os.path.exists(img_file):
                try:
                    image_id = upload_image_to_strapi(token, img_file)
                except Exception as e:
                    print(f"   [ERROR] Görsel yükleme hatası: {e}")
                finally:
                    # Lokal görseli her durumda sil
                    if os.path.exists(img_file):
                        os.remove(img_file)
                        print(f"   [TRASH]  Lokal geçici dosya silindi.")

            # 8. Mekanı Strapi'ye kaydet (Türkçe)
            place_id, place_doc_id = create_place(
                token,
                place["name"],
                enriched_desc,
                place["score"],
                city_doc_id,
                image_id
            )

            # 9. Mekana İngilizce yerelleştirme ekle
            create_place_localization(
                token, place_doc_id, en_name, en_desc, place["score"], city_doc_id, image_id
            )

            # API limitlerini aşmamak için kısa bekleme
            time.sleep(2)

    print("\n" + "=" * 60)
    print("  [PARTY] Tüm veriler başarıyla Strapi'ye yüklendi!")
    print("=" * 60)


if __name__ == "__main__":
    main()
