import requests
import os

URL = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
#API_KEY = os.environ.get('HOTPEPPER_API')
API_KEY = '1492fa1612238816'
print(API_KEY)
body = {
    'key':API_KEY,
    'keyword':'恵比寿駅',
    'format':'json',
    'count':15
}

# APIに必要なURLや変数に格納したbodyをもとに、requestsライブラリでリクエスト
# リクエストしたデータをresponseの変数に格納
response = requests.get(URL,body)

# 取得したデータからJSONデータを取得
datum = response.json()
# JSONデータの中からお店のデータを取得
#print(datum)
stores = datum['results']['shop']
# お店のデータの中から、店名を抜き出して表示させる
for store_name in stores:
    name = store_name['name']
    print(name)
