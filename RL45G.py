import numpy as np
import json
import random
# from ActorCriticNetwork import *
import pdb

# Define the traffic elements
# traffic_elements = [5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80]
traffic_elements = [5, 80]

# Numbers of TTIs in DTI
num_TTIs = 20

# Generate the random array
traffic_vector = np.random.choice(traffic_elements, size=num_TTIs)

W0 = 0.01
W1 = 1


# Compute the CDF of data at specific points
def compute_cdf(data, points):
    # Sort the data
    sorted_data = np.sort(data)

    # Compute the cumulative distribution values
    cdf_values = np.arange(1, len(sorted_data) + 1) / len(sorted_data)

    # Compute the CDF at the given points
    cdf_at_points = np.zeros_like(points, dtype=float)
    for i, point in enumerate(points):
        cdf_at_points[i] = np.searchsorted(sorted_data, point, side='right') / len(sorted_data)

    return cdf_at_points


# Read json file
def read_json(json_path):
    existing_data = {}
    try:
        with open(json_path, 'r') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {}
    finally:
        return existing_data


# Load network data from json file to dictionary--> will be used to map traffic to QoS
def VOIP_json_dict(json_path, attribute):
    data = read_json(json_path)
    new_dict = {}
    if attribute == 'delay':
        for _, value in data.items():
            new_dict[(int(value['numUE']), int(value['numRbs']))] = (
            value['delay']['delay_mean'], value['delay']['delay_std'])
    elif attribute == 'loss':
        for _, value in data.items():
            new_dict[(int(value['numUE']), int(value['numRbs']))] = (
            value['loss']['loss_mean'], value['loss']['loss_std'])
    return new_dict


# a function that takes an array of traffic and an RBs value, then retrieves the corresponding QoS from the QOS dictionary
def get_qos_values(data_dict, traffic_array, rbs_value):
    qos_values = []
    for traffic in traffic_array:
        key = (traffic, rbs_value)
        if key in data_dict:
            qos_value, _ = data_dict[key]
            qos_values.append(qos_value)
        else:
            raise KeyError(f"Key {key} not found in the dictionary.")
    return qos_values


# round array to specific value set
def round_to_set(array, value_set):
    value_set = np.array(value_set)  # Convert the value set to a NumPy array for vectorized operations
    rounded_array = np.zeros_like(array)  # Initialize an array to store the rounded values

    for i, value in enumerate(array):
        # Find the value in the set that is closest to the current value
        closest_value = value_set[np.argmin(np.abs(value_set - value))]
        rounded_array[i] = closest_value

    return rounded_array


# threshold qos
qos_threshold = 0.1

json_path = 'VOIP_D30sec_results.json'
Network_qos_VOIP_delay = VOIP_json_dict(json_path, attribute='delay')
Network_qos_VOIP_loss = VOIP_json_dict(json_path, attribute='loss')

# actor = ActorNetwork(0.01, input_dims=1, fc1_dims=10, fc2_dims=10,  n_actions=8)
# critic = CriticNetwork(0.005, input_dims=1, fc1_dims=10, fc2_dims=10, n_actions=1)

beta_list = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
CDF_list = [0, 0.2, 0.4, 0.6, 0.8, 1]

QTable = {}  # Action Table
ValueTable = {}
VisitTable = {}

for episode in range(100):

    # Create an empty traffic vector
    traffic_vector = np.array([])

    # Create an empty qos vector
    qos_vector = np.array([])

    for _ in range(200):
        # Generate random traffic for the length of DTI
        traffic_vector_DTI = np.random.choice(traffic_elements, size=num_TTIs)

        # Extend the traffic_vector using the traffic_vector_DTI
        traffic_vector = np.concatenate((traffic_vector, traffic_vector_DTI))

        # Compute te CDF of the traffic_vector at specific points listed in traffic_elements
        cdf_traffic_vector = compute_cdf(traffic_vector, traffic_elements)
        cdf_traffic_vector = round_to_set(cdf_traffic_vector, CDF_list)

        # beta = random.choice(beta_list) # TODO: Return here
        beta = np.sum(traffic_vector[qos_vector > qos_threshold]) / np.sum(traffic_vector)

        # print(f"beta={beta}, cdf_traffic_vector[0]={cdf_traffic_vector[0]}, cdf_traffic_vector[1]={cdf_traffic_vector[1]}")
        # Update the Q Table (Action Table)
        value_saved = 0
        rbs_saved = 0
        for rbs in range(1, 9):
            # Map Traffic to QoS
            qos_vector_DTI = get_qos_values(Network_qos_VOIP_loss, traffic_vector_DTI, rbs)

            # create a temporary qos_vector_temp to compute beta by concatinating the qos_vector and the qos_vector_DTI
            qos_vector_temp = np.concatenate((qos_vector, qos_vector_DTI))

            # pdb.set_trace()

            # Compute the degradation probability; beta=0 all traffic transmitted, beta=1 no data is transmitted
            beta_next_state = np.sum(traffic_vector[qos_vector_temp > qos_threshold]) / np.sum(traffic_vector)

            # Compute the reward function
            reward = W0 * ((rbs - 8) / 8) + W1 * (beta_next_state)

            if (round(beta_next_state, 1), cdf_traffic_vector[0]) not in ValueTable.keys():
                ValueTable[round(beta_next_state, 1), cdf_traffic_vector[0]] = 1000

            # new value
            value_temp = -1 * reward + ValueTable[round(beta_next_state, 1), cdf_traffic_vector[0]]

            # print(rbs,value_saved,value_temp,rbs_saved)

            if value_temp > value_saved:
                value_saved = value_temp
                rbs_saved = rbs

            # print(f"rbs={rbs},value_temp={value_temp}, reward={reward}, part1={(8-rbs)/8}, part2={beta_next_state} ===> rbs_saved={rbs_saved}, value_saved={value_saved}")

        # Map Traffic to QoS
        qos_vector_DTI = get_qos_values(Network_qos_VOIP_delay, traffic_vector_DTI, rbs_saved)

        # create a temporary qos_vector_temp to compute beta by concatinating the qos_vector and the qos_vector_DTI
        qos_vector = np.concatenate((qos_vector, qos_vector_DTI))

        ValueTable[beta, cdf_traffic_vector[0]] = value_saved
        QTable[beta, cdf_traffic_vector[0]] = rbs_saved

        if (beta, cdf_traffic_vector[0]) not in VisitTable.keys():
            VisitTable[beta, cdf_traffic_vector[0]] = 1
        else:
            VisitTable[beta, cdf_traffic_vector[0]] = VisitTable[beta, cdf_traffic_vector[0]] + 1

        # pdb.set_trace()

print(f"QTable = {QTable}")
print(f"ValueTable = {ValueTable}")
print(f"VisitTable = {VisitTable}")
print('---')
