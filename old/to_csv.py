import json
import requests
import pandas as pd

URL = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
#API_KEY = os.environ.get('HOTPEPPER_API')
HOTPEPPER_API_KEY = '1492fa1612238816'

api_key = HOTPEPPER_API_KEY

i_start = 1
restaurant_datas=[]

#while True:
query = {
	'key': api_key,
	'large_area': 'Z011', # 東京
	'order': 1, #名前の順
	'start': i_start, #検索結果の何番目から出力するか
	'count': 10, #最大取得件数
	'format': 'json'
}
url_base = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
responce = requests.get(url_base, query)
result = json.loads(responce.text)['results']['shop']
if len(result) == 0:
	#break
	print("0")
for restaurant in result:
	restaurant_datas.append([restaurant['name'], restaurant['address'], restaurant['budget']['code'], restaurant['genre']['code']])
i_start += 100
print(i_start)

columns = ['name', 'address', 'budget', 'genre']
df_restaurants = pd.DataFrame(restaurant_datas, columns=columns)
print(df_restaurants)
df_restaurants.to_csv('restaurants_tokyo.csv')
