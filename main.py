# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.


import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent, UnfollowEvent, PostbackEvent, Postback, ButtonsTemplate, 
)

#ライン返信内容の生成
import feedparser
import datetime

# rss link list
# https://59log.com/?func=detail&id=2852
rss_kokunai = "https://news.google.com/news/rss/headlines/section/topic/NATION.ja_jp/%E5%9B%BD%E5%86%85?ned=jp&hl=ja&gl=JP"
rss_kokusai = "https://news.google.com/news/rss/headlines/section/topic/WORLD.ja_jp/%E5%9B%BD%E9%9A%9B?ned=jp&hl=ja&gl=JP"
rss_business = "https://news.google.com/news/rss/headlines/section/topic/BUSINESS.ja_jp/%E3%83%93%E3%82%B8%E3%83%8D%E3%82%B9?ned=jp&hl=ja&gl=JP"
rss_seiji ="https://news.google.com/news/rss/headlines/section/topic/POLITICS.ja_jp/%E6%94%BF%E6%B2%BB?ned=jp&hl=ja&gl=JP"
rss_entame ="https://news.google.com/news/rss/headlines/section/topic/ENTERTAINMENT.ja_jp/%E3%82%A8%E3%83%B3%E3%82%BF%E3%83%A1?ned=jp&hl=ja&gl=JP"
rss_sport = "https://news.google.com/news/rss/headlines/section/topic/SPORTS.ja_jp/%E3%82%B9%E3%83%9D%E3%83%BC%E3%83%84?ned=jp&hl=ja&gl=JP"
rss_tech="https://news.google.com/news/rss/headlines/section/topic/SCITECH.ja_jp/%E3%83%86%E3%82%AF%E3%83%8E%E3%83%AD%E3%82%B8%E3%83%BC?ned=jp&hl=ja&gl=JP"

"""
#追加インポート
import bs4, requests

#レスポンス内容の取得
link = "https://news.google.com/"

# Google ニュース 情報取得
get_url_info = requests.get('https://news.google.com/?hl=ja&gl=JP&ceid=JP:ja')
# BeautifulSoup オブジェクトを作成
bs4Obj = bs4.BeautifulSoup(get_url_info.text, 'html.parser')
a =bs4Obj.find_all("a",class_="ipQwMb Q7tWef")

#outputの生成
output = "Googleニュースより、、、\n\n"
#タイトルとリンクすべて取得
for child in a[0:3]:
  output = output + "タイトル:" + child.string+"\n"
  output = output + os.path.join(link,child['href'].lstrip("./")) + "\n\n"
"""

#レスポンス処理
app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    message = ""
    target =""
    output=""
    a =event.message.text
    if a in ("国内","国際","ビジネス","政治","エンタメ","スポーツ","テクノロジ"):
        if event.message.text =="国内":
            target = rss_kokunai
        elif event.message.text=="国際":
            target = rss_kokusai
        elif event.message.text=="ビジネス":
            target = rss_business
        elif event.message.text=="政治":
            target = rss_seiji
        elif event.message.text=="エンタメ":
            target = rss_entame
        elif event.message.text=="スポーツ":
            target = rss_sport
        elif event.message.text=="テクノロジ":
            target = rss_tech

        # rss response 取得
        get_rss_result = feedparser.parse(target)
        output =get_rss_result.feed.title + "\n"
        for entry in get_rss_result.entries[0:3]:
            output = output + entry.title + "\n"
            output = output + entry.link +"\n\n"
    else:
        output = "国内、国際、ビジネス、政治、エンタメ、スポーツ、テクノロジの中から文字列入力してください。"

    message = output

    """
    if event.message.text == "ニュース":
        message = output
    else:
        message = "ニュース以外が入力されましたよ"
    """

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )

"""
    line_bot_api.reply_message(
        event.reply_token,
#        TextSendMessage(text=event.message.text)
        TextSendMessage(text="Hello\\n aaa\n bbb\n\nddd")
    )
"""

#FollowEvent
@handler.add(FollowEvent)
def on_follow(event):
    reply_token = event.reply_token
    user_id = event.source.user_id
    profiles = line_bot_api.get_profile(user_id=user_id)
    display_name = profiles.display_name
    picture_url = profiles.picture_url
    status_message = profiles.status_message

    line_bot_api.reply_message(
        reply_token=reply_token,
        messages=TextSendMessage(text="友達追加ありがとう!!\nこれからよろしく！")
    )
"""
#イベントの動作するタイミングが不明
@handler.add(UnfollowEvent)
def on_unfollow(event):
    reply_token = event.reply_token
    user_id = event.source.user_id
    profiles = line_bot_api.get_profile(user_id=user_id)
    display_name = profiles.display_name
    picture_url = profiles.picture_url
    status_message = profiles.status_message

    line_bot_api.reply_message(
        reply_token=reply_token,
        messages=TextSendMessage(text="またあらためてよろしく！")
    )
"""


"""
# ボタンの入力を受け取るPostbackEvent
@handler.add(PostbackEvent)
def on_postback(event):
    reply_token = event.reply_token
    user_id = event.source.user_id
    postback_msg = event.postback.data

    if postback_msg == 'is_show=1':
        line_bot_api.push_message(
            to=user_id,
            messages=TextSendMessage(text='is_showオプションは1だよ！')
        )
    elif postback_msg == 'is_show=0':
        line_bot_api.push_message(
            to=user_id,
            messages=TextSendMessage(text='is_showオプションは0だよ！')
        )

# ボタンを送信する
def send_button(event, user_id):
    message_template = ButtonsTemplate(
      text='BTC_JPYの通知',
      actions=[
          PostbackAction(
            label='ON',
            data='is_show=1'
          ),
          PostbackAction(
            label='OFF',
            data='is_show=0'
          )
      ]
    )
    line_bot_api.push_message(
        to=user_id,
        messages=PostbackAction(
            alt_text='button template',
            template=message_template
        )
    )
"""



@app.route('/push_garbage_day', methods=['GET'])
def push_garbage_day():
 
    # ゴミの日リスト(1)
    # 0: 月, 1: 火, 2: 水, 3: 木, 4: 金
    garbage_list = {
        0: '可燃・ビン',
        1: 'その他資源',
        2: 'カン・ペッドボトル',
        3: '可燃・ビン',
        4: 'プラ・油・特定品目',
    }
 
    weekdays_list ={
        0: "月",
        1: "火",
        2: "水",
        3: "木",
        4: "金",
        5: "土",
        6: "日"
    }

    weekday = datetime.datetime.now().weekday()
 
#    if weekday == 5 or weekday == 6:
#        return 'OK'
    push_text = "今、" + str(datetime.datetime.now()) + "です。\n"
    push_text += '今日は、' + weekdays_list[weekday] +"曜日だよ。\n"
    push_text += '今日もがんばってね'
    to = 'U8927177e1f082eeb71b1bd09e59a3f4b' # 送信先(2)
    line_bot_api.push_message(to, TextSendMessage(text=push_text))
    line_bot_api.push_message(to, TextSendMessage(text="test"))
 
    return 'OK'

if __name__ == "__main__":
    port = int(os.getenv("PORT",5000))
    app.run(host="0.0.0.0",port=port)


