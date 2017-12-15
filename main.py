import os

# Django specific settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


import sys
# add the project path into the sys.path
sys.path.append('/tmp/web/python/scrapy/gazzetta')
# add the virtualenv site-packages path to the sys.path
# sys.path.append('/tmp/venv/Lib/site-packages')
sys.path.append('/tmp/web/python/scrapy/venv/Lib/site-packages')


# noinspection PyUnresolvedReferences
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


if __name__ == '__main__':
    from players.controller import Controller
    c = Controller()
