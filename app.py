from flask import Flask, request, jsonify
import json


try:
    from bot_logic import parse_mensagem_usuario
except ImportError as e:
    # A função de fallback agora é mais útil para depuração.
    print(f"ERRO CRÍTICO: Não foi possível importar 'parse_mensagem_usuario' de 'bot_logic.py'. Erro: {e}")
    def parse_mensagem_usuario(texto: str):
        print("AVISO: Usando a função de parser de fallback.")
        return {"action": "fallback", "texto_original": texto}


app = Flask(__name__)

@app.route('/', methods=['GET'])
def health_check():
    return "<h1>Servidor do Bot de Checklist está a funcionar!</h1>"

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Recebe e processa os webhooks da Evolution API.
    """
    print("\n--- Novo Webhook Recebido ---")
    try:
        dados_webhook = request.get_json()
        print(f"Dados brutos recebidos: {json.dumps(dados_webhook, indent=2)}")

        texto_usuario = dados_webhook['data']['message']['body']
        numero_remetente = dados_webhook['data']['key']['remoteJid']

        print(f"Mensagem de '{numero_remetente}': '{texto_usuario}'")

        acao_estruturada = parse_mensagem_usuario(texto_usuario)
        
        if hasattr(acao_estruturada, 'model_dump'):
            acao_dict = acao_estruturada.model_dump()
        else:
            acao_dict = acao_estruturada # Já é um dicionário no caso do fallback

        print(f"Ação interpretada: {json.dumps(acao_dict, indent=2)}")

        print("--- Processamento do Webhook Concluído ---")

        return jsonify({"status": "sucesso", "mensagem": "Webhook recebido e processado"}), 200

    except Exception as e:
        print(f"ERRO ao processar o webhook: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
