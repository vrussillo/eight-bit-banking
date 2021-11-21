import requests
import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_KEY = os.environ.get ('API_KEY')

resp = requests.get('https://coinlib.io/api/v1/coin?key=589564bfc67234c3&pref=USD&symbol=BTC', params={'key': API_KEY, 'symbol':'ADA'})

coin_id = {"BTC": 859, "AVAX": 1512453}

# def get_coin_id(coin):
#     return coin_id.get(coin)

key_list = list(coin_id.keys())
value_list = list(coin_id.values())




# API_SECRET = 'OggoQmwD0VbsC4VKHflur1gX5ETTtNpF'



# data = resp.json()

# for result in data['results']:
#     print(result['symbol'])
