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
target_store = 59
eapi = "https://eapi.pcloud.com/"
token = "AT2fZ89VHkDT7OaQZMlMlVkZdslpGwQPJNbTKpnbvQtbO8yBYcny"
headers = {"Authorization": f"Bearer {token}"}

async def main(deal):  
  async with httpx.AsyncClient() as client:
    print(deal)
    status = await check_status(client, deal)
    print(status)
    if status:
      products = await get_products(client, deal)
      remainings = await get_remaining_amounts(client, products)
      remainings = filter_remainings(remainings)
      #print(remainings[products[0]["PRODUCT_ID"]])
      for product in products:
        
        product = process_product(product, remainings[str(product["PRODUCT_ID"])])
      total = sum(list(map(lambda item: item["total"], products)))
      documents = await get_documents(client, products)
      await add_products(client, products, documents)
      if "S" in documents:
        ...
        #await update_document(client, documents["S"], total)
      #time.sleep(10)
      await confirm_documents(client, documents)
    client.close()
    
async def get_cdek_token(client):
  url = "https://api.cdek.ru/v2/oauth/token"
  data = {"client_id": cdek_account, "client_secret": cdek_secure_password, "grant_type": "client_credentials"}
  response = client.post(url, data=data)
  response = response.json()
  print(response)
  return response["access_token"]

async def get_cdek_order_number(client, token, im_number):
  url = f"https://api.cdek.ru/v2/orders?im_number={im_number}"
  headers = {"Authorization": f"Bearer {token}"}
  response = client.get(url, headers=headers)
  response = response.json()
  return response["entity"]["cdek_number"]
  
