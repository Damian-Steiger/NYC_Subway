import os, csv
import matplotlib.pyplot as plt

def init_stuff():
    global path
    global files
    global d

    path = os.getcwd()
    files = os.listdir(path)
    files.sort()
    d = dict()

def read_stuff():
    for fn in files:
        if fn.endswith(".csv"):
            with open (fn, 'r') as f:
                csv_r = csv.reader(f)
                for row in csv_r:
                    for i in range (0, len(row)):
                        if i % 2 == 0 and row[i] not in d:
                            d[row[i]] = []
                        if i > 0 and row[i - 1] in d:
                            d[row[i-1]].append(row[i])

def plot_stuff(): #NOT DYNAMIC!!! <- to do, make it dynamically graph dict keys arrays
    plt.grid()
    plt.plot(d["delta"], "b-")
    plt.title("Quanergy Time and Msg Pack Time Diffrence Vs Time")
    plt.legend(["Delta"])
    plt.ylabel("Time Difference (ms)")
    plt.xlabel("Time (ms)") #almost real time
    plt.show()

init_stuff()
read_stuff()
plot_stuff()
