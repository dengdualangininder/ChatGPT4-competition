import json
import os
import requests
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

    
def lambda_handler(event, context):
    signature = event.get('headers', {}).get('X-Line-Signature', None)
    body = event.get('body', None)

    if not signature or not body:
        return {'statusCode': 400, 'body': 'Missing signature or body'}

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return {
            'statusCode': 400,
            'body': 'Invalid signature. Please check your channel access token/channel secret.'
        }

    return {'statusCode': 200, 'body': 'OK'}


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    reply_text = get_chatgpt_response(text)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

def get_chatgpt_response(prompt):
    try:
        api_key = os.environ['OPENAI_API_KEY']
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
        data = {
            'model': 'text-davinci-002',
            'prompt': prompt,
            'max_tokens': 50,
            'temperature': 0.8,
        }
        response = requests.post('https://api.openai.com/v1/engines/davinci-codex/completions', headers=headers, json=data)
        response.raise_for_status()
        response_text = response.json()['choices'][0]['text'].strip()
        return response_text
    except Exception as e:
        return f"Error getting response from OpenAI: {str(e)}"
