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

async def create(data):  
  async with httpx.AsyncClient() as client:
    contact_id = await get_contact_id(client, data)
    if contact_id:
      await update_contact(client, contact_id, data)
    else:
      contact_id = await create_contact(client, data)
    data["contact_id"] = contact_id
    data["line_items"] = await set_product_skus(client, data["line_items"])
    fields = get_deal_fields(data)
    payload = { "fields": fields}
    deal = await create_deal(client, payload)
    await set_deal_products(client, deal, data["line_items"])
    
async def update(data):
  async with httpx.AsyncClient() as client:
    #data = match_data(data)
    deals = await get_deals(client, data["id"])
    data = match_data(data)
    if len(deals):
      data["fields"]["ID"] = deals[0]["ID"]
      await update_deal(client, data)
    else: 
      await create_deal(client, data)
      
async def get_cdek_token(client):
  url = "https://api.cdek.ru/v2/oauth/token"
  data = {"client_id": cdek_account, "client_secret": cdek_secure_password, "grant_type": "client_credentials"}
  response = await client.post(url, data=data)
  response = response.json()
  print(response)
  return response["access_token"]
  ...

async def get_cdek_order_data(client, token, im_number):
  url = f"https://api.cdek.ru/v2/orders?im_number={im_number}"
  headers = {"Authorization": f"Bearer {token}"}
  response = await client.get(url, headers=headers)
  response = response.json()
  return response["entity"]

async def update_cdek_number(cdek_number, order):
  async with httpx.AsyncClient() as client:
    deals= await get_deals(client, order)
    data = {
      "id": deals[0]["ID"],
      "fields": {
        "UF_CRM_1765618344040": cdek_number
      }
    }   
    await update_deal(client, data)
  
async def create_deal(client, data):
  url = bitrix_webhook + "crm.deal.add"
  response = await client.post(url, json=data)
  response = response.json()
  print(response)
  return response["result"]

async def update_deal(client, data):
  url = bitrix_webhook + "crm.deal.update"
  response = await client.post(url, json=data)
  print(response.json())
  
async def get_deals(client, order):
  url = bitrix_webhook + "crm.deal.list"
  data = {"filter": {"ORIGIN_ID": order}}
  response = await client.post(url, json=data)
  response = response.json()
  print(response)  
  return response["result"]

async def set_deal_products(client, id, line_items):
  url = bitrix_webhook + "crm.deal.productrows.set"
  rows = list(map(lambda item: {"PRODUCT_ID": item["crm_id"], "QUANTITY": item["quantity"]}, line_items))
  data = {"ID": id, "rows": rows}
  response = await client.post(url, json=data)
  print(response.json())

async def get_deal_products(client, line_items):
  url = bitrix_webhook + "catalog.products.list"
  sku_list = list(map(lambda item: item["sku"], line_items))
  data = {"select": ["id", "property159"], "filter": {"iblockId": 17, "property159": sku_list}}
  print(data)
  response = await client.post(url, json=data)
  response = response.json()
  return response["result"]["products"]
  
async def set_product_skus(client, line_items):
  products = await get_deal_products(client, line_items)
  print(products)
  for item in line_items:
    item["crm_id"] = list(filter(lambda product: product["property159"]["value"] == item["sku"], products))
  return line_items
  
async def get_contacts(client, data):
  url = bitrix_webhook + "crm.contact.list"
  response = await client.post(url, json=data)
  response = response.json()
  return response["result"]

async def get_contact_id(client, data):
  filter_list = [{"EMAIL": data["billing"]["email"]}, {"PHONE": data["billing"]["phone"]}]
  for filter in filter_list:
    data = {"filter": filter}
    contacts = await get_contacts(client, data)
    if contacts:
      return contacts[0]["ID"]
  return ""

async def get_contact_data(client, id):
  url = bitrix_webhook + "crm.contact.get"
  data = {"ID": id }
  response = await client.post(url, json=data)
  response = response.json()
  return response["result"]
  
async def create_contact(client, data):
  url = bitrix_webhook + "crm.contact.add"
  fields = {
    "NAME": data["shipping"]["first_name"],
    "LAST_NAME": data["shipping"]["last_name"],
    "EMAIL": [
        {
          "VALUE": data["billing"]["email"]
        }
    ],
    "PHONE": [
        {
          "VALUE": data["shipping"]["phone"]
        }
    ]
  }
  data = {"fields": fields}
  response = await client.post(url, json=data)
  response = response.json()
  return response["result"]["ID"]
    
async def update_contact(client, contact_id, data):
  url = bitrix_webhook + "crm.contact.update"
  fields = {
    "NAME": data["shipping"]["first_name"],
    "LAST_NAME": data["shipping"]["last_name"],
    "EMAIL": [
        {
          "VALUE": data["billing"]["email"]
        }
    ],
    "PHONE": [
        {
          "VALUE": data["shipping"]["phone"]
        }
    ]
  }
  payload = {
    "ID": contact_id,
    "fields": fields
  }
  print(payload)
  response = await client.post(url, json=payload)
  response = response.json()
  print(response)
  return response
  
async def update_encoding(data):
  async with httpx.AsyncClient() as client:
    await update_deal(client, data)
    
def get_deal_fields(data):
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
  #print(data["sbjs_current"])
  #print(unquote(data["sbjs_current"]))
  #items = 
  fields = {
    "TITLE": f"Заказ #{data["id"]}",
    "CATEGORY_ID": 0,
    "STAGE_ID": "NEW",
    "COMMENTS": "\n".join(list(map(lambda item: f"{item["name"]} - {item["quantity"]}: {item["total"]}", order_data["items"]))),
    "ORIGIN_ID": data["id"],
    "OPPORTUNITY": data["total"],
    "CONTACT_ID": data["contact_id"],
    "ASSIGNED_BY_ID": 17,
    "UF_CRM_DLYALUDEIRU57": data["id"],
    "UF_CRM_67978D249E9AE": order_data["payment_method"],
    #ym client id 
    #"UF_CRM_1765627743791": data["ym_client_id"],
    #адрес доставки 
    "UF_CRM_1765783423126": f"{data["shipping"]["city"]}, {data["shipping"]["address_1"]}, {data["shipping"]["postcode"]}",
    #тип доставки
    "UF_CRM_1765783446849": data["shipping_lines"][0]["method_title"],
    #телефон
    "UF_CRM_1765783469498": data["shipping"]["phone"],
    #email
    "UF_CRM_1765783595133": data["billing"]["email"],
    #оплачено
    "UF_CRM_1765783623915": "",
    "UTM_SOURCE": "",
    "UTM_MEDIUM": "",
    "UTM_CAMPAIGN": "",
    "UTM_CONTENT": "", 
    "UTM_TERM": ""
  }
  return fields
