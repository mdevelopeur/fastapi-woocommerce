from fastapi import FastAPI, Request
import multipart
import re
from api.functions import main
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

@app.post('/api/webhook')
async def post_handler(request: Request):
    try: 
        data = await request.json()
        await main(data)
        return 
    except Exception as e:
        print(e)
        return e
