from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

# 從環境變數抓取金鑰
line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))
openai.api_key = os.environ.get("OPENAI_API_KEY")

# ➤ 新增一個根目錄 route，讓 Railway 可以順利 deploy 成功
@app.route("/")
def index():
    return "LINE GPT Bot is running!"

# ➤ LINE Webhook callback 用的路由
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# ➤ 當收到文字訊息時，觸發 GPT 回應
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    gpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是 Flicker Tales 的客服助理，親切且溫柔，專門幫助使用者了解如何製作手翻書。"},
            {"role": "user", "content": user_message}
        ]
    )

    reply_text = gpt_response.choices[0].message['content']

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# ➤ 啟動 Flask server（本地測試或 Railway）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
