import os
import re

DEBUG = True

DATABASE_NAME = os.path.abspath('muxtube.db')
SECRET_KEY = '<create some random text and put it here>'

VALID_USERNAME = re.compile('[a-z][a-z0-9]{2,19}')
RESERVED_NAMES = set([
        'root', 'anonymous', 'signup', 'login', 'about', 'muxtube', 'index',
        'bookmarklet', 'settings', 'tracks', 'random', 'explore', 'blog',
        'api', 'home'])
