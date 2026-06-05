# -*- coding: utf-8 -*-
import requests
import os
from dotenv import load_dotenv

# Local ortamdaki .env dosyasını yükle (eğer varsa)
load_dotenv()

STRAPI_URL = os.getenv("STRAPI_URL", "https://gezi-rehberi-3ucn.onrender.com").rstrip("/")
STRAPI_EMAIL = os.getenv("STRAPI_EMAIL", "api@gezirehberi.com")
STRAPI_PASSWORD = os.getenv("STRAPI_PASSWORD", "GeziBip210!")

def clean():
    # Login
    res = requests.post(f"{STRAPI_URL}/api/auth/local", json={
        "identifier": STRAPI_EMAIL,
        "password": STRAPI_PASSWORD
    })
    token = res.json()["jwt"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Collect unique documentIds for places
    place_docs = set()
    for locale in ["tr", "en"]:
        for status in ["draft", "published"]:
            url = f"{STRAPI_URL}/api/places?locale={locale}&status={status}&pagination[pageSize]=200"
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json().get("data", [])
                for item in data:
                    doc_id = item.get("documentId")
                    if doc_id:
                        place_docs.add(doc_id)
                        
    print(f"Total places to delete: {len(place_docs)}")
    for doc_id in place_docs:
        del_url = f"{STRAPI_URL}/api/places/{doc_id}"
        r = requests.delete(del_url, headers=headers)
        print(f"Deleted place {doc_id}: {r.status_code}")

    # Collect unique documentIds for cities
    city_docs = set()
    for locale in ["tr", "en"]:
        for status in ["draft", "published"]:
            url = f"{STRAPI_URL}/api/cities?locale={locale}&status={status}&pagination[pageSize]=200"
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json().get("data", [])
                for item in data:
                    doc_id = item.get("documentId")
                    if doc_id:
                        city_docs.add(doc_id)
                        
    print(f"Total cities to delete: {len(city_docs)}")
    for doc_id in city_docs:
        del_url = f"{STRAPI_URL}/api/cities/{doc_id}"
        r = requests.delete(del_url, headers=headers)
        print(f"Deleted city {doc_id}: {r.status_code}")

if __name__ == "__main__":
    clean()
