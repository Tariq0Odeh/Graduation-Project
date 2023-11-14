import numpy as np
import pdb


class Slice:
    def __init__(self, t, k):
        self.t = t
        self.x = np.random.randint(1, 10, len(t))
        self.r = np.random.random(k)*10
        self.q = np.random.random(len(t))*10


if __name__ == '__main__':

    N = 20  # Numbers of TTIs in DTI
    K = 2  # Different types of resources allocated to slice
    TTI = np.arange(1000)   # The transmission time interval
    T = TTI[0::N]   # the set of starting points of all DTIs
    qt = 8  # QoS minimum threshold

    for cnt in range(len(T)-1):
        t = TTI[T[cnt]:(T[cnt+1])]
        print(t)                #add here update function
        slices = Slice(t, K)
        print(slices.x)
        print(slices.r)
        print(slices.q)
        pdb.set_trace()

