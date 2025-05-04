import os
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
from openai import OpenAI

# Inicializa Slack Bolt App e Flask
slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
openai_key = os.environ.get("OPENAI_API_KEY")

app = App(token=slack_bot_token)
handler = SlackRequestHandler(app)
flask_app = Flask(__name__)
openai = OpenAI(api_key=openai_key)

# Evento de mensagem
@app.event("message")
def handle_message_events(body, say, logger):
    event = body.get("event", {})
    text = event.get("text")
    if text and not event.get("bot_id"):
        response = f"Recebido: {text}"
        say(response)

# Endpoint para o Slack Events API
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# Health check para Cloud Run
@flask_app.route("/")
def index():
    return "TaziBot rodando com Slack Bolt + Flask"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)
