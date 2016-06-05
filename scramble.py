#scramble.py
from PIL import Image
import sys
import os
import random
from ranrot import RanrotBGenerator



class Scrambler(object):
    def __init__(self, random=random):
        self.random = random
    
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

    def scramble(self, out):
        while True:
            chunk = f.read(4)
            if chunk:
                for b in chunk:
                    yield b
            else:
                break
        

class MessageScrambler(Scrambler):
    def __init__(self, message=None, random=random):
        self.message = [ord(i) for i in message]
        self.random = random
        self.random.seed(hash(len(self.message)))
    
    def code(self, seq):
        for i in xrange(len(seq)):
            seq[i] = seq[i] ^ self.random.randint(0, 255)
        return seq
    
    def scramble(self):
        s = super(MessageScrambler, self).scramble(self.message)
        return ''.join([chr(i) for i in s])
    
    def un_scramble(self):
        s = super(MessageScrambler, self).un_scramble(self.message)
        return ''.join([chr(i) for i in s])


class ImageScrambler(Scrambler):
    def __init__(self, image=None, random=random):
        self.img = image
        self.random = random
        self.random.seed(hash(self.img.size))
        
    def get_pixels(self):
        w, h = self.img.size
        pxs = []
        for x in range(h):
            for y in range(w):
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
        for x in range(h):
            for y in range(w):
                out_img.putpixel((x, y), pxIter.next())
        return out_img


def main():
    if sys.argv[1] == 'image':
        img = Image.open(sys.argv[3])
        scr = ImageScrambler(img, random)
        if sys.argv[2] == "scramble":
            out_img = scr.build_image(scr.scramble())
            out_img.save("scrambled.png")
        elif sys.argv[2] == "unscramble":
            out_img = scr.build_image(scr.un_scramble())
            out_img.save("unscrambled.png")
        else:
            sys.exit("Unsupported operation: " + operation())

    if sys.argv[1] == 'message':
        msg = sys.argv[3]
        scr = MessageScrambler(msg, random)
        if sys.argv[2] == "scramble":
            out = scr.scramble()
            r = MessageScrambler(''.join(out), random).un_scramble()
        elif sys.argv[2] == "unscramble":
            out = scr.un_scramble()
            r = MessageScrambler(''.join(out), random).scramble()
        else:
            sys.exit("Unsupported operation: " + operation())
        print out
        print r

if __name__ == "__main__":
    import time
    st = time.time()
    if sys.argv[-1] == 'ranrot':
        random = RanrotBGenerator()
    main()
    print 'total time: %s' % (time.time() - st)