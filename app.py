import base64
import asyncio
from flask import Flask, request, jsonify
from database.database import ChecklistDatabase, init_database
import requests
import os
import json
from datetime import datetime
from processar_imagem import processar_imagem_recebida
from services.whatsapp import enviar_mensagem_whatsapp
import openai

app = Flask(__name__)

# === FLUXOS DE CHECKLIST ===
FLUXO_DIA1 = [
    "envelope_sala_dia1", "lista_presenca_dia1", "ata_sala_dia1", "avaliacao_especializada_dia1",
    "envelope_coordenacao_dia1", "cartao_resposta_reserva_dia1", "ata_sala_reserva_dia1",
    "lista_presenca_reserva_dia1", "avaliacao_especializada_reserva_dia1", "envelope_porta_objetos_dia1",
    "envelope_sala_extra_dia1", "manuais", "crachas", "relacao_candidatos_salas",
    "alicate", "canetas", "pinceis", "fita_adesiva"
]

FLUXO_DIA2 = [
    "envelope_sala_dia2", "lista_presenca_dia2", "ata_sala_dia2", "avaliacao_especializada_dia2",
    "envelope_coordenacao_dia2", "cartao_resposta_reserva_dia2", "ata_sala_reserva_dia2",
    "lista_presenca_reserva_dia2", "avaliacao_especializada_reserva_dia2", "folha_rascunho_reserva",
    "envelope_porta_objetos_dia2", "envelope_sala_extra_dia2", "envelope_folhas_rascunho",
    "manuais", "crachas", "relacao_candidatos_salas", "alicate", "canetas", "pinceis", "fita_adesiva"
]

# Estado do progresso por sessão
estado_fluxo = {}  # {sessao_id: {"dia": 1 ou 2, "indice": 0}}


def iniciar_checklist(sessao_id: str, dia=1):
    checklist_existente = ChecklistDatabase.buscar_checklist_dia1(sessao_id)
    if checklist_existente:
        print(f"📌 Checklist já iniciado para {sessao_id}")
        return "já iniciado"

    ChecklistDatabase.criar_checklist_dia1(sessao_id=sessao_id)
    estado_fluxo[sessao_id] = {"dia": dia, "indice": 0}
    print(f"✅ Checklist iniciado para {sessao_id}")
    return "iniciado"


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

def gerar_resposta_ia(texto_usuario, checklist, fluxo, dia):
    """
    Usa a OpenAI para interpretar o comando do usuário e gerar uma resposta baseada no checklist atual.
    """
    itens_status = []
    for item in fluxo:
        status = checklist.get(f"{item}_presente", False)
        itens_status.append(f"{item.replace('_', ' ')}: {'OK' if status else 'FALTANDO'}")
    prompt = f"""
    Você é um assistente de checklist. O usuário enviou: '{texto_usuario}'.
    O checklist do dia {dia} está assim:
{chr(10).join(itens_status)}
Responda de forma objetiva e clara, em português, dizendo o que está faltando ou se está tudo certo.
    """
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente de checklist."},
                {"role": "user", "content": prompt}
            ]
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erro OpenAI: {e}")
        return "❌ Erro ao consultar IA. Tente novamente mais tarde."
