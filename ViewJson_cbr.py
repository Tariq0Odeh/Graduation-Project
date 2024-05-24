import json
import matplotlib.pyplot as plt
from tabulate import tabulate
import csv
import os
import sys


def read_json(json_path):
    directory = os.path.dirname(json_path)

    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        sys.exit(1)

    if not os.path.isfile(json_path):
        print(f"File '{json_path}' does not exist.")
        sys.exit(1)

    try:
        with open(json_path, 'r') as f:
            existing_data1 = json.load(f)
    except FileNotFoundError:
        print(f"File '{json_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"File '{json_path}' is not a valid JSON file.")
        sys.exit(1)

    return existing_data1


def plot_specific_data(existing_data1, numUEsString):
    plot_delay = {}
    for key, value in existing_data1.items():
        if key == numUEsString:
            numUE = value['numUE']
            if numUE not in plot_delay.keys():
                plot_delay[numUE] = {"numRbs": [], "qos": [], "min": [], "max": []}
            plot_delay[numUE]['numRbs'].append(value['numRbs'])
            plot_delay[numUE]['qos'].append(value["delay"]["delay_mean"])
            plot_delay[numUE]['min'].append(value["delay"]["delay_min"])
            plot_delay[numUE]['max'].append(value["delay"]["delay_max"])

    plt.figure()
    for key in plot_delay.keys():
        sorted_indices = sorted(range(len(plot_delay[key]['numRbs'])), key=lambda k: plot_delay[key]['numRbs'][k])
        sorted_numRbs = [plot_delay[key]['numRbs'][i] for i in sorted_indices]
        sorted_qos = [plot_delay[key]['qos'][i] for i in sorted_indices]
        plt.plot(sorted_numRbs, sorted_qos, label="UEs = " + key)
        # plt.fill_between(plot_delay[key]['numRbs'], plot_delay[key]['min'], plot_delay[key]['max'], alpha=0.2)
    plt.title("VoIP Delay")
    plt.xlabel("numRbs")
    plt.ylabel("Delay")
    plt.xlim(0, 7)
    plt.grid(True)
    plt.legend()
    plt.show()


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

    plt.figure()
    for key in plot_delay.keys():
        sorted_indices = sorted(range(len(plot_delay[key]['numRbs'])), key=lambda k: plot_delay[key]['numRbs'][k])
        sorted_numRbs = [plot_delay[key]['numRbs'][i] for i in sorted_indices]
        sorted_qos = [plot_delay[key]['qos'][i] for i in sorted_indices]
        plt.plot(sorted_numRbs, sorted_qos, label="UEs = " + key)
        # plt.fill_between(plot_delay[key]['numRbs'], plot_delay[key]['min'], plot_delay[key]['max'], alpha=0.2)
    plt.title("VoIP Delay")
    plt.xlabel("numRbs")
    plt.ylabel("Delay")
    plt.xlim(0, 7)
    plt.grid(True)
    plt.legend()
    plt.show()


def print_to_table(data):
    headers = ["File", "Subnet", "Num UE", "Num RBs", "Delay (mean)", "Delay (std)", "Delay (min)", "Delay (max)"]

    table_data = []
    for file_name, record in data.items():
        table_row = [
            file_name,
            record["subnet"],
            record["numUE"],
            record["numRbs"],
            record["delay"]["delay_mean"],
            record["delay"]["delay_std"],
            record["delay"]["delay_min"],
            record["delay"]["delay_max"]
        ]
        table_data.append(table_row)

    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def write_json_to_csv(data, csv_file):
    sorted_data = sorted(data.items(), key=lambda x: int(x[1]["numUE"]))

    with open(csv_file, 'w', newline='') as csvfile:
        fieldnames = ["File", "Subnet", "Num UE", "Num RBs", "Delay (mean)", "Delay (std)", "Delay (min)",
                      "Delay (max)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for file_name, record in sorted_data:
            writer.writerow({
                "File": file_name,
                "Subnet": record["subnet"],
                "Num UE": record["numUE"],
                "Num RBs": record["numRbs"],
                "Delay (mean)": record["delay"]["delay_mean"],
                "Delay (std)": record["delay"]["delay_std"],
                "Delay (min)": record["delay"]["delay_min"],
                "Delay (max)": record["delay"]["delay_max"]
            })


if __name__ == '__main__':
    existing_data = read_json("/jsonFiles/VOIP_D30sec_results.json")
    # print_to_table(existing_data)
    plot_results(existing_data)
    # write_json_to_csv(existing_data, "voip_d30sec_results.csv")
