from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

from encodings import utf_8
import requests 

url="https://qa001.azurewebsites.net/qnamaker/knowledgebases/eb0ca313-f3c9-4acb-82ab-50d5c813f592/generateAnswer"
headers={
    'Authorization': 'EndpointKey 2247f406-090c-4fe6-a8f1-6a72ecbb0d85',
    'Content-type': 'application/json'

}


line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
 


@csrf_exempt
def callback(request):
 
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            if isinstance(event, MessageEvent):  # 如果有訊息事件
                q=event.message.text
                datas={'question':q}
                r = requests.post(url, headers=headers,json=datas)
                t=r.json()['answers'][0]['answer']
                print(t)
                if(t!="No good match found in KB."):
                    line_bot_api.reply_message(  # 回復傳入的訊息文字
                        event.reply_token,
                        TextSendMessage(text=t,quick_reply=QuickReply(items=[
                        QuickReplyButton(action=MessageAction(label="找不到我要的答案",text="找不到我要的答案"))
                        ]
                        )
                        )
                    )
                else:
                    line_bot_api.reply_message(  # 回復傳入的訊息文字
                        event.reply_token,
                        TextSendMessage(text="無法識別，請您在輸入一次問題",quick_reply=QuickReply(items=[
                        QuickReplyButton(action=MessageAction(label="找不到我要的答案",text="找不到我要的答案"))
                        ]
                        )
                        )
                    )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()