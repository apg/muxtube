# muxtube - like muxtape, but for YouTube

## What?

Justin Ouellete originally created Muxtape which was a way to share 12 mp3s
online with the world. It has since morphed into a "platform for bands."

So, I, Andrew Gwozdziewycz, thought it'd be cool to bring back the original
spirit of Muxtape, but using YouTube videos instead of mp3s. However, I've 
gotten lazy, and haven't finished it. Would you like to contribute?

It's using bottle.py, and SQLObject, and it's GPL'd


## Requirements

SQLObject, Python 2.[5-6]


## Install:

    $ python
    >>> import random
    >>> import string
    >>> ''.join([random.choice(string.printable) for _ in range(128)])
    'some long string'
    $ vi settings.py # plug the string in the SECRET_KEY spot
    $ python models.py # this creates the database -- sqlite


## It's not Finished

### Bookmarklet

There should be a bookmarklet, but I never finished writing it. The idea is
that each account gets it's own bookmarklet based on 128 random characters, and
the job of it is to issue a GET request like to the url: 

    /bookmarklet/add?token=<128 character token>&title=<title>&video_id=<id>

I was only going to make it work from YouTube, but it'd be neat if it worked 
wherever YouTube videos are embedded.


### UI

The UI is mostly there, but it's a bit buggy. It doesn't have a way to pause,
nor does it properly place the video. You can play videos of course.

I'm not thrilled about the styles, but whatever.


### Security

Yeah, this isn't your bank account, so it's not ultimate security level A, but
passwords are hashed, *I think* sensibly--you decide. The bookmarklet idea
obviously could use some work with the token, but again--who cares? I just
didn't wanna have to write a more complicated bookmark which made you sign in
if you weren't already signed in. That's all.


## Other Concerns

Oh, and this is probably all against YouTube's terms of service, but I set it
up so you can show the video thinking that hiding them by default would
certainly be a violation--showing them, well, maybe not. If you launch this
somewhere, be forewarned.


## Legal

Copyright 2010, Andrew Gwozdziewycz <web@apgwoz.com>. Licensed under the GPL.
see COPYING for details.