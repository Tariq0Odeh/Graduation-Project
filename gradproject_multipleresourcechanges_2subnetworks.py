# -*- coding: utf-8 -*-
"""GradProject_MultipleResourceChanges_2Subnetworks.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1SaWGxdyci1IDgMIzLihs27XLy1NS2W34
"""

import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import matplotlib.pyplot as plt
import numpy as np
import gym
from gym import wrappers
import pdb
import json
import random
import math

"""functions to plot the score after finishing"""

def plotLearning(scores, filename, x=None, window=5):
    N = len(scores)
    running_avg = np.empty(N)
    for t in range(N):
        running_avg[t] = np.mean(scores[max(0, t-window):(t+1)])
    if x is None:
        x = [i for i in range(N)]
    plt.ylabel('Score')
    plt.xlabel('Game')
    plt.plot(x, running_avg)
    plt.savefig(filename)

"""Classes and function related to **SUBNETWORKS**"""

N = 20  # Numbers of TTIs in DTI
capacity = 8
numOfSubnetworks = 2
space = 2

possibleTraffic = [x for x in range(5, 81, 5)]

w0 = 2
w1 = 3

class QosSimulation:
    def __init__(self, dict):
        self.dict = dict

class Subnetwork:
    def __init__(self, qosSimulation, q_thresh):
        self.x = np.array([])
        self.r = np.full((N,), 1)
        self.beta = 1
        self.qosSimulation = qosSimulation
        self.q = np.array([])
        self.q_thresh = q_thresh
        self.trafficList = np.array([])
        self.cumulativeX = 0.0
        self.cumulativeQoS = 0.0

def updateSubnetwork(subnetwork, traffic, resource, qos):
    if traffic is not None:
        subnetwork.x = traffic
        subnetwork.cumulativeX += np.sum(traffic)
    if resource is not None:
        subnetwork.r = resource
    if qos is not None:
        subnetwork.q = qos

def initializeSubnetworks(subnets):
    for sub in subnets:
        sub.trafficList = np.array([])
        minIndex, maxIndex = getRandomIndices(space)
        sub.x = getTraffic(sub, minIndex, maxIndex)
        getQoS(sub)
        calculateBeta(sub)
        sub.cumulativeX += np.sum(sub.x)

"""Functions related to **QOS and BETA**"""

def read_json(json_path):
    existing_data = {}
    try:
        with open(json_path, 'r') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {}
    finally:
        return existing_data

def initDict_VoIP(json_path, attribute):
    data = read_json(json_path)
    new_dict = {}
    if attribute == 'delay':
        for _, value in data.items():
            new_dict[(int(value['numUE']), int(value['numRbs']))] = (value['delay']['delay_mean'], value['delay']['delay_std'])
    elif attribute == 'loss':
        for _, value in data.items():
            new_dict[(int(value['numUE']), int(value['numRbs']))] = (value['loss']['loss_mean'], value['loss']['loss_std'])
    return new_dict

def sample_from_gaussian(mean, std_dev):
    return np.random.normal(mean, std_dev)

def calculateBeta(subnetwork):
    subnetwork.beta = np.sum((subnetwork.q >= subnetwork.q_thresh) * subnetwork.x) / np.sum(subnetwork.x)
    # subnetwork.cumulativeQoS += np.sum((subnetwork.q >= subnetwork.q_thresh) * subnetwork.x)
    # subnetwork.beta = subnetwork.cumulativeQoS / subnetwork.cumulativeX

def getQoS(subnetwork):
    qos = np.zeros(N)
    for i in range(N):
        mean, stdDeviation = subnetwork.qosSimulation.dict[(int(subnetwork.x[i]), subnetwork.r[0])]
        # sampledValue = sample_from_gaussian(mean, stdDeviation)
        qos[i] = mean
    updateSubnetwork(subnetwork, None, None, qos)

"""Functions related to **TRAFFIC**"""

def getTraffic(subnetwork, minIndex, maxIndex):
    newTraffic = np.array([])
    sublist = possibleTraffic[minIndex:maxIndex+1]
    newTraffic = np.random.choice(sublist, N, replace=True)

    subnetwork.trafficList = np.concatenate((subnetwork.trafficList, newTraffic))
    return newTraffic

def calculate_cdf(subnetwork):
    sorted_traffic_list = sorted(subnetwork.trafficList)
    cumulative_frequency = [np.sum(np.array(sorted_traffic_list) <= value) for value in possibleTraffic]
    cdf = np.array(cumulative_frequency) / len(subnetwork.trafficList)
    return cdf

