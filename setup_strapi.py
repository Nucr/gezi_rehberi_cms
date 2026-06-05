# -*- coding: utf-8 -*-
"""
Strapi Kurulum Script'i
- TR locale ekler
- Public role izinlerini açar (cities, places find/findOne)
- API kullanıcısı oluşturur
"""
import requests
import time
import os
from dotenv import load_dotenv

# Local ortamdaki .env dosyasını yükle (eğer varsa)
load_dotenv()

STRAPI_URL = os.getenv("STRAPI_URL", "https://gezi-rehberi-3ucn.onrender.com").rstrip("/")
ADMIN_EMAIL = os.getenv("STRAPI_ADMIN_EMAIL", "pejkopat@gmail.com")
ADMIN_PASSWORD = os.getenv("STRAPI_ADMIN_PASSWORD", "GeziBip210!")
API_EMAIL = os.getenv("STRAPI_EMAIL", "api@gezirehberi.com")
API_PASSWORD = os.getenv("STRAPI_PASSWORD", "GeziBip210!")

def admin_login():
    """Admin paneline giriş yap, admin JWT token döndür."""
    print("[LOCK] Admin login yapılıyor...")
    time.sleep(2)
    res = requests.post(f"{STRAPI_URL}/admin/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }, timeout=15)
    if res.status_code == 429:
        print("[WAIT] Rate limit, 60 saniye bekleniyor...")
        time.sleep(60)
        res = requests.post(f"{STRAPI_URL}/admin/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }, timeout=15)
    res.raise_for_status()
    token = res.json()["data"]["token"]
    print(f"[OK] Admin token alındı.")
    return token

def add_tr_locale(token):
    """Türkçe locale ekle ve varsayılan yap."""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Mevcut locales kontrol
    res = requests.get(f"{STRAPI_URL}/i18n/locales", headers=headers, timeout=10)
    locales = res.json()
    locale_codes = [l.get("code") for l in locales]
    print(f"[LOCATION] Mevcut locale'ler: {locale_codes}")
    
    if "tr" not in locale_codes:
        print("[WORLD] Türkçe locale ekleniyor...")
        res = requests.post(f"{STRAPI_URL}/i18n/locales", headers=headers, json={
            "name": "Turkish (tr)",
            "code": "tr",
            "isDefault": False
        }, timeout=10)
        if res.status_code in (200, 201):
            print("[OK] Türkçe locale eklendi.")
        else:
            print(f"[WARNING] Locale ekleme: {res.status_code} - {res.text[:200]}")
    else:
        print("[OK] Türkçe locale zaten mevcut.")

def setup_public_permissions(token):
    """Public role için cities ve places API izinlerini aç."""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Users-permissions plugin'deki rolleri al
    res = requests.get(f"{STRAPI_URL}/users-permissions/roles", headers=headers, timeout=10)
    if res.status_code != 200:
        print(f"[WARNING] Roller alınamadı: {res.status_code}")
        return
    
    roles = res.json().get("roles", [])
    public_role = None
    authenticated_role = None
    for role in roles:
        if role.get("type") == "public":
            public_role = role
        if role.get("type") == "authenticated":
            authenticated_role = role
    
    if not public_role:
        print("[ERROR] Public role bulunamadı!")
        return
    
    print(f"[TOOLS] Public role ID: {public_role['id']}")
    
    # Rol detaylarını al
    res = requests.get(f"{STRAPI_URL}/users-permissions/roles/{public_role['id']}", headers=headers, timeout=10)
    role_data = res.json().get("role", {})
    permissions = role_data.get("permissions", {})
    
    # City ve Place için find ve findOne izinlerini aç
    for api_name in ["city", "place"]:
        api_key = f"api::{api_name}"
        if api_key in permissions:
            controllers = permissions[api_key].get("controllers", {})
            for ctrl_name, actions in controllers.items():
                for action_name in actions:
                    if action_name in ("find", "findOne"):
                        actions[action_name]["enabled"] = True
                        print(f"  [OK] {api_key}.{ctrl_name}.{action_name} = enabled")
    
    # i18n locale listesi de public olsun
    if "plugin::i18n" in permissions:
        controllers = permissions["plugin::i18n"].get("controllers", {})
        for ctrl_name, actions in controllers.items():
            for action_name in actions:
                if "locale" in action_name.lower() or action_name in ("listLocales", "getLocales"):
                    actions[action_name]["enabled"] = True
                    print(f"  [OK] plugin::i18n.{ctrl_name}.{action_name} = enabled")
    
    # Upload plugin de public (görsel okuma)
    if "plugin::upload" in permissions:
        controllers = permissions["plugin::upload"].get("controllers", {})
        for ctrl_name, actions in controllers.items():
            for action_name in actions:
                if action_name in ("find", "findOne"):
                    actions[action_name]["enabled"] = True
                    print(f"  [OK] plugin::upload.{ctrl_name}.{action_name} = enabled")
    
    # İzinleri güncelle
    update_data = {"permissions": permissions}
    res = requests.put(
        f"{STRAPI_URL}/users-permissions/roles/{public_role['id']}",
        headers=headers,
        json=update_data,
        timeout=15
    )
    if res.status_code == 200:
        print("[OK] Public izinler başarıyla güncellendi!")
    else:
        print(f"[WARNING] İzin güncelleme: {res.status_code} - {res.text[:200]}")
    
    # Authenticated role için de tüm izinleri aç
    if authenticated_role:
        print(f"\n[TOOLS] Authenticated role ID: {authenticated_role['id']}")
        res = requests.get(f"{STRAPI_URL}/users-permissions/roles/{authenticated_role['id']}", headers=headers, timeout=10)
        auth_role_data = res.json().get("role", {})
        auth_permissions = auth_role_data.get("permissions", {})
        
        for api_name in ["city", "place"]:
            api_key = f"api::{api_name}"
            if api_key in auth_permissions:
                controllers = auth_permissions[api_key].get("controllers", {})
                for ctrl_name, actions in controllers.items():
                    for action_name in actions:
                        actions[action_name]["enabled"] = True
                        print(f"  [OK] {api_key}.{ctrl_name}.{action_name} = enabled (auth)")
        
        # Upload izinleri (authenticated)
        if "plugin::upload" in auth_permissions:
            controllers = auth_permissions["plugin::upload"].get("controllers", {})
            for ctrl_name, actions in controllers.items():
                for action_name in actions:
                    actions[action_name]["enabled"] = True
        
        res = requests.put(
            f"{STRAPI_URL}/users-permissions/roles/{authenticated_role['id']}",
            headers=headers,
            json={"permissions": auth_permissions},
            timeout=15
        )
        if res.status_code == 200:
            print("[OK] Authenticated izinler güncellendi!")
        else:
            print(f"[WARNING] Auth izin güncelleme: {res.status_code}")


def create_api_user(token):
    """Normal bir API kullanıcısı oluştur (JWT auth ile kullanılacak)."""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Authenticated role ID'sini al
    res = requests.get(f"{STRAPI_URL}/users-permissions/roles", headers=headers, timeout=10)
    roles = res.json().get("roles", [])
    auth_role_id = None
    for role in roles:
        if role.get("type") == "authenticated":
            auth_role_id = role["id"]
            break
    
    if not auth_role_id:
        print("[ERROR] Authenticated role bulunamadı!")
        return
    
    # Kullanıcı oluştur
    user_data = {
        "username": "api_user",
        "email": API_EMAIL,
        "password": API_PASSWORD,
        "confirmed": True,
        "blocked": False,
        "role": auth_role_id
    }
    
    # Önce var mı kontrol et
    res = requests.get(f"{STRAPI_URL}/users-permissions/search/api_user", headers=headers, timeout=10)
    
    res = requests.post(
        f"{STRAPI_URL}/content-manager/collection-types/plugin::users-permissions.user",
        headers=headers,
        json=user_data,
        timeout=15
    )
    if res.status_code in (200, 201):
        print(f"[OK] API kullanıcısı oluşturuldu: {API_EMAIL}")
    else:
        print(f"[WARNING] Kullanıcı oluşturma: {res.status_code} - {res.text[:200]}")


def verify_public_access():
    """Public API erişimini test et."""
    print("\n🔍 Public API erişimi test ediliyor...")
    
    endpoints = [
        "/api/cities",
        "/api/places",
    ]
    for ep in endpoints:
        try:
            res = requests.get(f"{STRAPI_URL}{ep}", timeout=10)
            if res.status_code == 200:
                print(f"  [OK] {ep} -> OK (200)")
            else:
                print(f"  [ERROR] {ep} -> {res.status_code}")
        except Exception as e:
            print(f"  [ERROR] {ep} -> {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("  Strapi Kurulum Script'i")
    print("=" * 50)
    
    token = admin_login()
    add_tr_locale(token)
    setup_public_permissions(token)
    create_api_user(token)
    verify_public_access()
    
    print("\n" + "=" * 50)
    print("  Kurulum tamamlandı!")
    print("=" * 50)
