
#imports
import json
import re
import os
import matplotlib.pyplot as plt
import numpy as np
import simplejson
import time
import csv
import sys

def init_stuff():
    global json_data
    global yard_array
    global yard_dict
    global yard_counter
    global already_dict
    global split
    global ticks
    global master_time

    yard_counter = 0
    yard_array = []
    json_data = []
    yard_dict = dict()
    already_dict = dict()
    split = ''
    ticks = []
    master_time = str(time.time())

def clear_data():
    global json_data
    global yard_array
    global yard_counter
    global already_dict
    global split
    global ticks
    global already_dict
    yard_array.append(yard_counter)
    yard_counter = 0
    json_data = []
    tm=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(split/1000.0))
    ticks.append(tm)
    already_dict.clear()


def graph_it():
    plt.figure(figsize=(20,10))
    directory = os.getcwd()
    x_pos = np.arange(len(yard_array))
    plt.bar(x_pos, yard_array)
    plt.grid()
    y = 0
    i = 0
    colors = ['r','b','g','c','m','y','#FFC0CB']
    day = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday']
    iteration = [24,19,21,9,12,24,24]
    while y < 125:
        plt.axvspan(xmin = y, xmax = y + iteration[i], color = colors[i], alpha=0.25)
        plt.text(y+(iteration[i])/3, max(yard_array), day[i], alpha=0.5, size = 7)
        y += iteration[i]
        i += 1
    plt.ylabel('Trains in Yard')
    plt.xlabel('Hours')
    plt.title('Trains in Yard')
    #plt.savefig(directory+"/graphs/"+str(time.time()) + '.png', dpi = 150)
    plt.show()

def read_file():
    global master_time
    yard_positions = []
    init_stuff()
    dire = os.listdir(sys.argv[1])  #list files from directory
    dire.sort()

    with open('csv/' + master_time+'_yard_log.csv', 'w') as csvF:
        title = ['Time', 'Train', 'Status']
        csv.writer(csvF).writerow(title)
    csvF.close()

    for f in dire:  #run through all the files
        if f.endswith('yard_positions.json'):# load yard positions
            print('After File = {}'.format(f))
            with open(sys.argv[1] + '/' + f, 'r') as reader:
                yard_positions = yard_positions + simplejson.load(reader)
        for k in range (0,len(yard_positions)): #converts yard positions to dict for efficiency
                if yard_positions[k] not in yard_dict:
                    yard_dict[yard_positions[k]] = ''
        if f.endswith('checkpoint.json'):
            print('After File = {}'.format(f))
            with open(sys.argv[1] + '/' + f, 'r') as reader:
                json_data = json.load(reader)
                process_file(json_data)
                clear_data()

def process_file(json_array):
    global yard_counter
    global split
    global master_time
    global already_dict
    controller = 0
    with open('csv/' + master_time+'_log.csv', 'a') as csvF:
        contents = ['-', '-', "-"]
        csv.writer(csvF).writerow(contents)
        for i in json_array:
            if controller == 0:
                split = i['epoch']
                controller = 1
            if i['Group Name'] == 'SVBTrain' and re.match('0::1[0-9][0-9][0-9]',
                    i['ObjectID']):
                try:
                    if (i['ITrain::EV_POSITION']['pos'][0] in yard_dict and
                            i['ObjectID'] not in already_dict):
                        yard_counter += 1
                        already_dict[i['ObjectID']] = None
                        tm = time.strftime('%Y-%m-%d %H:%M:%S',
                                          time.localtime(i['epoch']/1000.0))
                        contents = [tm, i['ObjectID'], "In Yard"]
                        csv.writer(csvF).writerow(contents)
                except (KeyError, IndexError) as e:
                    pass
    csvF.close()
read_file()
graph_it()
