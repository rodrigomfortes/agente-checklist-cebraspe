import httpx

async def enviar_mensagem_whatsapp(telefone: str, mensagem: str):
    url = "http://localhost:8080/message/sendText/cebraspe-checklist"
    headers = {
        "Content-Type": "application/json",
        "apikey": "CD7ED21646FF-4B71-B90E-9E14892277BA"
    }
    payload = {
        "number": telefone,
        "text": mensagem
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        print("📤 Resposta:", response.json())
