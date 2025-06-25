import httpx

async def enviar_mensagem_whatsapp(telefone: str, mensagem: str):
    url = "http://localhost:8080/message/sendText/cebraspe-checklist"
    headers = {
        "Content-Type": "application/json",
        "apikey": "1EFCE2CB0D36-4D75-B0D4-8B1DF9DCDF7B"
    }
    payload = {
        "number": telefone,
        "text": mensagem
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        print("📤 Resposta:", response.json())
