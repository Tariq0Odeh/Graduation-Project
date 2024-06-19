import json
import matplotlib.pyplot as plt
from tabulate import tabulate
import csv
import matplotlib.cm as cm
import numpy as np


def read_json(json_path):
    existing_data = {}
    try:
        with open(json_path, 'r') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {}
    finally:
        return existing_data


def plot_results(existing_data):
    plot_delay = {}

    for key, value in existing_data.items():
        numUE = value['numUE']
        if numUE not in plot_delay.keys():
            plot_delay[numUE] = {"numRbs": [], "qos": [], "min": [], "max": []}
        plot_delay[numUE]['numRbs'].append(value['numRbs'])
        plot_delay[numUE]['qos'].append(value["delay"]["delay_mean"])
        plot_delay[numUE]['min'].append(value["delay"]["delay_min"])
        plot_delay[numUE]['max'].append(value["delay"]["delay_max"])

    ue_keys = sorted(plot_delay.keys(), key=int)
    colors = plt.get_cmap('tab20', len(ue_keys))

    plt.figure()
    for i, key in enumerate(ue_keys):
        sorted_indices = sorted(range(len(plot_delay[key]['numRbs'])), key=lambda k: plot_delay[key]['numRbs'][k])
        sorted_numRbs = [plot_delay[key]['numRbs'][i] for i in sorted_indices]
        sorted_qos = [plot_delay[key]['qos'][i] for i in sorted_indices]
        plt.plot(sorted_numRbs, sorted_qos, label="UEs = " + str(key), color=colors(i))
    plt.title("CBR Delay")
    plt.xlabel("numRbs")
    plt.ylabel("Delay")
    plt.xlim(0, 7)
    plt.grid(True)
    plt.legend()

    plt.xlim(0, 7)
    plt.grid(True)
    plt.show()  # Show all plots together at the end

if __name__ == '__main__':
    existing_data = read_json("CBR_D30sec_results.json")
    plot_results(existing_data)
