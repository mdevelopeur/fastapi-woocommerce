from urllib.parse import unquote
from datetime import datetime
import httpx
import re
import math
import numbers
import time
import os
import redis
import random 
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")
cdek_account = os.getenv("cdek_account")
cdek_secure_password = os.getenv("cdek_secure_password")
bitrix_webhook = os.getenv("bitrix_webhook")
#target_store = 59
#eapi = "https://eapi.pcloud.com/"
#token = "AT2fZ89VHkDT7OaQZMlMlVkZdslpGwQPJNbTKpnbvQtbO8yBYcny"
#headers = {"Authorization": f"Bearer {token}"}

async def main(data):  
  async with httpx.AsyncClient() as client:
    cdek_token = await get_cdek_token(client)
    cdek_order_data = await get_cdek_order_data(client, cdek_token, data["id"])
    print(cdek_order_data)
    
    
async def get_cdek_token(client):
  url = "https://api.cdek.ru/v2/oauth/token"
  data = {"client_id": cdek_account, "client_secret": cdek_secure_password, "grant_type": "client_credentials"}
  response = await client.post(url, data=data)
  response = response.json()
  print(response)
  return response["access_token"]

async def get_cdek_order_data(client, token, im_number):
  url = f"https://api.cdek.ru/v2/orders?im_number={im_number}"
  headers = {"Authorization": f"Bearer {token}"}
  response = await client.get(url, headers=headers)
  response = response.json()
  return response["entity"]

async def create_deal(client, data):
  url = bitrix_webhook + "crm.deal.add"
  response = await client.post(url, json=data)
  print(response.json())

def match_data(data):
  output = {}
  
