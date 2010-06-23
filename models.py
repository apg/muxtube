import hmac
import datetime
import random
import string

import settings

from sqlobject import *
sqlhub.processConnection = connectionForURI('sqlite://' + settings.DATABASE_NAME)

alpha_numeric = string.letters + string.digits


def foreground_color(bg, dark='000000', light='ffffff'):
    if bg.startswith('#'):
        h = bg[1:]
    else:
        h = bg
    try:
        return dark if int(h, 16) > 0x7fffff else light
    except:
        return 'ffffff'


def generate_color():
    print "in generate_color"
    return ''.join('%02x' % random.randint(0, 255) for x in range(3))


def hash_password(password):
    h = hmac.HMAC(settings.SECRET_KEY, password)
    return h.hexdigest()


class User(SQLObject):
    username = StringCol(length=3)
    password = StringCol(length=32)
    bookmarklet = StringCol(length=128)
    color = StringCol(length=6, default=generate_color)
    added = DateTimeCol(default=datetime.datetime.now)

    username_index = DatabaseIndex('username')
    
    @classmethod
    def new(cls, username, password):
        if username not in settings.RESERVED_NAMES and \
                not User.selectBy(username=username).getOne(None):
            bookmarklet = ''.join(random.choice(alpha_numeric)
                                  for n in range(128))
            user = User(username=username, password=hash_password(password),
                        bookmarklet=bookmarklet)
            return user
        return None

    def check_password(self, raw):
        hashed = hash_password(raw)
        return self.password == hashed

    def change_password(self, password):
        self.password = hash_password(password)
        

class Track(SQLObject):
    user = ForeignKey('User')
    video_id = StringCol(length=50)
    title = StringCol(length=255)
    added = DateTimeCol(default=datetime.datetime.now)

    @classmethod
    def tracks_for_user(cls, user):
        return Track.selectBy(user=user)


def init():
    User.createTable(ifNotExists=True)
    Track.createTable(ifNotExists=True)


if __name__ == '__main__':
    init()
