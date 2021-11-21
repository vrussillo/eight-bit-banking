import requests
import os
from dotenv import load_dotenv
from currencies import curr_logos, key_list

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)



API_KEY = os.environ.get ('API_KEY')

resp = requests.get('https://coinlib.io/api/v1/coinlist', params={'key': API_KEY, 'pref':'USD', 'page': '1', 'order':'volume_desc' })

# coin_id = {"BTC": 859, "AVAX": 1512453}

# # def get_coin_id(coin):
# #     return coin_id.get(coin)

# key_list = list(coin_id.keys())
# value_list = list(coin_id.values())



data = resp.json()



# for key_list in data:
#     print(key_list)

# def coin_function():
#     for coin in data['coins']:
#         if 'WORM' in coin['symbol']:
#             print(coin)
