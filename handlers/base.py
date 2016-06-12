# -*- coding: utf-8 -*-
import os, uuid, time, StringIO
import traceback

import tornado
import tornado.web
from PIL import Image

from utils.ranrot import RanrotBGenerator, RanrotWGenerator
from utils.scramble import MessageScrambler, ImageScrambler

import random as randomMT


PRNGS_MAP = {
    'default': randomMT,
    'ranrotB': RanrotBGenerator(),
    'ranrotW': RanrotWGenerator(),
}


def get_generator(gen_key, size=12345):
    try:
        key_parts = gen_key.split(':')
        random_cls = PRNGS_MAP.get(key_parts[0], randomMT)
        seed = int(key_parts[1])
        seq = int(key_parts[2])
        random_cls.seed(seed)
        random_cls.jumpahead(seq)
        ret = random_cls
    except Exception as e:
        randomMT.seed(hash(size))
        randomMT.jumpahead(size)
        ret = randomMT
        gen_key = 'default:' + str(hash(size)) + ':' + str(size)

    return ret, gen_key


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class GenerateRandomNumbers(tornado.web.RequestHandler):
    def get(self):
        seed = int(self.get_argument('seed', time.time()))
        limit = min(int(self.get_argument('count', 10000)), 10000)
        random = PRNGS_MAP.get(self.get_argument('generator', 'default'))
        random.seed(seed)
        rows = limit / 10
        extra = limit % 10
        for i in xrange(rows):
            self.write(', '.join(['{:10.12f}'.format(random.random())
                                  for _ in xrange(10)]))
            self.write('<br>')
        self.write(', '.join(['{:10.12f}'.format(random.random())
                              for _ in xrange(extra)]))



class ScrambleText(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        start_time = time.time()
        message = self.get_argument('message')
        operation = self.get_argument('operation', 'scramble')
        gen_key = self.get_argument('gen_key', ':'.join(['default', '12345', '12345']))

        generator, gen_key = get_generator(gen_key)
        scrambler = MessageScrambler(message, generator, seed=True)
        original_message = scrambler.message
        if operation == 'scramble':
            out = scrambler.scramble()
        else:
            out = scrambler.un_scramble()

        def __round(num):
            working = str(num-int(num))
            for i, e in enumerate(working[2:]):
                if e != '0':
                    return int(num) + float(working[:i+4])

        ret = { 'scrambled': str(out),
                'original': str(original_message),
                'extra': {'gen_conf': gen_key,
                          'cheie': scrambler.key,
                          'durata': '%ss' % __round(time.time() - start_time)
                          }
                }
        self.write(ret)


class ScrambleImage(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        start_time = time.time()
        image_path = self.get_argument('image')
        operation = self.get_argument('operation', 'scramble')
        gen_key = self.get_argument('gen_key', ':'.join(['default', '12345', '12345']))

        image = Image.open('static/' + image_path)
        image = image.convert('RGB')

        generator, gen_key = get_generator(gen_key)
        scrambler = ImageScrambler(image=image, random=generator, seed=True)
        if operation == 'scramble':
            out_image = scrambler.build_image(scrambler.scramble())
        else:
            out_image = scrambler.build_image(scrambler.un_scramble())

        file_name = image_path.split('/')[-1]
        if '-a-' in file_name:
            file_name = file_name.split('-a-')[-1]
        file_name = '%s-a-%s' % (time.time(), file_name)
        paths = {'scramble': 'static/img/upload/scrambled/%s',
                'un_scramble': 'static/img/upload/unscrambled/%s' }

        save_path = paths.get(operation, 'un_scramble') % file_name
        out_image.save(save_path)

        full_url = save_path[7:]

        def __round(num):
            working = str(num-int(num))
            for i, e in enumerate(working[2:]):
                if e != '0':
                    return int(num) + float(working[:i+4])

        ret = { 'scrambled': full_url,
                'original': image_path,
                'extra': {'gen_conf': gen_key,
                          'durata': '%ss' % __round(time.time() - start_time)
                          }
                }
        self.write(ret)


class FileUpload(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        file_body = self.request.files['files[]'][0]['body']
        img = Image.open(StringIO.StringIO(file_body))
        file_name = '{}-a-{}'.format(time.time(),self.request.files['files[]'][0]['filename'] )
        path = 'static/img/upload/'
        img.save(path + file_name, img.format)

        full_url = 'img/upload/%s' % file_name

        ret = {'files': []}
        ret['files'].append(
                      {
                        "name": file_name,
                        "size": img.size,
                        "url": full_url,
                        "thumbnailUrl": full_url,
                        "deleteUrl": '',
                        "deleteType": "DELETE"
                      })
        self.write(ret)

