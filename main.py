import numpy as np
import pdb

# Define global variables
N = 20  # Numbers of TTIs in DTI
K = 2  # Different types of resources allocated to subnetwork
TTI = np.arange(1000)   # The transmission time interval
T = TTI[0::N]   # the set of starting points of all DTIs
qt = 6  # QoS minimum threshold

# Used to initialize a subnetwork
class Subnetwork:
    def __init__(self, t):
        self.t = t
        self.x = np.random.randint(1, 10, len(t)) 
        self.r = np.random.random(K) * 10
        self.q = np.random.random(len(t)) * 10

def betaCalculation(subnetwork):
    beta = np.sum((subnetwork.q <= qt) * subnetwork.x) / np.sum(subnetwork.x)
    return beta

# this function should be changed to get the actual traffic X
# It represents getting the traffic from the forecast module
def getTraffic():
    return np.random.randint(1, 10, len(t))

# Use reinforcement learning to update the resounces
def getResources():
    beta = betaCalculation(subnetwork) # calculate beta from previous results (q, x)
    return np.random.random(K) * 10

# Function used to update a subnetwork attributes
def updateSubnetwork(subnetwork):
    subnetwork.x = getTraffic()
    subnetwork.r = getResources()
    subnetwork.q = np.random.random(len(t)) * 10
    
if __name__ == '__main__':
    subnetwork = None
    # subnetworks creation
    for cnt in range(len(T) - 1):
        t = TTI[T[cnt]:(T[cnt + 1])]
        print(t)    #add here update function
        if subnetwork == None: # create subnetwork
            subnetwork = Subnetwork(t)
        else: # update subnetwork
            updateSubnetwork(subnetwork)
        print("x = ", subnetwork.x)
        print("r = ", subnetwork.r)
        print("q = ", subnetwork.q)
        print("beta = ", betaCalculation(subnetwork), "\n")

        # pdb.set_trace()
