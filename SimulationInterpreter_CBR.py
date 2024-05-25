import json
import numpy as np
import pandas as pd
import os
import re

folder_path = '../OneDrive'
json_path = 'jsonFiles/cbr_d30sec_results.json'


def readResults(csv_file, numOfUE):
    df = pd.read_csv(folder_path + "/" + csv_file, dtype={6: str, 15: str, 16: str})
    data_delay = []
    for i in range(1, int(numOfUE) + 1):
        ue = "MultiCell_Standalone.ue[" + str(i) + "].app[0]"
        filtered = df[(df['type'] == 'scalar') & (df['module'] == ue)]

        filtered_delay = filtered[(filtered['name'].str.contains('cbrFrameDelay'))]
        filtered_delay.loc[:, 'value'] = pd.to_numeric(filtered_delay['value'])
        data_delay.append(np.mean(filtered_delay.value))

    data_delay = [x for x in data_delay if x != 0 and not pd.isna(x)]

    delay_mean = np.mean(data_delay)
    delay_std = np.std(data_delay)
    delay_min = np.min(data_delay)
    delay_max = np.max(data_delay)

    return {"delay": {"delay_mean": delay_mean, "delay_std": delay_std, "delay_min": delay_min, "delay_max": delay_max}}


def getParameters(file):
    match = re.match(r'D30sec_(\w+)_Rbs(\d+)_UEs(\d+)\.csv', file)
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
    csv_files = [file for file in files_list if 'CBR' in file and file.endswith('.csv')]

    for file in csv_files:
        if file in existing_data.keys():
            continue
        processed = True
        print("Processing file: ", file)
        [subnet, numUE, numRbs] = getParameters(file)
        results = readResults(file, numUE)
        json_result = {"subnet": subnet, "numUE": numUE, "numRbs": numRbs, "delay": results["delay"]}
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
