# Instale dependências:
# pip install Flask requests

import os
import time
import requests
from flask import Flask, request, jsonify

# Configura logger para mais detalhes
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Configurações da Evolution API via variáveis de ambiente
EV_API_URL = os.environ.get('EV_API_URL', 'http://evolution:8080')
EV_INSTANCE = os.environ.get('EV_INSTANCE', 'chama')
EV_API_KEY = os.environ['API_KEY']


def send_text(recipient: str, message: str):
    """
    Envia uma mensagem de texto via Evolution API.
    """
    url = f"{EV_API_URL}/message/sendText/{EV_INSTANCE}"
    headers = {
        'Content-Type': 'application/json',
        'apikey': EV_API_KEY
    }
    payload = {
        'number': recipient,
        'text': message,
        'delay': 0,
        'linkPreview': False
    }
    app.logger.info(f"Enviando texto para {recipient}: '{message}'")
    try:
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        app.logger.info(f"Mensagem enviada com sucesso: {resp.status_code}")
    except requests.RequestException as e:
        app.logger.error(f"Erro ao enviar mensagem: {e}")
    return


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    app.logger.info(f"Payload recebido: {data}")

    # Suporta payload v2 do Evolution onde 'event' e 'data' contêm a mensagem
    event = data.get('event') or ''
    if event.lower() == 'messages.upsert':
        msg = data.get('data', {})
        # Extrai texto da mensagem
        text = None
        # Para mensagens simples
        if 'conversation' in msg.get('message', {}):
            text = msg['message']['conversation']
        # Para mensagens de texto estendidas
        elif msg.get('message', {}).get('extendedTextMessage'):
            text = msg['message']['extendedTextMessage'].get('text')
        sender_jid = msg.get('key', {}).get('remoteJid', '')
        # Extrai apenas número antes do '@'
        recipient = sender_jid.split('@')[0]

        app.logger.info(f"Recebido de {recipient}: '{text}'")
        if text and text.strip().lower() == 'oi':
            app.logger.info("Trigger de resposta ao 'oi', aguardando 2s...")
            time.sleep(2)
            send_text(recipient, 'olá')
    else:
        app.logger.info(f"Evento ignorado: {event}")

    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
