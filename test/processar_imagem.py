import requests
import base64
from salvar_imagem import salvar_imagem_sqlite

def baixar_imagem_base64(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode("utf-8")
    else:
        raise Exception(f"Erro ao baixar imagem: {response.status_code}")

def processar_imagem_recebida(mensagem, remetente, timestamp):
    if "imageMessage" not in mensagem:
        return

    image_data = mensagem["imageMessage"]
    file_url = image_data.get("url")
    campo_checklist = image_data.get("caption", "documento_nao_identificado").lower().replace(" ", "_")
    nome_arquivo = f"{timestamp}_{remetente.replace('@', '_')}.jpg"

    try:
        base64_da_imagem = baixar_imagem_base64(file_url)
        salvar_imagem_sqlite(base64_da_imagem, remetente, nome_arquivo)
        print(f"✅ Imagem '{campo_checklist}' salva no banco como '{nome_arquivo}'.")
    except Exception as e:
        print(f"❌ Erro ao salvar imagem: {e}")
