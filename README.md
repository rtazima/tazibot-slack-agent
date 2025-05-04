# TaziBot Slack Agent

Um agente que monitora mensagens do Slack, classifica por tipo (incidente, decisão, etc.) e responde automaticamente com o estilo do Rodrigo Tazima.

## Requisitos
- Conta no Google Cloud Platform
- Projeto com Cloud Run e Cloud Build ativados
- Secrets configurados no Secret Manager:
  - `slack-bot-token` token do Slack (xoxb-...)
  - `openai-api-key`  API key da OpenAI

## Como gerar uma OpenAI API Key

1. Acesse: https://platform.openai.com/account/api-keys
2. Clique em "Create new secret key"
3. Copie a chave gerada (ela começa com `sk-...`) — ela só aparecerá uma vez!
4. Guarde com segurança e use no passo de criação do secret.

## Passos para deploy na GCP com Secret Manager

1. Autentique no GCP:
   ```
   gcloud auth login
   gcloud config set project [PROJECT ID]]
   ```

2. Crie os secrets:
   ```
   echo -n "xoxb-..." | gcloud secrets create slack-bot-token --data-file=-
   echo -n "sk-..." | gcloud secrets create openai-api-key --data-file=-
   ```

3. Conceda permissão para o Cloud Run acessar os secrets:
   ```
   gcloud secrets add-iam-policy-binding slack-bot-token \
     --member="serviceAccount:[PROJECT_NUMBER]-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"

   gcloud secrets add-iam-policy-binding openai-api-key \
     --member="serviceAccount:[PROJECT_NUMBER]-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```
4. Suba o código e rode o build:
   ```bash
   gcloud builds submit --config cloudbuild.yaml .
   ```

   > ℹ️ Certifique-se de que o arquivo `cloudbuild.yaml` use o seguinte formato para associar os secrets corretamente:
   ```yaml
   --set-secrets=SLACK_BOT_TOKEN=slack-bot-token:latest,OPENAI_API_KEY=openai-api-key:latest
   ```

5. Torne o serviço público (necessário para Slack acessar):
   ```bash
   gcloud run services add-iam-policy-binding tazibot \
     --region=us-central1 \
     --platform=managed \
     --member="allUsers" \
     --role="roles/run.invoker"
   ```

6. Suba o código e rode o build:
   ```
   gcloud builds submit --config cloudbuild.yaml .
   ```

7. Acompanhe logs do Cloud Run:
   ```
   gcloud logs read --platform=managed --project=[PROJECT_ID] --limit=50
   ```
 