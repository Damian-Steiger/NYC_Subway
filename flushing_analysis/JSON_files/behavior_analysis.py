#imports
import json
import re
import os
import matplotlib.pyplot as plt
import numpy as np
import time
import csv
import simplejson
import sys

def init_stuff():
    global json_data # dynamic train data array
    global yard_dict # static dict of yard positions
    global track_array # array of trak data for graph
    global yard_array # array of yard data for graph
    global total_trips # counts # of total trips
    global first # location of first transfer (for stacked graphs)
    global x_ticks # counts linearly by += 1 for x axis reference
    global train_dictionary

    json_data = []
    yard_dict = dict()
    track_array = []
    yard_array = []
    total_trips = []
    first = []
    x_ticks = 0
    train_dictionary = dict()

def do_plot():
    fig, ax = plt.subplots()
    ind = np.arange(len(total_trips))
    width = 0.4
    for i in range (0, len(track_array)):
        if yard_array[i] < 1 or track_array[i] < 1:
            pass
        if first[i] == "yard":
            yard_rects = ax.barh(i,yard_array[i],width,label='Yard',color = 'r')
            track_rects = ax.barh(i,track_array[i],width,label='Revenue',color='b', left = yard_array[i])
        elif first[i] == "track":
            track_rects = ax.barh(i,track_array[i],width,label='Revenue',color = 'b')
            yard_rects = ax.barh(i,yard_array[i],width,label='Yard',color = 'r', left = track_array[i])
    ax.set_xlabel('Time (Hours)')
    ax.set_ylabel('Trip Number')
    ax.set_title('Trips - Time in Yard vs Revenue')
    ax.set_yticks(ind+(width/2))
    ax.set_yticklabels(total_trips)
    ax.legend(["Yard", "Revenue"])
    ax.grid()
    ax.text(-1,-3,"Average Yard Time: "+str(sum(yard_array)/len(total_trips)))
    ax.text(-1,-5,"Average Track Time: "+str(sum(track_array)/len(total_trips)))

def do_plot2():
    fig, ax = plt.subplots()
    ind = np.arange(len(total_trips))
    width = 0.4
    track_rects=ax.bar(ind-width/2,track_array,width,label='Revenue',color='b')
    yard_rects = ax.bar(ind+width/2,yard_array,width,label='Yard',color = 'r')
    ax.set_ylabel('Time (Hours)')
    ax.set_xlabel('Trip Number')
    ax.set_title('Trips - Time in Yard vs Revenue')
    ax.set_xticks(ind+(width/2))
    ax.set_xticklabels(total_trips, rotation = "70")
    ax.legend()
    ax.grid()
    ax.text(-1,-5,"Average Yard Time: "+str(sum(yard_array)/len(total_trips)))
    ax.text(-1,-6,"Average Track Time: "+str(sum(track_array)/len(total_trips)))

def read_file():
    global yard_dict
    yard_positions = []
    init_stuff()
    dire = os.listdir(sys.argv[1])  #list files from directory
    dire.sort()
    CONTROL = True

    for f in dire: # read checkpoint and yard dictionary first
        if f.endswith("checkpoint.json"):
            temp = f
            dire.remove(f)
            dire.insert(1, temp)
        if f.endswith("yard_positions.json"):
            temp = f
            dire.remove(f)
            dire.insert(0, temp)

    for f in dire:  #run through all the files
        if f.endswith(".json") and CONTROL: #Only first checkpoint
            print("File = {}".format(f))
            with open(sys.argv[1] + '/' + f, 'r') as reader:
                filter_json(simplejson.load(reader))
                processing(json_data)
                clear_data()
        if f.endswith('yard_positions.json'):# load yard positions
            print('Yard Positions File = {}'.format(f))
            with open(sys.argv[1] + '/' + f, 'r') as reader:
                yard_positions = yard_positions + simplejson.load(reader)
            CONTROL = True
        for k in range (0,len(yard_positions)): #converts yard positions to dict for efficiency
                if yard_positions[k] not in yard_dict:
                    yard_dict[yard_positions[k]] = ''

def filter_json(json):
    global json_data
    for i in json:
        if (i["Group Name"] == "SVBTrain"
            and re.match('0::1[0-9][0-9][0-9]',
            i["ObjectID"])):
            json_data.append(i)

def processing(array):
    now = None
    for json in array:
        now = json["epoch"]
        if json["Group Name"] == "SVBTrain":
            name = json["ObjectID"]
            if re.match('0::1[0-9][0-9][0-9]', name):
                if True or name == "0::1006":
                    if name not in train_dictionary:
                        train_dictionary[name] = Train(name, json)
                        if train_dictionary[name].state == "yard":
                            train_dictionary[name].ystart = now
                        else:
                            train_dictionary[name].tstart = now
                    else:
                        train_dictionary[name].update(json)

    for name, trn in train_dictionary.items(): ##idk why this breaks it
        trn.finalize(now)

def clear_data():
    global json_data
    json_data = []

class Train:
    PKEY = "ITrain::EV_POSITION"
    yend = 0
    tend = 0
    ystart = 0
    tstart = 0
    def __init__(self, name, json):
        global yard_dict
        self.name = name
        self.track_time = 0
        self.yard_time = 0
        self.transfers = -1
        self.epoch = json["epoch"]
        self.state = self.location(json)
        self.pos = self.position(json)
        self.first = self.location(json)

    def __str__(self):
        tm = runtime.strftime('%Y-%m-%d %H:%M:%S',
                              runtime.localtime(self.epoch / 1000.0))
        return "{} - Train {} loc={} pos={} yard{} track={} xfer={}".format(
                tm, self.name, self.state, self.pos, self.yard_time,
                self.track_time, self.transfers)

    def location(self, json):
        if self.PKEY in json and len(json[self.PKEY]["pos"]) > 0:
            if json[self.PKEY]["pos"][0] in yard_dict:
                return 'yard'
            else:
                return 'track'
        return 'unknown'

    def position(self, json):
        if self.PKEY in json and len(json[self.PKEY]["pos"]) > 0:
            return json[self.PKEY]["pos"][0]
        else:
            return 0

    def update(self, json):
        now = json["epoch"]

        if self.state == "unknown":
            self.state = self.location(json)
            self.pos = self.position(json)

            if self.state != "unknown":
                pointless = True
                #print("LOCO: {}".format(self))
        else:
            if self.location(json) != 'unknown':
                self.pos = self.position(json)

                if self.location(json) != self.state:
                    self.state = self.location(json)

                    if self.state == 'track':
                        self.yard_time += now - self.epoch

                    else:
                        self.track_time += now - self.epoch
                    self.transfers += 1
                    #print("UPDT: {}".format(self))
                    self.epoch = now

                if self.transfers >= 2:
                    self.trip_offload()


    def finalize(self, now):
        if self.state == 'yard':
            self.yard_time += now - self.epoch
        else:
            self.track_time += now - self.epoch

    def trip_offload(self):
        global x_ticks
        track_array.append(float(self.track_time / 3600000))
        yard_array.append(float(self.yard_time / 3600000))
        x_ticks += 1
        total_trips.append(str(x_ticks) + " : "+ self.name)
        if self.first == "yard":
            first.append("yard")
        else:
            first.append("track")
        self.reset_train()

    def reset_train(self):
        global train_dictionary
        self.track_time = 0
        self.yard_time = 0
        self.transfers = 0
        del train_dictionary[self.name]

read_file()
do_plot()
do_plot2()
