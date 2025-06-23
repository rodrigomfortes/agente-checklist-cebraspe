import requests

url = "https://c259-2804-29b8-5086-213b-3d9c-aef9-5bea-eda4.ngrok-free.app/webhook"

payload = {
    "data": {
        "message": {
            "body": "Já conferi os crachás, fita adesiva e o alicate"
        },
        "key": {
            "remoteJid": "11999999999@whatsapp.net"
        }
    }
}

r = requests.post(url, json=payload)  # <-- Aqui já envia como JSON automaticamente
print(r.status_code)
print(r.text)
