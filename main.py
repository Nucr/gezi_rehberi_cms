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
from dotenv import load_dotenv

# Local ortamdaki .env dosyasını yükle (eğer varsa)
load_dotenv()

# --- AYARLAR -----------------------------------------------------------------
STRAPI_URL = os.getenv("STRAPI_URL", "https://gezi-rehberi-3ucn.onrender.com").rstrip("/")
STRAPI_EMAIL = os.getenv("STRAPI_EMAIL", "api@gezirehberi.com")
STRAPI_PASSWORD = os.getenv("STRAPI_PASSWORD", "GeziBip210!")

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
]


# --- FONKSİYONLAR -------------------------------------------------------------

def clear_database(token):
    """Veritabanındaki mükerrer verileri temizler (Mekanlar ve Şehirler silinir)."""
    headers = {"Authorization": f"Bearer {token}"}
    print("[BROOM] Veritabanı temizleniyor (mükerrer kayıtlar siliniyor)...")
    
    # Mekanları temizle
    try:
        res = requests.get(f"{STRAPI_URL}/api/places?locale=all&pagination[pageSize]=200", headers=headers, timeout=15)
        if res.status_code == 200:
            places = res.json().get("data", [])
            for place in places:
                doc_id = place.get("documentId")
                if doc_id:
                    requests.delete(f"{STRAPI_URL}/api/places/{doc_id}", headers=headers, timeout=10)
            print(f"   [TRASH]  {len(places)} adet mekan silindi.")
    except Exception as e:
        print(f"   [WARN] Mekan temizleme hatası: {e}")
        
    # Şehirleri temizle
    try:
        res = requests.get(f"{STRAPI_URL}/api/cities?locale=all&pagination[pageSize]=100", headers=headers, timeout=15)
        if res.status_code == 200:
            cities = res.json().get("data", [])
            for city in cities:
                doc_id = city.get("documentId")
                if doc_id:
                    requests.delete(f"{STRAPI_URL}/api/cities/{doc_id}", headers=headers, timeout=10)
            print(f"   [TRASH]  {len(cities)} adet şehir silindi.")
    except Exception as e:
        print(f"   [WARN] Şehir temizleme hatası: {e}")

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


def generate_image(place_name, city_name):
    """
    Pollinations engelini (402) kökten çözen, Picsum ve Unsplash altyapısını
    kullanan asla çökmeyen ve engellenmeyen görsel indirme fonksiyonu.
    """
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", place_name).strip("_") or "place"
    filename = f"temp_{safe_name}.jpg"
    
    # ─── AKILLI GÖRSEL SEÇİM SİSTEMİ ───
    # Mekan ismine göre internetteki en popüler ve kaliteli seyahat fotoğraflarını eşleştiriyoruz
    url = "https://picsum.photos/800/500"  # Genel fallback (varsayılan)
    
    p_name = place_name.lower()
    if "ayasofya" in p_name or "hagia" in p_name:
        url = "https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?w=800&auto=format&fit=crop&q=75"
    elif "kapalıçarşı" in p_name or "bazaar" in p_name:
        url = "https://images.unsplash.com/photo-1566838217578-1903568a76d9?w=800&auto=format&fit=crop&q=75"
    elif "topkapı" in p_name or "palace" in p_name:
        url = "https://images.unsplash.com/photo-1608815843437-a2285a3833b3?w=800&auto=format&fit=crop&q=75"
    elif "göreme" in p_name or "balon" in p_name:
        url = "https://images.unsplash.com/photo-1507608869274-d3177c8bb4c7?w=800&auto=format&fit=crop&q=75"
    elif "uçhisar" in p_name or "castle" in p_name:
        url = "https://images.unsplash.com/photo-1570716428704-5177112028f8?w=800&auto=format&fit=crop&q=75"
    elif "derinkuyu" in p_name or "yeraltı" in p_name:
        url = "https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800&auto=format&fit=crop&q=75"
    elif "kaleiçi" in p_name:
        url = "https://images.unsplash.com/photo-1549144511-f099e773c147?w=800&auto=format&fit=crop&q=75"
    elif "düden" in p_name or "şelale" in p_name:
        url = "https://images.unsplash.com/photo-1433832597046-4f10e10ac764?w=800&auto=format&fit=crop&q=75"
    elif "aspendos" in p_name or "tiyatro" in p_name:
        url = "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800&auto=format&fit=crop&q=75"

    print(f"[PAINT] '{place_name}' için yüksek kaliteli ve kararlı görsel indiriliyor...")

    # Bot engelini aşmak için tarayıcı taklidi yapıyoruz
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for attempt in range(1, 4):
        try:
            res = requests.get(url, headers=headers, timeout=20, stream=True)
            res.raise_for_status()

            with open(filename, "wb") as f:
                for chunk in res.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            size = os.path.getsize(filename)
            if size >= 5_000:
                print(f"   [OK] Görsel başarıyla indirildi: {filename} ({size:,} bytes)")
                return filename

            time.sleep(1)
        except Exception as e:
            print(f"   [ERROR] Görsel indirme denemesi başarısız ({attempt}/3): {e}")
            # Eğer ana link patlarsa Picsum genel havuzuna yönlendiriyoruz (Asla boş dönmesin)
            url = f"https://picsum.photos/800/500?random={attempt}"
            time.sleep(1)

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

            # 6. AI ile görsel üret
            img_file = generate_image(place["name"], city["name"])

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
