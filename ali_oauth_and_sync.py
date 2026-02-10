#!/usr/bin/env python3
"""
ali_oauth_and_sync_sandbox.py - OAuth & Sync CLI for Sandbox
Usage:
  python ali_oauth_and_sync_sandbox.py auth_url
  python ali_oauth_and_sync_sandbox.py fetch_token --code YOUR_CODE
  python ali_oauth_and_sync_sandbox.py sync --access_token YOUR_TOKEN
"""
import os
import time
import hashlib
import argparse
import requests
from urllib.parse import urlencode
from app import app
from extensions import db
from models import Product

app.app_context().push()
CLIENT_ID='516252'
CLIENT_SECRET='e6Q6Vk6eMyf7usmncNEd2a9GJrjX7QfM'
REDIRECT_URI='https://braaibitesbeverages.com/auth/callback'
AUTH_URL='https://sandbox.oauth.alibaba.com/authorize'
TOKEN_URL='https://sandbox.oauth.alibaba.com/token'
HOST='https://sandbox.api.alibaba.com'
PATH='/openapi/param2/2/portals.open/api.listPromotionProduct/'

KEYWORDS=['braai grill','braai tools','craft beer','wine','spirits','braai snacks']

def build_auth_url(state):
    params={'response_type':'code','client_id':CLIENT_ID,'redirect_uri':REDIRECT_URI,'state':state,'force_auth':'true'}
    return f"{AUTH_URL}?{urlencode(params)}"

def exchange_code_for_token(code):
    data={'grant_type':'authorization_code','client_id':CLIENT_ID,'client_secret':CLIENT_SECRET,'code':code,'redirect_uri':REDIRECT_URI}
    r=requests.post(TOKEN_URL,data=data); r.raise_for_status(); return r.json().get('access_token')

def compute_sign(path,params):
    items=sorted(params.items()); concat=''.join(f"{k}{v}" for k,v in items)
    raw=CLIENT_SECRET+path+concat+CLIENT_SECRET
    return hashlib.md5(raw.encode('utf-8')).hexdigest().upper()

def fetch_products(token,keyword,page=1):
    full=PATH+CLIENT_ID; url=HOST+full
    params={'keywords':keyword,'page_no':page,'page_size':20,'timestamp':int(time.time()*1000)}
    params['sign']=compute_sign(full,params)
    headers={'Authorization':f"Bearer {token}"}
    r=requests.get(url,params=params,headers=headers); r.raise_for_status()
    j=r.json()
    if 'error_response' in j: raise RuntimeError(j['error_response'])
    return j.get('result',{}).get('products',[])

def sync_all(token):
    for kw in KEYWORDS:
        print(f"🔄 Syncing '{kw}'...")
        for p in range(1,6):
            lst=fetch_products(token,kw,p)
            if not lst: break
            for i in lst:
                prod=Product(id=int(i['productId']),title=i.get('productTitle',''),
                             image=i.get('imageUrl',''),price=float(i.get('salePrice',0)),
                             stock=int(i.get('inventory') or 0),category=kw.title())
                db.session.merge(prod)
            db.session.commit()
            print(f"  • Page {p} synced ({len(lst)})")
    print("✅ Sandbox OAuth sync complete.")

def main():
    p=argparse.ArgumentParser(); sp=p.add_subparsers(dest='cmd',required=True)
    sp.add_parser('auth_url'); f=sp.add_parser('fetch_token'); f.add_argument('--code',required=True)
    s=sp.add_parser('sync'); s.add_argument('--access_token',required=True)
    a=p.parse_args()
    if a.cmd=='auth_url': print(build_auth_url(os.urandom(16).hex()))
    elif a.cmd=='fetch_token': print(exchange_code_for_token(a.code))
    elif a.cmd=='sync': sync_all(a.access_token)

if __name__=='__main__':
    main()
