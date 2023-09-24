"""
WSGI config for flea_market_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# load_dotenv を追加
from dotenv import load_dotenv

load_dotenv()

# "flea_market_app.settings.dev" に変更
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flea_market_app.settings.dev')

application = get_wsgi_application()
