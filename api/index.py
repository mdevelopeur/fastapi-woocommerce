from fastapi import FastAPI, Request
import multipart
import re
from api.functions import create, update, update_encoding
from urllib.parse import unquote, urlparse

app = FastAPI()

@app.get('/api/webhook')
async def get_handler():
    try:
        ...
        return 
    except Exception as e:
        print(e)
        return e

@app.post('/api/create')
async def create_deal(request: Request):
    try: 
        data = await request.json()
        print(data)
        await create(data)
        return 
    except Exception as e:
        print(e)
        return e

@app.post('/api/update')
async def create_deal(request: Request):
    try: 
        data = await request.json()
        print(data)
        await update(data)
        return 
    except Exception as e:
        print(e)
        return e

@app.post('/api/delete')
async def create_deal(request: Request):
    try: 
        data = await request.json()
        print(data)
        await main(data)
        return 
    except Exception as e:
        print(e)
        return e

@app.post('/api/update_encoding')
async def create_deal(request: Request):
    try: 
        data = await request.json()
        print(data)
        await update_encoding(data)
        return 
    except Exception as e:
        print(e)
        return e
