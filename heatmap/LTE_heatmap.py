
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import math
import os
import csv

def read_csv():
    dir = os.listdir(os.getcwd())
    dir.sort()
    for fn in dir:
        if fn.endswith('.csv'):
            with open (fn) as csvf:
                csvr = csv.reader(csvf, delimiter = ',')
                for row in csvr:
                    print(converter(row[0],row[1],row[2]))

def converter(lat,lon,alt):
    lat = float(lat)
    lon = float(lon)
    alt = float(alt)
    a = 6378137
    e = 8.1819190842622e-2  
    N = a / math.sqrt(1- math.pow(e, 2)) * math.pow(math.sin(lat), 2)

    X = ((N+alt) * math.cos(lat) * math.cos(lon))
    Y = ((N+alt) * math.cos(lat) * math.sin(lon))
    Z = ((1 - math.pow(e,2) * (N + alt)) * math.sin(lat))

    return [X,Y,Z]

def heat_map():
    np.random.seed(0)
    sns.set()
    uniform_data = np.random.rand(10,12)
    ax = sns.heatmap(uniform_data)
    plt.show()

read_csv()
