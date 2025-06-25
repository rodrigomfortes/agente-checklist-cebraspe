# app.py
import base64
import asyncio
import os
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from database.database import ChecklistDatabase, init_database
from services.whatsapp import enviar_mensagem_whatsapp

# === Integração com LLM ===
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List, Literal, Union

# Modelos de ações possíveis
class MarcarConferido(BaseModel):
    action: Literal["marcar_conferido"]
    itens: List[str]

class VerificarFaltantes(BaseModel):
    action: Literal["verificar_faltantes"]

class ReiniciarChecklist(BaseModel):
    action: Literal["reiniciar_checklist"]

AcoesChecklist = Union[MarcarConferido, VerificarFaltantes, ReiniciarChecklist]

# LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

def interpretar_mensagem_usuario(texto: str):
    prompt = f"""
Você é um agente inteligente que interpreta mensagens de WhatsApp durante um checklist técnico para aplicação de provas do CEBRASPE.

Seu papel é identificar se o usuário deseja:
1. Marcar um ou mais itens como conferidos
2. Verificar quais itens ainda estão faltando
3. Reiniciar o checklist

Sempre responda no formato JSON estruturado:
{{
  "action": "marcar_conferido" | "verificar_faltantes" | "reiniciar_checklist",
  "itens": ["item1", "item2"] // Apenas se a ação for 'marcar_conferido'
}}

Mensagem original do usuário: \"{texto.strip()}\"
"""
    try:
        resposta = llm.invoke(prompt).content
        if isinstance(resposta, list):
            resposta_str = json.dumps(resposta)
        else:
            resposta_str = resposta

        resultado = json.loads(resposta_str)
        if resultado["action"] == "marcar_conferido":
            return MarcarConferido(**resultado)
        elif resultado["action"] == "verificar_faltantes":
            return VerificarFaltantes(action="verificar_faltantes")
        elif resultado["action"] == "reiniciar_checklist":
            return ReiniciarChecklist(action="reiniciar_checklist")
    except Exception as e:
        print(f"⚠️ Erro ao interpretar mensagem: {e}")
    return None


# === FLASK SETUP ===
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

estado_fluxo = {}  # {sessao_id: {"dia": 1 ou 2, "indice": 0}}


def iniciar_checklist(sessao_id: str, dia=1):
    if ChecklistDatabase.buscar_checklist_dia1(sessao_id):
        print(f"📌 Checklist já iniciado para {sessao_id}")
        return "já iniciado"
    ChecklistDatabase.criar_checklist_dia1(sessao_id=sessao_id)
    estado_fluxo[sessao_id] = {"dia": dia, "indice": 0}
    print(f"✅ Checklist iniciado para {sessao_id}")
    return "iniciado"


@app.route("/", methods=["GET"])
def home():
    return "<h1>✅ Bot Checklist CEBRASPE está ativo!</h1>"


