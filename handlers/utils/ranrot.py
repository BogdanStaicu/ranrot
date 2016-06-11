import ctypes
import time
import argparse

class RanrotBase(object):
    def _lrotl(self, x, r):
        left = (x << r) & self.MASK
        right = x >> (self.MASK_LENGTH-r)
        return left | right

    def shuffle(self, x, random=None, int=int):
        if random is None:
            random = self.random
        for i in reversed(xrange(1, len(x))):
            j = int(random() * (i+1))
            x[i], x[j] = x[j], x[i]

    def randint(self, min_value=0, max_value=100):
        interval = max_value - min_value
        if interval <= 0:
            # 'Invalid interval'
            return None

        x = int(interval * self.random())
        if x >= interval:
            x -= 1
        return min_value + x

    def jumpahead(self, num):
        for i in xrange(num):
            self.random()

    def random(self):
        raise NotImplementedError

    def getrandbits(self):
        raise NotImplementedError

    def seed(self, seed):
        raise NotImplementedError


class RanrotWGenerator(RanrotBase):
    KK = 17
    JJ = 10
    R1 = 19
    R2 =  27

    MASK = 0xFFFFFFFFFFFFFFFF
    MASK_LENGTH = MASK.bit_length()

    def __init__(self, seed=12345):
        self.p1 = self.p2 = 0
        self.rand_buffer = []
        for i in xrange(self.KK):
            self.rand_buffer.append([0,0])
        self.randbits = [0, 0]
        self.seed(seed)

    def getrandbits(self):
        z = ctypes.c_ulong(self._lrotl(self.rand_buffer[self.p1][0], self.R1) +
                           self.rand_buffer[self.p2][0]).value
        y = ctypes.c_ulong(self._lrotl(self.rand_buffer[self.p1][1], self.R2) +
                           self.rand_buffer[self.p2][1]).value

        self.rand_buffer[self.p1][0] = y
        self.rand_buffer[self.p1][1] = z

        self.p1 = self.p1 - 1 if self.p1 > 0 else self.KK -1
        self.p2 = self.p2 - 1 if self.p2 > 0 else self.KK -1

        self.randbits[0] = y
        self.randbits[1] = z
        return y

    def random(self):
        z = self.getrandbits()
        self.randbits[1] = ctypes.c_ulong((z & 0x000FFFFF) | 0x3FF00000).value
        x = self.randbits[0] + self.randbits[1]

        return float(x)*(1.0/self.MASK)

    def seed(self, seed):
        s = seed
        for i in xrange(self.KK):
            for j in xrange(2):
                s = ctypes.c_ulong(s *  2891336453 + 1).value
                self.rand_buffer[i][j] = s

        self.p1 = 0
        self.p2 = self.JJ

        for i in xrange(31):
            self.getrandbits()


class RanrotBGenerator(RanrotBase):
    KK = 17
    JJ = 10
    R1 = 13
    R2 = 9
    
    MASK = 0xFFFFFFFF
    MASK_LENGTH = MASK.bit_length()

    def __init__(self, seed=12345):
        self.p1 = self.p2 = 0
        self.rand_buffer = []
        self.rand_buffer_copy = []
        self.seed(seed)

    def test(self):
        if self.rand_buffer[self.p1] == self.rand_buffer_copy[0]:
            same = True
            for i in xrange(self.KK):
                if self.rand_buffer[i] != self.rand_buffer_copy[self.KK - self.p1 + i]:
                    same = False
                    break
            if same:
                return False
        return True

    def seed(self, seed):
        i = 0
        s = seed
        self.rand_buffer = []
        while i < self.KK:
            s = ctypes.c_uint(s *  2891336453 + 1).value 
            self.rand_buffer.append(int(s))
            i += 1
        
        self.p1 = 0
        self.p2 = self.JJ
        self.rand_buffer_copy = self.rand_buffer + self.rand_buffer

        for i in xrange(self.KK): 
            self.getrandbits()
         
    def getrandbits(self, k=32):
        x = 0
        a = self._lrotl(self.rand_buffer[self.p2], self.R1)
        b = self._lrotl(self.rand_buffer[self.p1], self.R2)

        x = self.rand_buffer[self.p1] = ctypes.c_uint(a+b).value

        self.p1 = self.p1 - 1 if self.p1 > 0 else self.KK -1
        self.p2 = self.p2 - 1 if self.p2 > 0 else self.KK -1

        if not self.test():
            if (self.p2 + self.KK - self.p1) % self.KK != self.JJ:
                print('Random number generator not initialized')
            else:
                print('Random number generator returned to initial state')
        
        return x
    
    def random(self):
        x = self.getrandbits()
        return float(x)*(1.0/self.MASK)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('generator', help='implementarea RanRot de folosit',
                        choices=['ranrotB', 'ranrotW'])
    parser.add_argument('--size', help='numarul de numere pseudoaleatoare generate',
                        default=2500000 )
    parser.add_argument('--seed', help='seed-ul folosit de generator',
                        default=12345)
    parser.add_argument('output', help='fisierul de iesire',
                        default='gentest.out')
    args = parser.parse_args()

    gens = {'ranrotB': RanrotBGenerator,
            'ranrotW': RanrotWGenerator}

    gen = gens[args.generator](int(args.seed))

    st = time.time()

    with open(args.output, 'w+') as f:
        i = j = 0
        while i < int(args.size):
            f.write('{0:08X}'.format(gen.getrandbits()))
            j += 1
            if j > 9:
                j = 0
                f.write('\n')
            i +=1
    print('Timp de executie: %s' % (time.time() - st))
