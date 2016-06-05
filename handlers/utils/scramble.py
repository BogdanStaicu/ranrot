#scramble.py
from PIL import Image
import sys
import os
import random
import string

PRINTABLE = string.printable[:-5]


class Scrambler(object):
    def __init__(self, random=random):
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


class FileScrambler(Scrambler):
    def __init__(self, file=None, random=random):
        self.file = file
        self.random = random
        self.random.seed(hash(self.get_file_size()))
        
    def get_file_size(self):
        old_file_position = self.file.tell()
        self.file.seek(0, os.SEEK_END)
        size = self.file.tell()
        self.file.seek(old_file_position, os.SEEK_SET)
        return size


class MessageScrambler(Scrambler):
    def __init__(self, message=None, random=random, seed=False):
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

    def un_scramble(self):
        idx = self._Scrambler__scrambled_index(self.message)
        seq = self.decode(self.message)
        out = range(len(self.message))
        cur = 0
        for i in idx:
            out[i] = self.message[cur]
            cur += 1
        return unicode(''.join([PRINTABLE[i] for i in out]))


class ImageScrambler(Scrambler):
    def __init__(self, image=None, random=random, seed=False):
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
