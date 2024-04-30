import json
import matplotlib.pyplot as plt
from tabulate import tabulate
import csv


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

    plt.figure()
    for key in plot_loss.keys():
        sorted_indices = sorted(range(len(plot_loss[key]['numRbs'])), key=lambda k: plot_loss[key]['numRbs'][k])
        sorted_numRbs = [plot_loss[key]['numRbs'][i] for i in sorted_indices]
        sorted_qos = [plot_loss[key]['qos'][i] for i in sorted_indices]
        plt.plot(sorted_numRbs, sorted_qos, label="UEs = " + key)
        # plt.fill_between(plot_loss[key]['numRbs'], plot_loss[key]['min'], plot_loss[key]['max'], alpha=0.2)
    plt.title("VoIP Loss")
    plt.xlabel("numRbs")
    plt.ylabel("Loss")
    plt.xlim(0, 7)
    plt.grid(True)
    plt.legend()

    plt.figure()
    for key in plot_jitter.keys():
        sorted_indices = sorted(range(len(plot_jitter[key]['numRbs'])), key=lambda k: plot_jitter[key]['numRbs'][k])
        sorted_numRbs = [plot_jitter[key]['numRbs'][i] for i in sorted_indices]
        sorted_qos = [plot_jitter[key]['qos'][i] for i in sorted_indices]
        plt.plot(sorted_numRbs, sorted_qos, label="UEs = " + key)
        # plt.fill_between(plot_jitter[key]['numRbs'], plot_jitter[key]['min'], plot_jitter[key]['max'], alpha=0.2)
    plt.title("VoIP Jitter")
    plt.xlabel("numRbs")
    plt.ylabel("Jitter")
    plt.legend()
    plt.xlim(0, 7)
    plt.grid(True)
    plt.show()  # Show all plots together at the end


def print_to_table(data):
    headers = ["File", "Subnet", "Num UE", "Num RBs", "Delay (mean)", "Delay (std)", "Delay (min)", "Delay (max)",
               "Loss (mean)", "Loss (std)", "Loss (min)", "Loss (max)", "Jitter (mean)", "Jitter (std)",
               "Jitter (min)", "Jitter (max)"]

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
            record["delay"]["delay_max"],
            record["loss"]["loss_mean"],
            record["loss"]["loss_std"],
            record["loss"]["loss_min"],
            record["loss"]["loss_max"],
            record["jitter"]["jitter_mean"],
            record["jitter"]["jitter_std"],
            record["jitter"]["jitter_min"],
            record["jitter"]["jitter_max"]
        ]
        table_data.append(table_row)

    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def write_json_to_csv(data, csv_file):
    # Sort the data based on "Num UE"
    sorted_data = sorted(data.items(), key=lambda x: int(x[1]["numUE"]))

    with open(csv_file, 'w', newline='') as csvfile:
        fieldnames = ["File", "Subnet", "Num UE", "Num RBs", "Delay (mean)", "Delay (std)", "Delay (min)",
                      "Delay (max)",
                      "Loss (mean)", "Loss (std)", "Loss (min)", "Loss (max)", "Jitter (mean)", "Jitter (std)",
                      "Jitter (min)", "Jitter (max)"]
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
                "Delay (max)": record["delay"]["delay_max"],
                "Loss (mean)": record["loss"]["loss_mean"],
                "Loss (std)": record["loss"]["loss_std"],
                "Loss (min)": record["loss"]["loss_min"],
                "Loss (max)": record["loss"]["loss_max"],
                "Jitter (mean)": record["jitter"]["jitter_mean"],
                "Jitter (std)": record["jitter"]["jitter_std"],
                "Jitter (min)": record["jitter"]["jitter_min"],
                "Jitter (max)": record["jitter"]["jitter_max"]
            })


if __name__ == '__main__':
    existing_data = read_json("VOIP_D30sec_results.json")
    # print_to_table(existing_data)
    plot_results(existing_data)
    # write_json_to_csv(existing_data, "voip_d30sec_results.csv")
