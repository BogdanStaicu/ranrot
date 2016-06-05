import ctypes
import time


class RanrotBGenerator:
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

    def _lrotl(self, x, r):
        left = (x << r) & self.MASK
        right = x >> (self.MASK_LENGTH-r)
        return left | right

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

    def shuffle(self, x, random=None, int=int):
        """x, random=random.random -> shuffle list x in place; return None.

        Optional arg random is a 0-argument function returning a random
        float in [0.0, 1.0); by default, the standard random.random.
        """

        if random is None:
            random = self.random
        for i in reversed(xrange(1, len(x))):
            # pick an element in x[:i+1] with which to exchange x[i]
            j = int(random() * (i+1))
            x[i], x[j] = x[j], x[i]

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
            self.random()  
         
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

    def randint(self, min=0, max=100):
        interval = max - min
        if interval <= 0:
            print 'Invalid interval'
            return None
        
        x = int(interval * self.random())
        if x >= interval:
            x -= 1 
        return min + x

    def jumpahead(self, num):
        for i in xrange(num):
            self.random()

if __name__ == '__main__':
    a = RanrotBGenerator()
    st = time.time()
    
    with open('py_test.out', 'w+') as f:
        i = j = 0
        while i < 2500000:
            f.write('{0:08X}'.format(a.getrandbits()))
            j += 1
            if j > 9:
                j = 0
                f.write('\n')
            i +=1      
    print('Total time: %s' % (time.time() - st))
