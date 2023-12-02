import numpy as np
import pdb

# Define global variables
N = 20  # Numbers of TTIs in DTI
K = 2  # Different types of resources allocated to slice
TTI = np.arange(1000)   # The transmission time interval
T = TTI[0::N]   # the set of starting points of all DTIs
qt = 6  # QoS minimum threshold

# Used to initialize a slice
class Slice:
    def __init__(self, t):
        self.t = t
        self.x = np.random.randint(1, 10, len(t)) 
        self.r = np.random.random(K) * 10
        self.q = np.random.random(len(t)) * 10

def betaCalculation(slice):
    beta = np.sum((slice.q <= qt) * slice.x) / np.sum(slice.x)
    return beta

# this function should be changed to get the actual traffic X
# It represents getting the traffic from the forecast module
def getTraffic():
    return np.random.randint(1, 10, len(t))

# Use reinforcement learning to update the resounces
def getResources():
    beta = betaCalculation(slice) # calculate beta from previous results (q, x)
    return np.random.random(K) * 10

# Function used to update a slice attributes
def updateSlice(slice):
    slice.x = getTraffic()
    slice.r = getResources()
    slice.q = np.random.random(len(t)) * 10
    
if __name__ == '__main__':
    slice = None
    # slices creation
    for cnt in range(len(T) - 1):
        t = TTI[T[cnt]:(T[cnt + 1])]
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
    
# TODO: Verify what is the traffic in the first slice -> What it would be in the code
