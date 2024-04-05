import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import csv

attribute = 'voIPPlayoutDelay'
# attribute = 'voIPPlayoutLoss'
# attribute = 'voIPJitter'


rbs = [1, 2, 3]

write_csv_filename = 'VoIPPlayoutDelay.csv'
results = []


def readCSV(csv_file, numUE):
    df = pd.read_csv(csv_file)
    means = []
    for i in range(numUE):
        j = i + 1
        ue = "MultiCell_Standalone.ue[" + str(j) + "].app[0]"
        filtered = df[(df['type'] == 'scalar') & (df['module'] == ue)]
        filtered = filtered[(filtered['name'].str.contains(attribute))]
        filtered['value'] = pd.to_numeric(filtered['value'])
        means.append(np.mean(filtered.value))
    means = [0 if math.isnan(x) else x for x in means]

    no_zeros = [x for x in means if x != 0]
    qos_mean = np.mean(no_zeros)
    qos_variance = np.var(no_zeros)
    minVal = min(no_zeros)
    maxVal = max(means)
    return [qos_mean, minVal, maxVal, qos_variance]


def write_csv():
    with open(write_csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        for row in results:
            writer.writerow(row)
    print("Results were written successfully")


def plot_line(numUE, files, color):
    csv_file = files[0]
    rets1 = readCSV(csv_file, numUE)
    csv_file = files[1]
    rets2 = readCSV(csv_file, numUE)
    csv_file = files[2]
    rets3 = readCSV(csv_file, numUE)
    qos = [rets1[0], rets2[0], rets3[0]]
    mins = [rets1[1], rets2[1], rets3[1]]
    maxs = [rets1[2], rets2[2], rets3[2]]
    plt.plot(rbs, qos, color=color, label="x = " + str(numUE))
    plt.fill_between(rbs, mins, maxs)

    res1 = [numUE, 1, rets1[0], rets1[3]]
    results.append(res1)
    res2 = [numUE, 2, rets2[0], rets2[3]]
    results.append(res2)
    res3 = [numUE, 3, rets3[0], rets3[3]]
    results.append(res3)
    print("[", str(numUE), ", Rb1]: mean = ", rets1[0], ", variance = ", rets1[3])
    print("[", str(numUE), ", Rb2]: mean = ", rets2[0], ", variance = ", rets2[3])
    print("[", str(numUE), ", Rb3]: mean = ", rets3[0], ", variance = ", rets3[3])


if __name__ == '__main__':
    files_20 = ["VoIP_numUE20_numRbs1.csv", "VoIP_numUE20_numRbs2.csv", "VoIP_numUE20_numRbs3.csv"]
    plot_line(20, files_20, 'blue')

    files_15 = ["VoIP_numUE15_numRbs1.csv", "VoIP_numUE15_numRbs2.csv", "VoIP_numUE15_numRbs3.csv"]
    plot_line(15, files_15, 'red')

    files_10 = ["VoIP_numUE10_numRbs1.csv", "VoIP_numUE10_numRbs2.csv", "VoIP_numUE10_numRbs3.csv"]
    plot_line(10, files_10, 'green')

    files_5 = ["VoIP_numUE5_numRbs1.csv", "VoIP_numUE5_numRbs2.csv", "VoIP_numUE5_numRbs3.csv"]
    plot_line(5, files_5, 'black')

    files_30 = ["VoIP_numUE30_numRbs1.csv", "VoIP_numUE30_numRbs1.csv", "VoIP_numUE30_numRbs3.csv"]
    plot_line(30, files_30, 'purple')

    write_csv()

    plt.xticks(rbs)
    plt.xlabel("Number of Rbs")
    plt.ylabel(attribute)
    plt.xlim(rbs[0], rbs[-1])
    plt.grid(True)
    plt.legend()
    plt.show()
