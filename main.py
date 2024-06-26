import numpy as np
import random
import pdb

from helperFunctions import initDict, sample_from_gaussian

# Define global variables
N = 20  # Numbers of TTIs in DTI
K = 1  # Different types of resources allocated to subnetwork
TTI = np.arange(1000)  # The transmission time interval
T = TTI[0::N]  # the set of starting points of all DTIs
trainingFlag = "training"

listOfUsers = [5, 10, 15, 20]
resources = [1, 2, 3]


# This class contains the qos dictionary for each subnetwork TYPE
# Keep in mind that multiple subnetworks can have the same type but different thresholds
class QosSimulation:
    def __init__(self, dict):
        self.dict = dict


# Used to initialize a subnetwork
class Subnetwork:
    def __init__(self, qosSimulation):
        self.x = np.full((N,), listOfUsers[0])
        self.r = np.full((N,), resources[0])
        self.beta = 1
        self.qosSimulation = qosSimulation
        self.q = np.zeros(N)  # We get this value from sampling the mean and standard deviation
        self.q_thresh = 0.007  # This value is set manually after observing the data from Simu5g
        self.cumulativeX = [np.full((N,), listOfUsers[0])]  # Store all traffic from the start


def calculateBeta(subnetwork):
    subnetwork.beta = np.sum((subnetwork.q <= subnetwork.q_thresh) * subnetwork.x) / np.sum(subnetwork.x)


# this function represents the traffic given to a subnetwork. In training, it is random. In testing, we take traffic
# from Italia communication dataset
def getTraffic(subnetwork):
    newTraffic = []
    if trainingFlag == "training":
        for i in range(N):
            newTraffic.append(random.choice(listOfUsers))
    else:
        for i in range(N):
            newTraffic.append(0)  # TODO: Return the traffic from the dataset
    subnetwork.cumulativeX.append(newTraffic)
    return newTraffic


# TODO: Implement CDF
def generate_cdf(subnetwork):
    newCDF = np.zeros((N, len(listOfUsers)))  # 2d array, cols = N (TTIs), rows = len(listofusers)
    for i in range(N):  # for every TTI
        data = np.zeros(len(subnetwork.cumulativeX))
        for j in range(len(subnetwork.cumulativeX)):
            data[j] = subnetwork.cumulativeX[j][i]
        count, bins_count = np.histogram(data, bins=[0, 5, 10, 15, 20])
        pdf = count / sum(count)
        cdf = np.cumsum(pdf)
        newCDF[i] = cdf
    return newCDF


# Using RL, the resources are changed (10% - 80%)
# This needs the state
# TODO: Add RL Work here
def getResources():
    newResources = []
    for i in range(N):
        newResources.append(random.choice(resources))
    return newResources

# This function returns the qos sample by using the dictionary
# Each subnetwork type has its own dictionary
# TODO: Make it work for more than one resource
def getQoS(subnetwork):
    qos = np.zeros(N)
    for i in range(N):
        gaussianTuple = subnetwork.qosSimulation.dict[(subnetwork.x[i], subnetwork.r[0])]  # value, value
        sampledValue = sample_from_gaussian(gaussianTuple[0], gaussianTuple[1])
        qos[i] = sampledValue
    updateSubnetwork(subnetwork, None, None, qos)


# Function used to update a subnetwork attributes
def updateSubnetwork(subnetwork, traffic, resource, qos):
    if traffic is not None:
        subnetwork.x = traffic
    if resource is not None:
        subnetwork.r = resource
    if qos is not None:
        subnetwork.q = qos


def initialize(subnetworksIn):
    for subn in subnetworksIn:
        getQoS(subn)
        calculateBeta(subn)


if __name__ == '__main__':
    voip_simulation = QosSimulation(initDict('VoIPPlayoutDelay.csv'))
    subnetworks = [Subnetwork(voip_simulation)]
    initialize(subnetworks)
    for cnt in range(len(T) - 1):  # Every DTI
        for subnetwork in subnetworks:
            # Start at the RL
            # At the start of the DTI we receive how much resources are allocated
            # TODO: This should be centralized
            resourceR = getResources()
            # Start of the network model
            # We also find out how much traffic we got
            trafficX = getTraffic(subnetwork)
            # We update the subnetwork with the new traffic and resources
            updateSubnetwork(subnetwork, trafficX, resourceR, None)
            # Calculate Degradation Probability
            getQoS(subnetwork)
            # Calculate Beta
            calculateBeta(subnetwork)
            print(cnt + 1)
            print("Traffic: ", subnetwork.x, "\nResources: ", subnetwork.r, "\nQOS: ", subnetwork.q, "\nBETA: ", subnetwork.beta)

# pdb.set_trace()