def getRandomIndices(space):
    Idx = np.random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], size=1)[0]
    minIndex = max(0, Idx - space // 2)
    maxIndex = min(15, minIndex + space)

    if maxIndex - minIndex != space:
        minIndex = max(0, maxIndex - space)

    return minIndex, maxIndex

"""Functions related to **ACTION**"""

def mapAction(action):
    if action == 0:
        return -1, -1
    elif action == 1:
        return -1, 0
    elif action == 2:
        return 0, -1
    elif action == 3:
        return -1, 1
    elif action == 4:
        return 0, 0
    elif action == 5:
        return 1, -1

    elif action == 6:
        return 0, 1
    elif action == 7:
        return 1, 0
    elif action == 8:
        return 1, 1

"""Definition of the Neural Network - contains **DELTA** computation"""

class GenericNetwork(nn.Module):
    def __init__(self, alpha, input_dims, fc1_dims, fc2_dims, n_actions):
        super(GenericNetwork, self).__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.n_actions = n_actions
        self.fc1 = nn.Linear(*self.input_dims, self.fc1_dims)
        self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)
        self.fc3 = nn.Linear(self.fc2_dims, n_actions)
        self.optimizer = optim.Adam(self.parameters(), lr=alpha)

        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, observation):
        state = T.Tensor(observation).to(self.device)
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class ActorCriticNetwork(nn.Module):
    def __init__(self, alpha, input_dims, fc1_dims, fc2_dims, n_actions):
        super(ActorCriticNetwork, self).__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.n_actions = n_actions
        self.fc1 = nn.Linear(*self.input_dims, self.fc1_dims)
        self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)
        self.pi = nn.Linear(self.fc2_dims, n_actions)
        self.v = nn.Linear(self.fc2_dims, 1)
        self.optimizer = optim.Adam(self.parameters(), lr=alpha)

        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, observation):
        state = T.Tensor(observation).to(self.device)
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        pi = self.pi(x)
        v = self.v(x)
        return (pi, v)

class Agent(object):
    def __init__(self, alpha, beta, input_dims, gamma=0.99,
                 layer1_size=256, layer2_size=256, n_actions=2):
        self.gamma = gamma
        self.actor = GenericNetwork(alpha, input_dims, layer1_size,
                                    layer2_size, n_actions=n_actions)
        self.critic = GenericNetwork(beta, input_dims, layer1_size,
                                     layer2_size, n_actions=1)
        self.log_probs = None

    def choose_action(self, observation):
        observation_stacked = np.hstack(observation)
        observation_tensor = T.tensor(observation_stacked, dtype=T.float32).unsqueeze(0)

        probabilities = F.softmax(self.actor.forward(observation_tensor))

        action_probs = T.distributions.Categorical(probabilities)
        action = action_probs.sample()
        self.log_probs = action_probs.log_prob(action)

        return action.item()

    def learn(self, state, reward, new_state, done):
        self.actor.optimizer.zero_grad()
        self.critic.optimizer.zero_grad()

        new_state_stacked = np.hstack(new_state)
        new_state_tensor = T.tensor(new_state_stacked, dtype=T.float32).unsqueeze(0)

        state_stacked = np.hstack(state)
        state_tensor = T.tensor(state_stacked, dtype=T.float32).unsqueeze(0)

        critic_value_ = self.critic.forward(new_state_tensor)
        critic_value = self.critic.forward(state_tensor)
        reward = T.tensor(reward, dtype=T.float).to(self.actor.device)

        delta = -reward + self.gamma * critic_value_ * (1 - int(done)) - critic_value

        actor_loss = -self.log_probs * delta
        critic_loss = delta ** 2

        (actor_loss + critic_loss).backward()

        self.actor.optimizer.step()
        self.critic.optimizer.step()

        return actor_loss, critic_loss, reward, delta

"""Definition of the **ENVIRONMENT**"""

