import argparse

import time
from PIL import Image
import sys
import os
import random as randomMT
import string

from ranrot import RanrotBGenerator, RanrotWGenerator

PRINTABLE = string.printable[:-5]


class Scrambler(object):
    def __init__(self, random=randomMT):
        self.random = random
        self.key = []
    
    def code(self, seq):
        raise NotImplementedError
    
    def __scrambled_index(self, seq):
        idx = range(len(seq))
        self.random.shuffle(idx)
        return idx

    def scramble(self, seq):
        idx = self.__scrambled_index(seq)
        out = []
        for i in idx:
            out.append(seq[i])
        return self.code(out)
        
    def un_scramble(self, seq):
        idx = self.__scrambled_index(seq)
        seq = self.code(seq)
        out = range(len(seq))
        cur = 0
        for i in idx:
            out[i] = seq[cur]
            cur += 1
        return out


class MessageScrambler(Scrambler):
    def __init__(self, message=None, random=randomMT, seed=False):
        super(MessageScrambler, self).__init__(random=random)
        self.message = [PRINTABLE.index(i) for i in message if i in PRINTABLE]
        if not seed:
            self.random.seed(hash(len(self.message)))
    
    def code(self, seq):
        for i in xrange(len(seq)):
            rnd = self.random.randint(0, len(PRINTABLE))
            self.key.append(rnd)
            seq[i] = (seq[i] + rnd) % len(PRINTABLE)
        return seq
    
    def scramble(self):
        s = super(MessageScrambler, self).scramble(self.message)
        return unicode(''.join([PRINTABLE[i] for i in s]))

    def decode(self, seq):
        for i in xrange(len(seq)):
            rnd = self.random.randint(0, len(PRINTABLE))
            self.key.append(rnd)
            seq[i] = (seq[i] - rnd) % len(PRINTABLE)
        return seq

    def un_scramble(self):
        idx = self._Scrambler__scrambled_index(self.message)
        seq = self.decode(self.message)
        out = range(len(self.message))
        cur = 0
        for i in idx:
            out[i] = seq[cur]
            cur += 1
        return unicode(''.join([PRINTABLE[i] for i in out]))


class ImageScrambler(Scrambler):
    def __init__(self, image=None, random=randomMT, seed=False):
        self.img = image
        self.random = random
        if not seed:
            self.random.seed(hash(self.img.size))
        
    def get_pixels(self):
        w, h = self.img.size
        pxs = []
        for x in range(w):
            for y in range(h):
                pxs.append(self.img.getpixel((x, y)))
        return pxs
    
    def code(self, pxs):
        for px_i in xrange(len(pxs)):
            xored = tuple(i ^ self.random.randint(0, 255) for i in pxs[px_i])
            pxs[px_i] = xored
        return pxs

    def scramble(self):
        pxs = self.get_pixels()
        return super(ImageScrambler, self).scramble(pxs)

    def un_scramble(self):
        pxs = self.get_pixels()
        return super(ImageScrambler, self).un_scramble(pxs)

    def build_image(self, pxs):
        out_img = Image.new("RGB", self.img.size)
        w, h = self.img.size
        pxIter = iter(pxs)
        for x in range(w):
            for y in range(h):
                out_img.putpixel((x, y), pxIter.next())
        return out_img


PRNGS_MAP = {
    'default': randomMT,
    'ranrotB': RanrotBGenerator(),
    'ranrotW': RanrotWGenerator(),
}

def get_generator(gen_conf, size=12345):
    try:
        key_parts = gen_conf.split(':')
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
        gen_conf = 'default:' + str(hash(size)) + ':' + str(size)

    return ret, gen_conf


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('type', help='tipul de date de criptat',
                        choices=['message', 'image'])
    parser.add_argument('operation', help='actiunea dorita',
                        choices=['scramble', 'unscramble'])
    parser.add_argument('genconf', help='cheia de configurare a generatorului: '
                                        '"<generator>:<seed>:<sequence number>"')
    parser.add_argument('payload', help='mesajul sau numele imaginii '
                                        'care va fi criptata/decriptata')
    args = parser.parse_args()

    start_time = time.time()
    generator, _ = get_generator(args.genconf)

    if args.type == 'message':
        scrambler = MessageScrambler(message=args.payload, random=generator, seed=True)
        text = '{} mesaj:\n\tMesaj original: {}\n\tMesaj {}: {}\n\tTimp de executie: {}s\n'
        if args.operation == 'scramble':
            result = scrambler.scramble()
            print(text.format('Criptare', args.payload, 'criptat', result, time.time() - start_time))
        else:
            result = scrambler.un_scramble()
            print(text.format('Decriptare', args.payload, 'decriptat', result, time.time() - start_time))
    elif args.type == 'image':
        image = Image.open(args.payload)
        scrambler = ImageScrambler(image=image, random=generator, seed=True)
        if args.operation == 'scramble':
            out_image = scrambler.build_image(scrambler.scramble())
            out_filename = 'scrambled.jpg'
        else:
            out_image = scrambler.build_image(scrambler.un_scramble())
            out_filename = 'restored.jpg'
        out_image.save(out_filename)
        print('Imaginea procesata a fost salvata in fisierul {}\n'
              'Timp de executie: {}s\n'.format(out_filename, time.time()-start_time))
