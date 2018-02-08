import os

# Django specific settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import sys
# sys.path.append('/tmp/venv/Lib/site-packages')
venv_path = os.getcwd() + r'\venv\Lib\site-packages'
sys.path.append(venv_path)
# add the project path into the sys.path
sys.path.append(os.getcwd() + r'\gazzetta')
# add the virtualenv site-packages path to the sys.path


# noinspection PyUnresolvedReferences
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


if __name__ == '__main__':
    from players.controller import Controller
    c = Controller()
