
#imports
import json
import re
import os
import matplotlib.pyplot as plt
import numpy as np
import time
import csv
import sys

def init_stuff():
    global json_data # dynamic train data
    global check_data # static control data
    global couples # dynamic graph data
    global check_dict # static dict of control trains
    global coupling_count
    global master_time
    global split
    global ticks

    coupling_count = 0
    couples = []
    check_data = []
    json_data = []
    check_dict = dict()
    master_time = str(time.time())
    split = ''
    ticks = []

def graph_it():
    plt.figure(figsize=(20,10))
    directory = os.getcwd()
    x_pos = np.arange(len(couples))
    plt.bar(x_pos, couples)
    plt.grid()
    y = 0
    i = 0
    colors = ['r','b','g','c','m','y','#FFC0CB']
    day = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday']
    iteration = [23,16,21,7,12,24,24]
    while y < 120:
        plt.axvspan(xmin = y, xmax = y + iteration[i], color = colors[i], alpha=0.25)
        plt.text(y+iteration[i]/3, max(couples), day[i], alpha=0.5, size = 7)
        y += iteration[i]
        i += 1
    plt.ylabel('Couples')
    plt.xlabel('Hours')
    plt.title('Coupling Counter')
    #plt.savefig(directory+"/graphs/"+str(time.time()) + '.png', dpi = 150)
    plt.show()

def read_file():
    global master_time
    init_stuff()
    dire = os.listdir(sys.argv[1])  #list files from directory
    dire.sort()
    CONTROL = True

    with open('csv/' + master_time+'_coupling_log.csv', 'w') as csvF:
        title = ['Time', 'Unit 1', 'Unit 2', 'Event']
        csv.writer(csvF).writerow(title)
    csvF.close()

    for f in dire:
        if f.endswith("checkpoint.json"):
            temp = f
            dire.remove(f)
            dire.insert(0, temp)

    for f in dire:  #run through all the files
        if f.endswith("checkpoint.json") and CONTROL: #Only first checkpoint
            print("Checkpoint File = {}".format(f))
            CONTROL = False
            with open(sys.argv[1] + '/' + f, 'r') as reader:
                filter_json(json.load(reader), True)
                process_check(check_data)
        elif f.endswith("after.json"):
            print("After File = {}".format(f))
            with open(sys.argv[1] + '/' + f, 'r') as reader:
                filter_json(json.load(reader), False)
                process_file(json_data)
                clear_data()

def filter_json(json, CONTROL):
    global check_data
    global json_data
    for i in json:
        if i["Group Name"]=="SVBTrain" and re.match('0::1[0-9][0-9][0-9]',
            i["ObjectID"]) and CONTROL:
            check_data.append(i)
        if i["Group Name"] == "SVBTrain" and re.match('0::1[0-9][0-9][0-9]',
            i["ObjectID"]):
            json_data.append(i)

def process_check(json_array):
    global check_dict
    check_dict = dict()
    for i in json_array:
        unit_ID = i["ITrain::EV_VOBC"][0]["first"]["obj"]
        if unit_ID not in check_dict:
            try:
                buddy_ID = i["ITrain::EV_VOBC"][1]["first"]["obj"]
                check_dict[unit_ID] = Unit(unit_ID,buddy_ID)
                check_dict[buddy_ID] = Unit(buddy_ID,unit_ID)
            except IndexError:
                check_dict[unit_ID] = Unit(unit_ID,0)

def process_file(json_array):
    global check_dict
    global coupling_count
    global master_time
    global split
    controller = 0
    with open('csv/' + master_time+'_log.csv', 'a') as csvF:
        for i in json_array:
           if controller == 0:
                split = i['epoch']
                controller = 1
           try:
               unit_ID = i["ITrain::EV_VOBC"][0]["first"]["obj"]
               if unit_ID not in check_dict:
                try:
                    buddy_ID = i["ITrain::EV_VOBC"][1]["first"]["obj"]
                    check_dict[unit_ID] = Unit(unit_ID,buddy_ID)
                    check_dict[buddy_ID] = Unit(buddy_ID,unit_ID)
                except IndexError:
                    check_dict[unit_ID] = Unit(unit_ID,0)
               try:
                   if i["ITrain::EV_VOBC"][1]["first"]["obj"] != check_dict[unit_ID].buddy:
                       coupling_count += 1
                       tm = time.strftime('%Y-%m-%d %H:%M:%S',
                                          time.localtime(i['epoch']/1000.0))
                       contents = [tm, i["ITrain::EV_VOBC"][0]["first"]["obj"],
                                   check_dict[unit_ID].buddy, "Uncoupled"]
                       csv.writer(csvF).writerow(contents)
                       check_dict[unit_ID].buddy = i["ITrain::EV_VOBC"][1]["first"]["obj"]
                       check_dict[i["ITrain::EV_VOBC"][1]["first"]["obj"]].buddy = unit_ID
               except IndexError:
                   pass
           except KeyError:
               pass
    csvF.close()

def clear_data():
    global json_data
    global coupling_count
    global split
    global ticks
    couples.append(coupling_count)
    json_data = []
    coupling_count = 0
    tm=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(split/1000.0))
    ticks.append(tm)

class Unit:
    def __init__(self, name, buddy):
        self.name = name
        self.buddy = buddy

read_file()
graph_it()
