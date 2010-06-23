import hmac
import urllib
import base64
import random
from functools import wraps, partial

from bottle import route, view, request, response, run, debug, send_file,\
    redirect, abort

from models import Track, User, foreground_color, hash_password

from settings import SECRET_KEY, VALID_USERNAME
import settings

DEBUG = getattr(settings, 'DEBUG', False)

ONE_YEAR = 31536000


def b32enc(value):
    if value:
        return base64.b32encode(value).replace('=', '-')
    return ''


def b32dec(value):
    if value:
        return base64.b32decode(value.replace('-', '='))
    return None


def sign(value):
    signed = hmac.HMAC(SECRET_KEY + value).hexdigest() + ';' + value
    return b32enc(signed)


def unsign(signed):
    try:
        decoded = b32dec(signed)
        if ';' in decoded:
            hashed, value = decoded.split(';', 1)
            valid = hmac.HMAC(SECRET_KEY + value).hexdigest() == hashed
        else:
            valid, value = '', ''
        return (valid, value)
    except TypeError:
        return (False, None)


def login_user(username):
    user_cookie = sign(username)
    response.set_cookie('user', user_cookie, expires=ONE_YEAR*2)


def logout_user():
    response.set_cookie('user', '', expires=-ONE_YEAR)


def context(**kwargs):
    tmp = {'request': request,
           'foreground_color': foreground_color,
           'error': None}
    tmp.update(kwargs)
    return tmp


def maybe_login(go_home=False):
    """Returns a function which itself is a decorator, which will add 
    `username` to the request object, if the user is logged in.

    If `go_home` is True, when logged in, the user will be redirected to their
    homepage.
    """
    
    def decorator(func):

        @wraps(func)
        def _(*args, **kwargs):
            valid, username = unsign(request.get_cookie('user', ''))
            if valid:
                # if it's valid, OK, otherwise, they're not logged in. we don't 
                # necessarily expect them to be here.
                request.username = username
                if go_home:
                    redirect('/%s' % username)
            else:
                request.username = None

            return func(*args, **kwargs)
        return _
    return decorator


def login_required(func):

    @wraps(func)
    def _(*args, **kwargs):
        valid, username = unsign(request.get_cookie('user', ''))
        if not valid or not username:
            redirect('/login?next=%s' % sign('%s?%s' % (request.fullpath,
                                                        request.query_string)))
        # the assertion is that we'll never set a valid cookie for a user that
        # doesn't exist. ... famous last words of course
        request.username = username
        return func(*args, **kwargs)

    return _


@route('/static/js/:filename')
def static_file(filename):
    send_file(filename, root='static/js')


@route('/static/images/:filename')
def static_file(filename):
    send_file(filename, root='static/images')


@route('/static/css/:filename')
def static_file(filename):
    send_file(filename, root='static/css')


@route('/about')
@view('about')
def about():
    return context()


@route('/signup')
@route('/signup', method='POST')
@maybe_login(go_home=True)
@view('signup')
def signup():
    if request.method == 'POST':
        user = None
        username = request.POST.get('username', '').lower()
        print 'username', username
        if VALID_USERNAME.match(username):
            user = User.new(username, request.POST.get('password', ''))
            if not user:
                return {'error': 'Username already taken.'}
            redirect('/%s' % user.username)
        else:
            return context(error='Invalid username')
    return context()


@route('/login')
@route('/login', method='POST')
@maybe_login(go_home=True)
@view('login')
def login():
    username = request.POST.get('username', '')
    if request.method == 'POST' and username:
        user = User.selectBy(username=username).getOne(None)
        if user and user.check_password(request.POST.get('password', '')):
            login_user(user.username)
            next = request.GET.get('next', None)
            if next:
                valid, value = unsign(next)
                if valid:
                    redirect(value)
                else:
                    abort(400)
            else:
                redirect('/%s' % username)
        else:
            return context(error='Invalid username or password')
    else:
        return context()


@route('/logout')
def logout():
    logout_user()
    redirect('/')


@route('/random')
def random_tube():
    """A random muxtube"""
    count = User.select().count()
    r = random.randint(0, count-1)
    user = User.select()[r]
    redirect('/%s' % user.username)


@route('/bookmarklet')
@login_required
@view('bookmarklet')
def bookmarklet():
    user = User.selectBy(username=request.username).getOne(None)
    return context(user=user)


# fdp4a78PvRMgJ4Dj1jHFNTNyTBYgc386JeIB6Mcm0oPaXSpdwVRqmVSeQToZqvH1sTfvZI2pAqwdeIuDdoCZEuFmv1&title=Have Nots - One in Four&video_id=OFNZA1vTUKU
@route('/bookmarklet/add')
def bookmarklet_add():
    video_id = request.GET.get('video_id', '')
    title = request.GET.get('title', 'Default Title')
    token = request.GET.get('token', '')

    user = None

    if len(token) == 128:
        user = User.selectBy(bookmarklet=token).getOne(None)

    if not user:
        return {'error': ("The token was either not present or invalid."
                          "Please reinstall your bookmarklet"),
                'status': 'error'}

    if not video_id:
        return {'error': "Cannot add video because of an invalid video id",
                'status': 'error'}

    track = Track(user=user, title=title, video_id=video_id)
    if track:
        return {'error': '',
                'status': 'success'}
    return {'error': "Could not add video",
            'status': 'error'}


@route('/settings')
@route('/settings', method='POST')
@login_required
@view('settings')
def settings():
    user = User.selectBy(username=request.username).getOne(None)
    if not user:
        abort(403)

    errors = {
        'password_error': '',
        'color_error': '',
        'general_error': '',
        }

    if request.method == 'POST':
        print 'settings!'
        updates = {}
    
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')

        # password
        if old_password or new_password:
            if not user.check_password(old_password):
                errors['password_error'] = 'Incorrect password'
            else:
                updates['password'] = hash_password(new_password)

        # color
        color = request.POST.get('color', '')
        if color:
            try:
                if len(color) == 6 and (int(color, 16) or color == '000000'):
                    updates['color'] = color.lower()
                else:
                    errors['color_error'] = 'A 6 digit hex number is required'
            except ValueError:
                errors['color_error'] = 'Not a valid hexidecimal number'

        print updates
        if updates:
            user.set(**updates)

    return context(user=user, **errors)


@route('/:username')
@maybe_login()
@view('tracks')
def user_home(username):
    user = User.selectBy(username=username).getOne(None)
    if not user:
        abort(404)
    else:
        tracks = Track.selectBy(user=user)
    return context(user=user, tracks=tracks)


@route('/')
@maybe_login()
@view('index')
def index():
    return context()
    

if __name__ == '__main__':
    debug(DEBUG)
    run(reloader=True)