class Environment(gym.Env):
    def __init__(self):
        super(Environment, self).__init__()
        pass

    def reset(self):
        newObservation = np.array([])
        for i in range(numOfSubnetworks):
            newCDF = np.zeros(16)
            beta = 100
            newObservation = np.concatenate((newObservation, np.insert(newCDF, 0, beta)))

        return newObservation

    def step(self, action, subnetworks, episode):
        betas = np.zeros(numOfSubnetworks)
        resourcesArray = np.zeros(numOfSubnetworks)
        resourceSum = 0
        for i in range(numOfSubnetworks):
            newResource = subnetworks[i].r[0] + mapAction(action)[i]
            newResource = max(1, min(newResource, 8))
            resourcesArray[i] = newResource
            resourceR = np.full(N, newResource)
            updateSubnetwork(subnetworks[i], None, resourceR, None)

            getQoS(subnetworks[i])

            calculateBeta(subnetworks[i])
            betas[i] = subnetworks[i].beta

            resourceSum += newResource

        # reward = w0 * (resourceSum - capacity) / capacity + w1 * -resourceSum * subnetworks[0].beta
        avg_beta = np.mean(betas)
        # reward = w0 * (resourceSum - capacity) / capacity + w1/2 * -resourcesArray[0] * subnetworks[0].beta + w1/2 * -resourcesArray[1] * subnetworks[1].beta
        reward = w0 * (resourceSum - capacity) / capacity + w1/2 * subnetworks[0].beta + w1/2 * subnetworks[1].beta
        pdb.set_trace()

        newObservation = np.array([])
        for i in range(numOfSubnetworks):
            newCDF = calculate_cdf(subnetworks[i])
            beta = subnetworks[i].beta * 100
            newObservation = np.concatenate((newObservation, np.insert(newCDF, 0, beta)))

        return newObservation, reward

    def nextDTI(self, subnetworks):
        for i in range(numOfSubnetworks):
            minIndex, maxIndex = getRandomIndices(space)
            trafficX = getTraffic(subnetworks[i], minIndex, maxIndex)
            updateSubnetwork(subnetworks[i], trafficX, None, None)

"""**MAIN FUNCTION**"""

# Main function for RL
if __name__ == '__main__':
    agent = Agent(alpha=0.0001, beta=0.001, input_dims=[numOfSubnetworks * (16 + 1)], gamma=0.99,
                  n_actions=9, layer1_size=32, layer2_size=64)

    env = Environment()
    score_history = []
    score = 0
    num_episodes = 150

    voip_simulation_delay = QosSimulation(initDict_VoIP('VOIP_D30sec_results.json', 'delay'))
    voip_simulation_loss = QosSimulation(initDict_VoIP('VOIP_D30sec_results.json', 'loss'))
    subnetwork_loss = Subnetwork(voip_simulation_loss, 0.15)
    subnetwork_delay = Subnetwork(voip_simulation_delay, 0.4)
    subnetworks = [subnetwork_loss, subnetwork_delay]
    initializeSubnetworks(subnetworks)

    actor_loss_array = []
    critic_loss_array = []
    reward_array = []
    delta_array = []
    action_array = []
    delay_resources_array = []
    loss_resources_array = []

    for i in range(num_episodes):
        print('episode: ', i,'score: %.3f' % score)
        done = False
        score = 0
        observation = env.reset()
        initializeSubnetworks(subnetworks)

        cnt = 0
        while not done:
            cnt += 1
            if cnt == 100:
                done = 1
            lastAction = -2
            while True:
                action = agent.choose_action(observation)
                observation_, reward = env.step(action, subnetworks, i)

                actor_loss, critic_loss , reward, delta= agent.learn(observation, reward, observation_, done)

                action_array.append(mapAction(action))
                actor_loss_array.append(actor_loss.item())
                critic_loss_array.append(critic_loss.item())
                reward_array.append(reward)
                delta_array.append(delta.item())
                delay_resources_array.append(subnetworks[1].r[0])
                loss_resources_array.append(subnetworks[0].r[0])

                observation = observation_

                rbs = 0
                for k in range(numOfSubnetworks):
                    rbs += subnetworks[k].r[0]

                mappedAction = mapAction(action)
                if (rbs >= 8 and (mappedAction == (1, 1) or mappedAction == (0, 1) or mappedAction == (1, 0))) or (rbs <= 2 and (mappedAction == (-1, -1) or mappedAction == (0, -1) or mappedAction == (-1, 0))) or (mappedAction == (0,0) and lastAction == (0,0)):
                    env.nextDTI(subnetworks)
                    score += reward
                    break
                lastAction = mappedAction

        score_history.append(score)

    filename = 'results.png'
    plotLearning(score_history, filename=filename, window=10)

plt.plot(delay_resources_array)

plt.plot(loss_resources_array)

plt.plot(delta_array)