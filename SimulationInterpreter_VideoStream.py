import json
import pdb

import numpy as np
import pandas as pd
import os
import re

folder_path = 'videoStream'
json_path = 'jsonFiles/videoStream_d90sec_results.json'


def readResults(csv_file, numOfUE):
    df = pd.read_csv(folder_path + "\\" + csv_file, dtype={6: str, 15: str, 16: str})
    data_delay = []
    data_loss = []
    for i in range(1, int(numOfUE) + 1):
        ue = "UrbanNetwork.ue[" + str(i) + "].app[1]"
        filtered = df[(df['type'] == 'scalar') & (df['module'] == ue)]

        filtered_delay = filtered[(filtered['name'].str.contains('rtVideoStreamingEnd2endDelaySegment'))]  # TODO: Edit Attribute
        filtered_delay.loc[:, 'value'] = pd.to_numeric(filtered_delay['value'])
        data_delay.append(np.mean(filtered_delay.value))

        filtered_loss = filtered[(filtered['name'].str.contains('rtVideoStreamingSegmentLoss'))]  # TODO: Edit Attribute
        filtered_loss.loc[:, 'value'] = pd.to_numeric(filtered_loss['value'])
        data_loss.append(np.mean(filtered_loss.value))

    data_delay = [x for x in data_delay if x != 0 and not pd.isna(x)]
    data_loss = [x for x in data_loss if x != 0 and not pd.isna(x)]

    delay_mean = np.mean(data_delay)
    delay_std = np.std(data_delay)
    delay_min = np.min(data_delay)
    delay_max = np.max(data_delay)

    loss_mean = np.mean(data_loss)
    loss_std = np.std(data_loss)
    loss_min = np.min(data_loss)
    loss_max = np.max(data_loss)

    return {"delay": {"delay_mean": delay_mean, "delay_std": delay_std, "delay_min": delay_min, "delay_max": delay_max},
            "loss": {"loss_mean": loss_mean, "loss_std": loss_std, "loss_min": loss_min, "loss_max": loss_max}}


def getParameters(file):
    match = re.match(r'D90sec_(\w+)_Rbs(\d+)_UEs(\d+)\.csv', file)
    subnet = match.group(1)
    numRbs = match.group(2)
    numUE = match.group(3)
    return [subnet, numUE, numRbs]


def read_json():
    existing_data = {}
    try:
        with open(json_path, 'r') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {}
    finally:
        return existing_data


if __name__ == '__main__':
    existing_data = read_json()
    processed = False

    files_list = os.listdir(folder_path)
    csv_files = [file for file in files_list if 'VideoStream' in file and file.endswith('.csv')]

    for file in csv_files:
        if file in existing_data.keys():
            continue
        processed = True
        print("Processing file: ", file)
        [subnet, numUE, numRbs] = getParameters(file)
        results = readResults(file, numUE)
        json_result = {"subnet": subnet, "numUE": numUE, "numRbs": numRbs, "delay": results["delay"],
                       "loss": results["loss"]}
        existing_data[file] = json_result

    if processed:
        directory = os.path.dirname(json_path)

        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(json_path, 'w') as f:
            json.dump(existing_data, f)
        print("Processing complete")
    else:
        print("Results are up to date")
