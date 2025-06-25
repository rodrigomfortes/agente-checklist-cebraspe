# app.py
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


@app.route("/", methods=["GET"])
def home():
    return "<h1>Bot Checklist CEBRASPE ativo!</h1>"


@app.route("/webhook", methods=["POST"])
def webhook():
    print("\n📩 --- Novo Webhook Recebido ---")
    try:
        dados = request.get_json()
        print(f"📦 Dados recebidos:\n{json.dumps(dados, indent=2, ensure_ascii=False)}")

        if dados.get("event") != "messages.upsert":
            return jsonify({"status": "ignorado"}), 200

        mensagem = dados["data"]["message"]
        remetente = dados["data"]["key"]["remoteJid"]
        timestamp = str(dados["data"].get("messageTimestamp", datetime.utcnow().timestamp()))
        sessao_id = remetente

        if "conversation" in mensagem:
            texto = mensagem["conversation"].strip().lower()
            print(f"💬 Texto de {remetente}: {texto}")

            if texto.startswith("iniciar"):
                dia = 1 if "2" not in texto else 2
                status = iniciar_checklist(sessao_id, dia=dia)
                if status == "iniciado":
                    fluxo = FLUXO_DIA1 if dia == 1 else FLUXO_DIA2
                    proximo_item = fluxo[0].replace("_", " ")
                    asyncio.run(enviar_mensagem_whatsapp(remetente, f"✅ Checklist iniciado! Envie a *foto de {proximo_item}* com legenda correspondente."))
                else:
                    asyncio.run(enviar_mensagem_whatsapp(remetente, "ℹ️ O checklist já está em andamento. Continue enviando as imagens normalmente!"))
                return jsonify({"status": f"checklist {status}"}), 200
            
            

        if "imageMessage" in mensagem:
            image_data = mensagem["imageMessage"]
            file_url = image_data.get("url")
            caption = image_data.get("caption", "documento_nao_identificado").lower().replace(" ", "_")
            if not file_url:
                return jsonify({"erro": "URL da imagem não encontrada"}), 400

            estado = estado_fluxo.get(sessao_id)
            if not estado:
                asyncio.run(enviar_mensagem_whatsapp(remetente, "⚠️ Você ainda não iniciou o checklist. Envie 'iniciar' para começar."))
                return jsonify({"status": "sem checklist ativo"}), 200

            fluxo = FLUXO_DIA1 if estado["dia"] == 1 else FLUXO_DIA2
            esperado = fluxo[estado["indice"]]

            if caption != esperado:
                asyncio.run(enviar_mensagem_whatsapp(remetente, f"⚠️ Esperado: *{esperado.replace('_', ' ')}*. Envie a imagem correta."))
                return jsonify({"status": "aguardando item correto"}), 200

            try:
                resposta = requests.get(file_url)
                if resposta.status_code != 200:
                    raise Exception(f"Erro HTTP {resposta.status_code} ao baixar imagem")
                foto_base64 = base64.b64encode(resposta.content).decode("utf-8")

                ChecklistDatabase.atualizar_item_dia1(
                    sessao_id=sessao_id,
                    campo=caption,
                    presente=True,
                    foto=foto_base64
                )

                print(f"✅ Imagem '{caption}' salva com sucesso para {sessao_id}!")

                estado["indice"] += 1
                if estado["indice"] < len(fluxo):
                    proximo = fluxo[estado["indice"]].replace("_", " ")
                    asyncio.run(enviar_mensagem_whatsapp(remetente, f"📸 Agora envie a *foto de {proximo}* com legenda correspondente."))
                else:
                    asyncio.run(enviar_mensagem_whatsapp(remetente, "🎉 Checklist finalizado! Obrigado pelo envio completo."))
                    del estado_fluxo[sessao_id]

                return jsonify({"status": "imagem processada"}), 200

            except Exception as e:
                print(f"❌ Erro ao processar imagem: {e}")
                return jsonify({"erro": str(e)}), 500

        return jsonify({"status": "mensagem não tratada"}), 200

    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    init_database()
    app.run(host="0.0.0.0", port=5001, debug=True)