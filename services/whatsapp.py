import httpx

async def enviar_mensagem_whatsapp(telefone: str, mensagem: str):
    url = "http://localhost:8080/message/sendText/cebraspe-checklist"
    headers = {
        "Content-Type": "application/json",
        "apikey": "3846A760F91E-4FD3-A3D7-898ABC4B7EC8"
    }
    payload = {
        "number": telefone,
        "text": mensagem
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        print("📤 Resposta:", response.json())



