#!/usr/bin/env python3
"""
AliExpress Product Synchronization Utility

This module handles both OAuth and direct API synchronization with AliExpress.
It consolidates functionality from previous sync_products.py and ali_oauth_and_sync.py

Usage:
    # Generate OAuth URL
    python -m app.utils.aliexpress_sync auth-url

    # Exchange authorization code for access token
    python -m app.utils.aliexpress_sync fetch-token --code YOUR_CODE

    # Sync products using OAuth token
    python -m app.utils.aliexpress_sync sync-oauth --token YOUR_TOKEN

    # Sync products using API key (simpler, no OAuth)
    python -m app.utils.aliexpress_sync sync
"""
import os
import time
import hashlib
import logging
import argparse
import requests
from urllib.parse import urlencode
from typing import List, Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Product categories to sync
DEFAULT_KEYWORDS = [
    'braai grill',
    'braai tools',
    'craft beer',
    'wine',
    'spirits',
    'braai snacks'
]


class AliExpressSync:
    """Handle AliExpress API synchronization"""

    def __init__(self, app_key: str, app_secret: str, api_host: str = None):
        """
        Initialize the sync utility

        Args:
            app_key: AliExpress App Key
            app_secret: AliExpress App Secret
            api_host: API host URL (sandbox or production)
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.api_host = api_host or 'https://sandbox.api.alibaba.com'
        self.api_path = '/openapi/param2/2/portals.open/api.listPromotionProduct/'

    def compute_signature(self, path: str, params: Dict) -> str:
        """
        Compute MD5 signature for API request

        Args:
            path: API endpoint path
            params: Request parameters

        Returns:
            Uppercase MD5 hash signature
        """
        sorted_params = sorted(params.items())
        concat = ''.join(f"{k}{v}" for k, v in sorted_params)
        raw = f"{self.app_secret}{path}{concat}{self.app_secret}"
        return hashlib.md5(raw.encode('utf-8')).hexdigest().upper()

    def fetch_products(self, keyword: str, page: int = 1,
                       page_size: int = 20, access_token: Optional[str] = None) -> List[Dict]:
        """
        Fetch products from AliExpress API

        Args:
            keyword: Search keyword
            page: Page number
            page_size: Number of products per page
            access_token: OAuth access token (optional)

        Returns:
            List of product dictionaries
        """
        try:
            full_path = f"{self.api_path}{self.app_key}"
            url = f"{self.api_host}{full_path}"

            params = {
                'keywords': keyword,
                'page_no': page,
                'page_size': page_size,
                'timestamp': int(time.time() * 1000)
            }

            # Compute signature
            params['sign'] = self.compute_signature(full_path, params)

            # Add OAuth token if provided
            headers = {}
            if access_token:
                headers['Authorization'] = f"Bearer {access_token}"

            # Make API request
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if 'error_response' in data:
                error_msg = data['error_response']
                logger.error(f"API error: {error_msg}")
                raise RuntimeError(f"AliExpress API error: {error_msg}")

            products = data.get('result', {}).get('products', [])
            logger.info(f"Fetched {len(products)} products for keyword '{keyword}', page {page}")

            return products

        except requests.RequestException as e:
            logger.error(f"HTTP request error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            raise

    def sync_to_database(self, keywords: List[str] = None,
                        max_pages: int = 5, access_token: Optional[str] = None):
        """
        Sync products from AliExpress to local database

        Args:
            keywords: List of search keywords
            max_pages: Maximum pages to fetch per keyword
            access_token: OAuth access token (optional)
        """
        from app import create_app
        from extensions import db
        from models import Product

        app = create_app()

        keywords = keywords or DEFAULT_KEYWORDS
        total_synced = 0

        with app.app_context():
            for keyword in keywords:
                logger.info(f"Syncing products for '{keyword}'...")

                for page in range(1, max_pages + 1):
                    try:
                        products = self.fetch_products(
                            keyword=keyword,
                            page=page,
                            access_token=access_token
                        )

                        if not products:
                            logger.info(f"No more products for '{keyword}' at page {page}")
                            break

                        # Save products to database
                        for product_data in products:
                            try:
                                product = Product(
                                    id=int(product_data['productId']),
                                    title=product_data.get('productTitle', ''),
                                    image=product_data.get('imageUrl', ''),
                                    price=float(product_data.get('salePrice', 0)),
                                    stock=int(product_data.get('inventory', 0)),
                                    category=keyword.title()
                                )
                                db.session.merge(product)
                                total_synced += 1

                            except Exception as e:
                                logger.error(f"Error processing product: {e}")
                                continue

                        db.session.commit()
                        logger.info(f"✓ Synced page {page} for '{keyword}' ({len(products)} products)")

                    except Exception as e:
                        logger.error(f"Error syncing page {page} for '{keyword}': {e}")
                        db.session.rollback()
                        break

            logger.info(f"✅ Sync complete! Total products synced: {total_synced}")


class AliExpressOAuth:
    """Handle AliExpress OAuth authentication"""

    def __init__(self, client_id: str, client_secret: str,
                 redirect_uri: str, auth_url: str, token_url: str):
        """
        Initialize OAuth handler

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: OAuth redirect URI
            auth_url: Authorization URL
            token_url: Token exchange URL
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = auth_url
        self.token_url = token_url

    def build_auth_url(self, state: str) -> str:
        """
        Generate OAuth authorization URL

        Args:
            state: Random state parameter for security

        Returns:
            Authorization URL
        """
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'force_auth': 'true'
        }
        url = f"{self.auth_url}?{urlencode(params)}"
        logger.info(f"Generated auth URL: {url}")
        return url

    def exchange_code_for_token(self, code: str) -> str:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Access token
        """
        try:
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': self.redirect_uri
            }

            response = requests.post(self.token_url, data=data, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            access_token = token_data.get('access_token')

            if not access_token:
                raise ValueError("No access token in response")

            logger.info("Successfully obtained access token")
            return access_token

        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise


def main():
    """Command-line interface"""
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Get configuration from environment
    app_key = os.getenv('ALIEXPRESS_APP_KEY')
    app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
    api_host = os.getenv('ALIEXPRESS_HOST', 'https://sandbox.api.alibaba.com')
    redirect_uri = os.getenv('ALIEXPRESS_REDIRECT_URI')
    auth_url = os.getenv('ALIEXPRESS_AUTH_URL')
    token_url = os.getenv('ALIEXPRESS_TOKEN_URL')

    if not app_key or not app_secret:
        logger.error("ALIEXPRESS_APP_KEY and ALIEXPRESS_APP_SECRET must be set in .env file")
        return

    # Setup argument parser
    parser = argparse.ArgumentParser(description='AliExpress Product Sync Utility')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Auth URL command
    subparsers.add_parser('auth-url', help='Generate OAuth authorization URL')

    # Fetch token command
    token_parser = subparsers.add_parser('fetch-token', help='Exchange auth code for token')
    token_parser.add_argument('--code', required=True, help='Authorization code')

    # Sync command (API key based)
    sync_parser = subparsers.add_parser('sync', help='Sync products using API key')
    sync_parser.add_argument('--keywords', nargs='+', help='Keywords to search')
    sync_parser.add_argument('--pages', type=int, default=5, help='Max pages per keyword')

    # Sync OAuth command
    sync_oauth_parser = subparsers.add_parser('sync-oauth', help='Sync products using OAuth token')
    sync_oauth_parser.add_argument('--token', required=True, help='OAuth access token')
    sync_oauth_parser.add_argument('--keywords', nargs='+', help='Keywords to search')
    sync_oauth_parser.add_argument('--pages', type=int, default=5, help='Max pages per keyword')

    args = parser.parse_args()

    # Execute command
    if args.command == 'auth-url':
        oauth = AliExpressOAuth(app_key, app_secret, redirect_uri, auth_url, token_url)
        state = os.urandom(16).hex()
        print(oauth.build_auth_url(state))

    elif args.command == 'fetch-token':
        oauth = AliExpressOAuth(app_key, app_secret, redirect_uri, auth_url, token_url)
        token = oauth.exchange_code_for_token(args.code)
        print(f"Access Token: {token}")

    elif args.command == 'sync':
        sync = AliExpressSync(app_key, app_secret, api_host)
        sync.sync_to_database(keywords=args.keywords, max_pages=args.pages)

    elif args.command == 'sync-oauth':
        sync = AliExpressSync(app_key, app_secret, api_host)
        sync.sync_to_database(
            keywords=args.keywords,
            max_pages=args.pages,
            access_token=args.token
        )


if __name__ == '__main__':
    main()