@app.route("/webhook", methods=["POST"])
def webhook():
    print("\n📩 Novo Webhook Recebido")
    try:
        dados = request.get_json()
        print(f"📦 Dados:\n{json.dumps(dados, indent=2, ensure_ascii=False)}")

        if dados.get("event") != "messages.upsert":
            return jsonify({"status": "ignorado"}), 200

        mensagem = dados["data"]["message"]
        remetente = dados["data"]["key"]["remoteJid"]
        sessao_id = remetente

        if "conversation" in mensagem:
            texto = mensagem["conversation"].strip().lower()
            print(f"💬 {remetente}: {texto}")

            # 🌞 Detecta início de checklist
                        # 🌞 Detecta início de checklist
            if "iniciar" in texto:
                if "dia 2" in texto:
                    if not ChecklistDatabase.buscar_checklist_dia2(sessao_id):
                        ChecklistDatabase.criar_checklist_dia2(sessao_id)
                    estado_fluxo[sessao_id] = {"dia": 2, "indice": 0}
                    primeiro_item = FLUXO_DIA2[0].replace("_", " ")
                    asyncio.run(enviar_mensagem_whatsapp(remetente, f"🗓️ Checklist do *Dia 2* iniciado. Envie a imagem de: *{primeiro_item}*"))
                    return jsonify({"status": "checklist dia 2 iniciado"}), 200
                else:
                    if not ChecklistDatabase.buscar_checklist_dia1(sessao_id):
                        ChecklistDatabase.criar_checklist_dia1(sessao_id)
                    estado_fluxo[sessao_id] = {"dia": 1, "indice": 0}
                    primeiro_item = FLUXO_DIA1[0].replace("_", " ")
                    asyncio.run(enviar_mensagem_whatsapp(remetente, f"🗓️ Checklist do *Dia 1* iniciado. Envie a imagem de: *{primeiro_item}*"))
                    return jsonify({"status": "checklist dia 1 iniciado"}), 200


            # 🤖 Interpretação por IA
            acao = interpretar_mensagem_usuario(texto)

            if isinstance(acao, MarcarConferido):
                dia = estado_fluxo.get(sessao_id, {}).get("dia", 1)
                for item in acao.itens:
                    if dia == 1:
                        ChecklistDatabase.atualizar_item_dia1(sessao_id, item.lower().replace(" ", "_"), presente=True)
                    else:
                        ChecklistDatabase.atualizar_item_dia2(sessao_id, item.lower().replace(" ", "_"), presente=True)
                asyncio.run(enviar_mensagem_whatsapp(remetente, f"✅ Itens conferidos: {', '.join(acao.itens)}"))
                return jsonify({"status": "conferido"}), 200

            elif isinstance(acao, VerificarFaltantes):
                dia = estado_fluxo.get(sessao_id, {}).get("dia", 1)
                checklist = (
                    ChecklistDatabase.buscar_checklist_dia1(sessao_id)
                    if dia == 1 else
                    ChecklistDatabase.buscar_checklist_dia2(sessao_id)
                )

                if not checklist:
                    asyncio.run(enviar_mensagem_whatsapp(
                        remetente,
                        "⚠️ Checklist ainda não iniciado. Envie 'iniciar' para começar."
                    ))
                else:
                    faltando = [
                        k.replace("_presente", "").replace("_", " ").capitalize()
                        for k, v in checklist.items()
                        if "_presente" in k and not v
                    ]
                    if faltando:
                        lista_formatada = '\n'.join(f"• {item}" for item in faltando)
                        mensagem = f"📋 *Itens faltando:*\n{lista_formatada}"
                    else:
                        mensagem = "🎉 Todos os itens já foram conferidos!"
                    asyncio.run(enviar_mensagem_whatsapp(remetente, mensagem))

                return jsonify({"status": "faltantes verificados"}), 200



            elif isinstance(acao, ReiniciarChecklist):
                dia = estado_fluxo.get(sessao_id, {}).get("dia", 1)
                if dia == 1:
                    ChecklistDatabase.resetar_checklist(sessao_id)
                else:
                    ChecklistDatabase.resetar_checklist_dia2(sessao_id)
                estado_fluxo[sessao_id] = {"dia": dia, "indice": 0}
                primeiro_item = (FLUXO_DIA1 if dia == 1 else FLUXO_DIA2)[0].replace("_", " ")
                asyncio.run(enviar_mensagem_whatsapp(remetente, f"♻️ Checklist do *Dia {dia}* reiniciado. Envie a imagem de: *{primeiro_item}*"))
                return jsonify({"status": "checklist reiniciado"}), 200

            else:
                asyncio.run(enviar_mensagem_whatsapp(remetente, "🤖 Não entendi. Tente algo como 'já conferi a lista de presença' ou 'o que falta?'"))
                return jsonify({"status": "mensagem irreconhecida"}), 200

        if "imageMessage" in mensagem:
            image_data = mensagem["imageMessage"]
            file_url = image_data.get("url")
            caption = image_data.get("caption", "documento_nao_identificado").lower().replace(" ", "_")

            if not file_url:
                return jsonify({"erro": "imagem sem URL"}), 400

            estado = estado_fluxo.get(sessao_id)
            if not estado:
                asyncio.run(enviar_mensagem_whatsapp(remetente, "⚠️ Envie 'iniciar' para começar o checklist."))
                return jsonify({"status": "sem checklist ativo"}), 200

            fluxo = FLUXO_DIA1 if estado["dia"] == 1 else FLUXO_DIA2
            esperado = fluxo[estado["indice"]]

            if caption != esperado:
                asyncio.run(enviar_mensagem_whatsapp(
                    remetente,
                    f"⚠️ Esperado: *{esperado.replace('_', ' ')}*. Corrija a legenda da foto antes de reenviar."
                ))
                return jsonify({"status": "item inesperado"}), 200

            try:
                resposta = requests.get(file_url)
                if resposta.status_code != 200:
                    raise Exception(f"Erro HTTP {resposta.status_code}")

                # --- NOVO TRECHO: DETECTAR O TIPO MIME DA IMAGEM ---
                content_type = resposta.headers.get('Content-Type')
                if not content_type or not content_type.startswith("image/"):
                    # Fallback para JPEG se não for uma imagem ou tipo desconhecido
                    # Ou você pode optar por rejeitar a imagem
                    mime_type = "image/jpeg"
                    print(f"⚠️ Aviso: Content-Type desconhecido ou não-imagem ({content_type}). Assumindo image/jpeg.")
                else:
                    mime_type = content_type
                # --- FIM DO NOVO TRECHO ---

                foto_base64 = base64.b64encode(resposta.content).decode("utf-8")
                # Use o mime_type detectado
                data_uri = f"data:{mime_type};base64,{foto_base64}"

                if estado["dia"] == 1:
                    ChecklistDatabase.atualizar_item_dia1(sessao_id, caption, presente=True, foto=data_uri)
                else:
                    ChecklistDatabase.atualizar_item_dia2(sessao_id, caption, presente=True, foto=data_uri)

                # Avança para o próximo item
                estado["indice"] += 1

                if estado["indice"] < len(fluxo):
                    proximo = fluxo[estado["indice"]].replace("_", " ")
                    asyncio.run(enviar_mensagem_whatsapp(remetente, f"📸 Agora envie: *{proximo}*"))
                else:
                    asyncio.run(enviar_mensagem_whatsapp(remetente, "🎉 Checklist concluído com sucesso!"))
                    del estado_fluxo[sessao_id]

                return jsonify({"status": "imagem processada"}), 200

            except Exception as e:
                print(f"❌ Erro ao processar imagem: {e}")
                asyncio.run(enviar_mensagem_whatsapp(remetente, f"❌ Erro ao processar a imagem. Tente novamente.\n\nErro: {e}"))
                return jsonify({"erro": str(e)}), 500

        return jsonify({"status": "tipo de mensagem não tratado"}), 200

    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    init_database()
    app.run(host="0.0.0.0", port=5001, debug=True)
