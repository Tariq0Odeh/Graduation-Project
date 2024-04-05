# this function was added just for testing the CDF code
import numpy as np
import random
import matplotlib.pyplot as plt

N = 20
listOfUsers = [5, 10, 15, 20]

cumulativeX = []

def getTraffic():
    newTraffic = []
    for i in range(N):
        newTraffic.append(random.choice(listOfUsers))
        # print(newTraffic[-1])
    cumulativeX.append(newTraffic)
    return newTraffic


def predictTraffic():
    predicted = np.zeros((N, len(listOfUsers)))  # 2d array, cols = N (TTIs), rows = len(listofusers)
    for i in range(N):  # for every TTI
        data = np.zeros(len(cumulativeX))
        for j in range(len(cumulativeX)):
            data[j] = cumulativeX[j][i]

        count, bins_count = np.histogram(data, bins=[0, 5, 10, 15, 20])
        pdf = count / sum(count)
        cdf = np.cumsum(pdf)
        predicted[i] = cdf
    print(predicted)
    plt.plot(bins_count[1:], cdf, label="CDF")
    plt.legend()
    plt.xticks([0, 5, 10, 15, 20])
    plt.show()
    pass


for i in range(10):
    getTraffic()
predictTraffic()
getTraffic()
predictTraffic()
getTraffic()
predictTraffic()