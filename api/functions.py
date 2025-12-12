from urllib.parse import unquote
from datetime import datetime
import httpx
import re
import math
import numbers
import time
import os
import json
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

async def create(data):  
  async with httpx.AsyncClient() as client:
    #cdek_token = await get_cdek_token(client)
    #cdek_order_data = await get_cdek_order_data(client, cdek_token, data["id"])
    #print(cdek_order_data)
    data = match_data(data)
    await create_deal(client, data)

async def update(data):
  async with httpx.AsyncClient() as client:
    #data = match_data(data)
    deal = await get_deal(client, data["id"])
    data = match_data(data)
    data["fields"]["ID"] = deal
    await update_deal(client, data)
    
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

async def update_deal(client, data):
  url = bitrix_webhook + "crm.deal.update"
  response = await client.post(url, json=data)
  print(response.json())
  
async def get_deal(client, id):
  url = bitrix_webhook + "crm.deal.list"
  data = {"filter": {"ORIGIN_ID": id}}
  response = await client.post(url, json=data)
  print(response.json())
  return response["result"]["ID"]

async def update_encoding(data):
  async with httpx.AsyncClient() as client:
    await update_deal(client, data)
    
def match_data(data):
  order_data = {
    "id": data["id"], 
    "status": data["status"],
    "total": data["total"],
    "name": f"{data["shipping"]["first_name"]} {data["shipping"]["last_name"]}",
    "email": data["billing"]["email"],
    "phone": data["shipping"]["phone"],
    "address": f"{data["shipping"]["city"]}, {data["shipping"]["address_1"]}, {data["shipping"]["postcode"]}",
    "payment_method": data["payment_method_title"],
    "items": list(map(lambda item: {"name": item["name"], "quantity": item["quantity"], "total": item["total"]}, data["line_items"])),
  }
  #items = 
  fields = {
    "TITLE": f"Заказ #{order_data["id"]}",
    "CATEGORY_ID": 0,
    "STAGE_ID": "NEW",
    "COMMENTS": "\n".join(list(map(lambda item: f"{item["name"]} - {item["quantity"]}: {item["total"]}", order_data["items"]))),
    "ORIGIN_ID": order_data["id"],
    "OPPORTUNITY": order_data["total"],
    "UF_CRM_DLYALUDEIRU57": order_data["id"],
    "UF_CRM_67978D249E9AE": order_data["payment_method"]
    
  }
  return {"fields": fields}
