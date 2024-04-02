import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

attribute = 'voIPPlayoutDelay'
# attribute = 'voIPPlayoutLoss'
# attribute = 'voIPJitter'


rbs = [1, 2, 3]


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
    qos_mean = np.mean(means)
    qos_variance = np.var(means)
    no_zeros = [x for x in means if x != 0]
    minVal = min(no_zeros)
    maxVal = max(means)
    return [qos_mean, minVal, maxVal, qos_variance]


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
    print("[", str(numUE), ", Rb1]: mean = ", rets1[0], ", variance = ", rets1[3])
    print("[", str(numUE), ", Rb2]: mean = ", rets2[0], ", variance = ", rets2[3])
    print("[", str(numUE), ", Rb3]: mean = ", rets3[0], ", variance = ", rets3[3])
    pass


if __name__ == '__main__':
    files_20 = ["VoIP_numUE20_numRbs1.csv", "VoIP_numUE20_numRbs2.csv", "VoIP_numUE20_numRbs3.csv"]
    plot_line(20, files_20, 'blue')

    files_15 = ["VoIP_numUE15_numRbs1.csv", "VoIP_numUE15_numRbs2.csv", "VoIP_numUE15_numRbs3.csv"]
    plot_line(15, files_15, 'red')

    files_10 = ["VoIP_numUE10_numRbs1.csv", "VoIP_numUE10_numRbs2.csv", "VoIP_numUE10_numRbs3.csv"]
    plot_line(10, files_10, 'green')

    plt.xticks(rbs)
    plt.xlabel("Number of Rbs")
    plt.ylabel(attribute)
    plt.xlim(rbs[0], rbs[-1])
    plt.grid(True)
    plt.legend()
    plt.show()
