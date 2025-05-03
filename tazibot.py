import os
from slack_sdk import WebClient
from slack_sdk.rtm_v2 import RTMClient
import openai

slack_token = os.environ["SLACK_BOT_TOKEN"]
openai.api_key = os.environ["OPENAI_API_KEY"]

client = WebClient(token=slack_token)

TAZIBOT_PROMPT = "Você é o TaziBot, um assistente que responde no estilo direto, humano e informal do Rodrigo Tazima. Seja objetivo, use emojis com parcimônia, fale como um líder técnico que é acessível e resolutivo."
CLASSIFICADOR_PROMPT = "Classifique a seguinte mensagem do Slack. Responda somente com a categoria: [Incidente, Dúvida Técnica, Decisão, Off-topic, Outro]. Mensagem: "

def gerar_resposta(texto):
    resposta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": TAZIBOT_PROMPT},
            {"role": "user", "content": f"Mensagem recebida: '{texto}'. Como o Tazima responderia?"}
        ]
    )
    return resposta.choices[0].message.content.strip()

def classificar_mensagem(texto):
    resposta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um classificador de mensagens Slack."},
            {"role": "user", "content": f"{CLASSIFICADOR_PROMPT} {texto}"}
        ]
    )
    return resposta.choices[0].message.content.strip()

@RTMClient.run_on(event="message")
def handle_message(**payload):
    data = payload['data']
    if 'text' in data and 'user' in data and not data.get('bot_id'):
        texto = data['text']
        canal = data['channel']
        categoria = classificar_mensagem(texto)
        if any(x in texto.lower() for x in ["bom dia", "valeu", "tudo certo", "obrigado"]):
            resposta = gerar_resposta(texto)
            client.chat_postMessage(channel=canal, text=resposta)
        elif categoria in ["Incidente", "Decisão"]:
            client.chat_postMessage(
                channel=canal,
                text=f"🔍 Classifiquei essa como *{categoria}*:
> {texto}"
            )

if __name__ == "__main__":
    print("TaziBot ativo...")
    rtm = RTMClient(token=slack_token)
    rtm.start()
