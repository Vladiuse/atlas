import os
import sys

from django.core.wsgi import get_wsgi_application

site_user_root_dir = "/home/v/vladiuse/atlas.vim-store.ru/public_html"
sys.path.insert(0, site_user_root_dir + "/atlas")
sys.path.insert(1, site_user_root_dir + "/venv/lib/python3.11/site-packages")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "atlas.settings")


application = get_wsgi_application()
