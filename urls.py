# -*- coding: utf-8 -*-
import os
from tornado import web
from handlers import base



url_patterns = [
    (r'/', base.MainHandler),
    (r'/random/', base.GenerateRandomNumbers),
    (r'/scramble_message/', base.ScrambleText),
    (r'/file_upload/', base.FileUpload),
    (r'/scramble_image/', base.ScrambleImage),
    (r'/(.*)', web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "static")}),
]