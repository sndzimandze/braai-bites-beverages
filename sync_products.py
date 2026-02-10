#!/usr/bin/env python3
"""
sync_products_sandbox.py - Fetch products from AliExpress Sandbox using AppKey + signed requests
Usage:
  1) pip install requests
  2) python sync_products_sandbox.py
"""
import time
import hashlib
import requests
from app import app
from extensions import db
from models import Product

app.app_context().push()
API_KEY = '516252'
API_SECRET = 'e6Q6Vk6eMyf7usmncNEd2a9GJrjX7QfM'
HOST = 'https://sandbox.api.alibaba.com'
PATH = '/openapi/param2/2/portals.open/api.listPromotionProduct/'

KEYWORDS = ['braai grill','braai tools','craft beer','wine','spirits','braai snacks']

def compute_sign(path, params):
    items = sorted(params.items())
    concat = ''.join(f"{k}{v}" for k,v in items)
    raw = API_SECRET + path + concat + API_SECRET
    return hashlib.md5(raw.encode('utf-8')).hexdigest().upper()

def fetch_products(keyword, page=1):
    full_path = PATH + API_KEY
    url = HOST + full_path
    params = {'keywords':keyword,'page_no':page,'page_size':20,'timestamp':int(time.time()*1000)}
    params['sign'] = compute_sign(full_path, params)
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    if 'error_response' in data:
        raise RuntimeError(data['error_response'])
    return data.get('result',{}).get('products',[])

def sync_all():
    for kw in KEYWORDS:
        print(f"🔄 Syncing '{kw}'...")
        for page in range(1,6):
            prods = fetch_products(kw, page)
            if not prods: break
            for p in prods:
                prod = Product(id=int(p['productId']),title=p.get('productTitle',''),
                                image=p.get('imageUrl',''),price=float(p.get('salePrice',0)),
                                stock=int(p.get('inventory',0)),category=kw.title())
                db.session.merge(prod)
            db.session.commit()
            print(f"  • Page {page} synced ({len(prods)})")
    print("✅ Sandbox sync complete.")

if __name__=='__main__':
    sync_all()
