import openai
import os
import json
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 初始化 LineBot
line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

# 初始化 OpenAI
openai.api_key = os.environ['OPENAI_API_KEY']

# 处理用户消息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    # 使用 OpenAI 进行语言处理
    response = openai.Completion.create(
        engine="davinci",
        prompt=user_message,
        max_tokens=60
    )

    # 获取 OpenAI 的回复
    ai_reply = response.choices[0].text.strip()

    # 将回复发送给用户
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=ai_reply)
    )

# 处理 Webhook 请求
def lambda_handler(event, context):
    signature = event['headers']['X-Line-Signature']
    body = event['body']

    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        print("Invalid signature. " + str(e))
        return {
            'statusCode': 400,
            'body': json.dumps("Invalid signature.")
        }

    return {
        'statusCode': 200,
        'body': json.dumps("Hello from Lambda!")
    }
