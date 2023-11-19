import numpy as np
import pdb

# Define global variables
N = 20  # Numbers of TTIs in DTI
K = 2  # Different types of resources allocated to slice
TTI = np.arange(1000)   # The transmission time interval
T = TTI[0::N]   # the set of starting points of all DTIs
qt = 6  # QoS minimum threshold

class Slice:
    def __init__(self, t):
        self.t = t
        self.x = np.random.randint(1, 10, len(t))
        self.r = np.random.random(K)*10
        self.q = np.random.random(len(t))*10

def updateSlice(slice):
    beta = betaCalculation(slice) # calculate beta from previous results (q, x)
    
    slice.x = np.random.randint(1, 10, len(t)) # this is an input from outside
    # update based on beta and forecast traffic
    slice.r = np.random.random(K)*10
    slice.q = np.random.random(len(t))*10
    
def betaCalculation(slice):
    beta = np.sum((slice.q<=qt)*slice.x)/np.sum(slice.x)
    return beta

if __name__ == '__main__':
    slice = None
    # slices creation
    for cnt in range(len(T)-1):
        t = TTI[T[cnt]:(T[cnt+1])]
        print(t)    #add here update function
        if slice == None: # create slice
            slice = Slice(t)
        else: # update slice
            updateSlice(slice)
        print("x = ", slice.x)
        print("r = ", slice.r)
        print("q = ", slice.q)
        print("beta = ", betaCalculation(slice), "\n")

        # pdb.set_trace()
