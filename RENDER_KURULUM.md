# Render uyumlu calistirma

Bu proje varsayilan olarak canli Strapi backend'e baglanir:

```text
https://gezi-rehberi-3ucn.onrender.com
```

## Lokalden canli Strapi'ye veri basma

```powershell
cd C:\Users\NUCRO\Desktop\gezi-rehberi-cms
.\.venv\Scripts\python.exe setup_strapi.py
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\streamlit.exe run app.py
```

## Lokal Strapi ile test etmek

```powershell
$env:STRAPI_URL="http://localhost:1337"
.\.venv\Scripts\streamlit.exe run app.py
```

## Render'da Streamlit deploy

Render'da yeni bir Web Service olustururken:

```text
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

Environment Variable:

```text
STRAPI_URL=https://gezi-rehberi-3ucn.onrender.com
STRAPI_API_TOKEN=Public izinler kapaliysa Strapi API token
```

Repo `render.yaml` dosyasi da icerir; Render Blueprint olarak kullanilabilir.

Not: Strapi'de Public role icin `city.find`, `city.findOne`, `place.find`, `place.findOne`
izinleri aciksa `STRAPI_API_TOKEN` bos kalabilir.
