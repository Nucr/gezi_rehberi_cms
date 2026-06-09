# -*- coding: utf-8 -*-
import os

import requests
from dotenv import load_dotenv

load_dotenv()

STRAPI_URL = os.getenv("STRAPI_URL", "https://gezi-rehberi-3ucn.onrender.com").rstrip("/")
STRAPI_EMAIL = os.getenv("STRAPI_EMAIL", "api@gezirehberi.com")
STRAPI_PASSWORD = os.getenv("STRAPI_PASSWORD", "GeziBip210!")

COLLECTIONS = ("places", "cities")
LOCALES = ("tr", "en", "all")
DELETE_LOCALES = ("tr", "en")
STATUSES = ("draft", "published")
PAGE_SIZE = 100


def login():
    res = requests.post(
        f"{STRAPI_URL}/api/auth/local",
        json={"identifier": STRAPI_EMAIL, "password": STRAPI_PASSWORD},
        timeout=20,
    )
    if res.status_code != 200:
        raise RuntimeError(f"Strapi login failed: {res.status_code} - {res.text[:300]}")

    token = res.json().get("jwt")
    if not token:
        raise RuntimeError("Strapi login response did not include a JWT token.")
    return token


def fetch_document_ids(collection, headers):
    document_ids = set()

    for locale in LOCALES:
        for status in STATUSES:
            page = 1
            while True:
                params = {
                    "locale": locale,
                    "status": status,
                    "pagination[page]": page,
                    "pagination[pageSize]": PAGE_SIZE,
                }
                res = requests.get(
                    f"{STRAPI_URL}/api/{collection}",
                    params=params,
                    headers=headers,
                    timeout=20,
                )

                if res.status_code != 200:
                    print(
                        f"[WARN] {collection} list failed "
                        f"(locale={locale}, status={status}, page={page}): "
                        f"{res.status_code} - {res.text[:200]}"
                    )
                    break

                payload = res.json()
                items = payload.get("data", [])
                for item in items:
                    doc_id = item.get("documentId")
                    if doc_id:
                        document_ids.add(doc_id)

                pagination = payload.get("meta", {}).get("pagination", {})
                page_count = pagination.get("pageCount", 1)
                if page >= page_count:
                    break
                page += 1

    return document_ids


def delete_documents(collection, document_ids, headers):
    deleted = 0
    failed = 0
    label = collection[:-3] + "y" if collection.endswith("ies") else collection[:-1]

    for doc_id in sorted(document_ids):
        deleted_any_locale = False
        for locale in DELETE_LOCALES:
            res = requests.delete(
                f"{STRAPI_URL}/api/{collection}/{doc_id}",
                params={"locale": locale},
                headers=headers,
                timeout=20,
            )
            if res.status_code in (200, 202, 204, 404):
                deleted_any_locale = True
            else:
                failed += 1
                print(
                    f"[FAIL] Delete {label} {doc_id} "
                    f"(locale={locale}): {res.status_code} - {res.text[:300]}"
                )

        if deleted_any_locale:
            deleted += 1
            print(f"[OK] Deleted {label} {doc_id}")

    return deleted, failed


def count_remaining(collection, headers):
    total_ids = fetch_document_ids(collection, headers)
    return len(total_ids)


def clean():
    print(f"Cleaning Strapi data at {STRAPI_URL}")
    token = login()
    headers = {"Authorization": f"Bearer {token}"}

    total_failed = 0
    for collection in COLLECTIONS:
        document_ids = fetch_document_ids(collection, headers)
        print(f"Total {collection} documents to delete: {len(document_ids)}")
        deleted, failed = delete_documents(collection, document_ids, headers)
        total_failed += failed
        print(f"Deleted {deleted}/{len(document_ids)} {collection}; failed: {failed}")

    print("\nVerification:")
    for collection in COLLECTIONS:
        remaining = count_remaining(collection, headers)
        print(f"Remaining {collection}: {remaining}")

    if total_failed:
        raise SystemExit(1)


if __name__ == "__main__":
    clean()
