import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import re

folder_path = 'D2min_VoIP'
json_path = 'results.json'


def readResults(csv_file, numOfUE):
    df = pd.read_csv(folder_path + "\\" + csv_file, dtype={6: str, 15: str, 16: str})
    data_delay = []
    data_loss = []
    data_jitter = []
    for i in range(1, int(numOfUE) + 1):
        ue = "MultiCell_Standalone.ue[" + str(i) + "].app[0]"
        filtered = df[(df['type'] == 'scalar') & (df['module'] == ue)]

        filtered_delay = filtered[(filtered['name'].str.contains('voIPPlayoutDelay'))]
        filtered_delay.loc[:, 'value'] = pd.to_numeric(filtered_delay['value'])
        data_delay.append(np.mean(filtered_delay.value))

        filtered_loss = filtered[(filtered['name'].str.contains('voIPPlayoutLoss'))]
        filtered_loss.loc[:, 'value'] = pd.to_numeric(filtered_loss['value'])
        data_loss.append(np.mean(filtered_loss.value))

        filtered_jitter = filtered[(filtered['name'].str.contains('voIPJitter'))]
        filtered_jitter.loc[:, 'value'] = pd.to_numeric(filtered_jitter['value'])
        data_jitter.append(np.mean(filtered_jitter.value))

    data_delay = [x for x in data_delay if x != 0 and not pd.isna(x)]
    data_loss = [x for x in data_loss if x != 0 and not pd.isna(x)]
    data_jitter = [x for x in data_jitter if x != 0 and not pd.isna(x)]

    delay_mean = np.mean(data_delay)
    delay_std = np.std(data_delay)
    delay_min = np.min(data_delay)
    delay_max = np.max(data_delay)

    loss_mean = np.mean(data_loss)
    loss_std = np.std(data_loss)
    loss_min = np.min(data_loss)
    loss_max = np.max(data_loss)

    jitter_mean = np.mean(data_jitter)
    jitter_std = np.std(data_jitter)
    jitter_min = np.min(data_jitter)
    jitter_max = np.max(data_jitter)

    return {"delay": {"delay_mean": delay_mean, "delay_std": delay_std, "delay_min": delay_min, "delay_max": delay_max},
            "loss": {"loss_mean": loss_mean, "loss_std": loss_std, "loss_min": loss_min, "loss_max": loss_max},
            "jitter": {"jitter_mean": jitter_mean, "jitter_std": jitter_std, "jitter_min": jitter_min,
                       "jitter_max": jitter_max}}


def plot_results(existing_data):
    plot_delay = {}
    plot_loss = {}
    plot_jitter = {}
    for key, value in existing_data.items():
        numUE = value['numUE']
        if numUE not in plot_delay.keys():
            plot_delay[numUE] = {"numRbs": [], "qos": [], "min": [], "max": []}
        plot_delay[numUE]['numRbs'].append(value['numRbs'])
        plot_delay[numUE]['qos'].append(value["delay"]["delay_mean"])
        plot_delay[numUE]['min'].append(value["delay"]["delay_min"])
        plot_delay[numUE]['max'].append(value["delay"]["delay_max"])

        if numUE not in plot_loss.keys():
            plot_loss[numUE] = {"numRbs": [], "qos": [], "min": [], "max": []}
        plot_loss[numUE]['numRbs'].append(value['numRbs'])
        plot_loss[numUE]['qos'].append(value["loss"]["loss_mean"])
        plot_loss[numUE]['min'].append(value["loss"]["loss_min"])
        plot_loss[numUE]['max'].append(value["loss"]["loss_max"])

        if numUE not in plot_jitter.keys():
            plot_jitter[numUE] = {"numRbs": [], "qos": [], "min": [], "max": []}
        plot_jitter[numUE]['numRbs'].append(value['numRbs'])
        plot_jitter[numUE]['qos'].append(value["jitter"]["jitter_mean"])
        plot_jitter[numUE]['min'].append(value["jitter"]["jitter_min"])
        plot_jitter[numUE]['max'].append(value["jitter"]["jitter_max"])

    plt.figure()
    for key in plot_delay.keys():
        plt.plot(plot_delay[key]['numRbs'], plot_delay[key]['qos'], label="x = " + key)
        plt.fill_between(plot_delay[key]['numRbs'], plot_delay[key]['min'], plot_delay[key]['max'], alpha=0.2)
    plt.title("VoIP Delay")
    plt.xlabel("numRbs")
    plt.ylabel("Delay")
    plt.legend()

    plt.figure()
    for key in plot_loss.keys():
        plt.plot(plot_loss[key]['numRbs'], plot_loss[key]['qos'], label="x = " + key)
        plt.fill_between(plot_loss[key]['numRbs'], plot_loss[key]['min'], plot_loss[key]['max'], alpha=0.2)
    plt.title("VoIP Loss")
    plt.xlabel("numRbs")
    plt.ylabel("Loss")
    plt.legend()

    plt.figure()
    for key in plot_jitter.keys():
        plt.plot(plot_jitter[key]['numRbs'], plot_jitter[key]['qos'], label="x = " + key)
        plt.fill_between(plot_jitter[key]['numRbs'], plot_jitter[key]['min'], plot_jitter[key]['max'], alpha=0.2)
    plt.title("VoIP Jitter")
    plt.xlabel("numRbs")
    plt.ylabel("Jitter")
    plt.legend()
    plt.show()  # Show all plots together at the end


def getParameters(file):
    match = re.match(r'D2min_(\w+)_numUE(\d+)_numRbs(\d+)\.csv', file)
    subnet = match.group(1)
    numUE = match.group(2)
    numRbs = match.group(3)
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
    csv_files = [file for file in files_list if file.endswith('.csv')]

    for file in csv_files:
        if file in existing_data.keys():
            continue
        processed = True
        print("Processing file: ", file)
        [subnet, numUE, numRbs] = getParameters(file)
        results = readResults(file, numUE)
        json_result = {"subnet": subnet, "numUE": numUE, "numRbs": numRbs, "delay": results["delay"],
                       "loss": results["loss"], "jitter": results["jitter"]}
        existing_data[file] = json_result

    if processed:
        with open(json_path, 'w') as f:
            json.dump(existing_data, f)
        print("Processing complete")
    else:
        print("Results are up to date")
    plot_results(existing_data)
