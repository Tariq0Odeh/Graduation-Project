import numpy as np
import pdb

# Define global variables
N = 20  # Numbers of TTIs in DTI
K = 2  # Different types of resources allocated to subnetwork
TTI = np.arange(1000)  # The transmission time interval
T = TTI[0::N]  # the set of starting points of all DTIs


# This class contains the qos dictionary for each subnetwork TYPE
# Keep in mind that multiple subnetworks can have the same type but different thresholds
class QosSimulation:
    def __init__(self, dict):
        self.dict = dict


# Used to initialize a subnetwork
class Subnetwork:
    def __init__(self, simu):
        self.x = 1  # TODO: Set initial traffic
        self.r = 0.1  # TODO: Set initial resources
        self.simu = simu
        self.q = 0.5  # We get this value from sampling the mean and standard deviation
        self.q_thresh = 0.5  # This value is set manually after observing the data from Simu5g


# def betaCalculation(subnetwork):
#     beta = np.sum((subnetwork.q <= qt) * subnetwork.x) / np.sum(subnetwork.x)
#     return beta


# this function represents the traffic given to a subnetwork. In training, it is random. In testing, we take traffic
# from Italia communication dataset
def getTraffic():
    return np.random.randint(1, 5)


# Using RL, the resources are changed (10% - 80%)
# TODO: This needs the state
def getResources():
    return np.random.randint(1, 8) * 0.1


# This function returns the qos sample by using the dictionary
# Each subnetwork type has its own dictionary
def getQoS(subnetwork):
    gaussianTuple = subnetwork.simu.dict[(subnetwork.x, subnetwork.r)]
    # TODO: Get sampled value
    sampledValue = 0.5
    updateSubnetwork(subnetwork, None, None, sampledValue)
    return sampledValue  # TODO: Return sampled value


# Function used to update a subnetwork attributes
def updateSubnetwork(subnetwork, traffic, resource, qos):
    if traffic is not None:
        subnetwork.x = traffic
    if resource is not None:
        subnetwork.r = resource
    if qos is not None:
        subnetwork.q = qos


# This is a temp function that creates a dictionary for the simulation
# Improve it to be read from a file
def initDict():
    new_dict = {}
    new_dict[(1, 0.1)] = (1, 1)
    new_dict[(1, 0.2)] = (1, 1)
    new_dict[(1, 0.3)] = (1, 1)
    new_dict[(1, 0.4)] = (1, 1)
    new_dict[(1, 0.5)] = (1, 1)
    new_dict[(1, 0.6)] = (1, 1)
    new_dict[(1, 0.7)] = (1, 1)
    new_dict[(1, 0.8)] = (1, 1)
    new_dict[(2, 0.1)] = (1, 1)
    new_dict[(2, 0.2)] = (1, 1)
    new_dict[(2, 0.3)] = (1, 1)
    new_dict[(2, 0.4)] = (1, 1)
    new_dict[(2, 0.5)] = (1, 1)
    new_dict[(2, 0.6)] = (1, 1)
    new_dict[(2, 0.7)] = (1, 1)
    new_dict[(2, 0.8)] = (1, 1)
    new_dict[(3, 0.1)] = (1, 1)
    new_dict[(3, 0.2)] = (1, 1)
    new_dict[(3, 0.3)] = (1, 1)
    new_dict[(3, 0.4)] = (1, 1)
    new_dict[(3, 0.5)] = (1, 1)
    new_dict[(3, 0.6)] = (1, 1)
    new_dict[(3, 0.7)] = (1, 1)
    new_dict[(3, 0.8)] = (1, 1)
    new_dict[(4, 0.1)] = (1, 1)
    new_dict[(4, 0.2)] = (1, 1)
    new_dict[(4, 0.3)] = (1, 1)
    new_dict[(4, 0.4)] = (1, 1)
    new_dict[(4, 0.5)] = (1, 1)
    new_dict[(4, 0.6)] = (1, 1)
    new_dict[(4, 0.7)] = (1, 1)
    new_dict[(4, 0.8)] = (1, 1)
    new_dict[(5, 0.1)] = (1, 1)
    new_dict[(5, 0.2)] = (1, 1)
    new_dict[(5, 0.3)] = (1, 1)
    new_dict[(5, 0.4)] = (1, 1)
    new_dict[(5, 0.5)] = (1, 1)
    new_dict[(5, 0.6)] = (1, 1)
    new_dict[(5, 0.7)] = (1, 1)
    new_dict[(5, 0.8)] = (1, 1)


if __name__ == '__main__':
    simulation1 = QosSimulation(initDict())
    subnetworks = [Subnetwork(simulation1)]
    for cnt in range(len(T) - 1):  # Every DTI
        # t = TTI[T[cnt]:(T[cnt + 1])]
        for subnetwork in subnetworks:
            # At the start of the DTI we receive how much resources are allocated
            resourceR = getResources()
            # We also find out how much traffic we got
            trafficX = getTraffic()
            # We update the subnetwork with the new traffic and resources
            updateSubnetwork(subnetwork, trafficX, resourceR, None)
            # Calculate Degradation Probability
            qos = getQoS(subnetwork)

        # pdb.set_trace()
