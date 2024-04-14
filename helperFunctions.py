import numpy as np
import pandas as pd


# csv_file = 'VoIPPlayoutDelay.csv'

# This function gets a sample value given the mean and standard deviation
def sample_from_gaussian(mean, std_dev):
    return np.random.normal(mean, std_dev)


# This is a temp function that creates a dictionary for the simulation
# Improve it to be read from a file
def initDict(csv_file):
    new_dict = {}
    df = pd.read_csv(csv_file)
    for index, row in df.iterrows():
        new_dict[(row[0], row[1])] = (row[2], row[3])
    return new_dict