#################Setup Junk#################
import math
import os
import matplotlib.pyplot as plt
import numpy as np
from numpy import diff

directory = os.getcwd()# Grabs the current directory
files = os.listdir(directory)
files.sort()
UWB_dict = dict([])
names_array = []
titles = []
control = 0
ground_truth = [5.116, 10.016, 14.639, 19.611, 25.117, 29.813, 34.380, 39.648,
                44.765, 49.715, 54.855, 60.287, 65.710, 70.790, 76.119, 81.406,
                85.503, 90.484, 95.459, 100.447, 105.085, 110.331, 114.405, 119.695,
                124.402, 129.495, 135.144, 139.423, 144.975, 149.809, 155.145,
                159.635, 165, 175, 200]
skeleton_key = True

def UWB_birth(name, first_reading):
    if first_reading > 500:
        first_reading = first_reading / 1000
    UWB_dict[name] = UWB(name, [], 0, [], [], 0, [], [])
    UWB_dict[name].measurement_array.append(first_reading)
    names_array.append(name)

def reset_objs():
    for i in UWB_dict:
        UWB_dict[i].dropped_msg_array.append(UWB_dict[i].dropped_msg)
        UWB_dict[i].measurement_array = []
        UWB_dict[i].dropped_msg = 0

def lobf(X , Y):
    xbar = sum(X)/len(X)
    ybar = sum(Y)/len(Y)
    n = len(X) # or len(Y)
    numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi**2 for xi in X]) - n * xbar**2
    b = numer / denum
    a = ybar - b * xbar
    return a, b

def equation(X , Y):
    xbar = sum(X)/len(X)
    ybar = sum(Y)/len(Y)
    n = len(X) # or len(Y)
    numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi**2 for xi in X]) - n * xbar**2
    b = numer / denum
    a = ybar - b * xbar
    return('y = {:.2f} + {:.2f}x'.format(a, b))

class UWB:
    def __init__(self, name, measurement_array, dropped_msg , standard_deviation_array, avg_dist_array, all_dropped_msg, dropped_msg_array, total_measurements):
        self.name = name
        self.measurement_array = measurement_array
        self.dropped_msg = dropped_msg
        self.standard_deviation_array = standard_deviation_array
        self.avg_dist_array = avg_dist_array
        self.all_dropped_msg = all_dropped_msg
        self.dropped_msg_array = dropped_msg_array
        self.total_measurements = total_measurements

    def add_measurement(self, measurement):
        if measurement > 500:
            measurement = measurement / 1000
        self.measurement_array.append(measurement)

    def add_dropped_msg(self, index):
        del self.measurement_array[index]
        self.all_dropped_msg += 1
        self.dropped_msg += 1

    def standard_deviation(self):
        try:
            self.standard_deviation_array.append(max(self.measurement_array) - min(self.measurement_array))
        except ValueError:
            pass

    def avg_dist(self):
        try:
            self.avg_dist_array.append(sum(self.measurement_array) / len(self.measurement_array))
        except ZeroDivisionError:
            pass

    def add_total_measurements(self):
        self.total_measurements.append(len(self.measurement_array))

    def total_time_msg(self, time, total, control):
        t_msg = round((max(time) - min(time))*2)
        self.all_dropped_msg += t_msg - total
        self.dropped_msg += t_msg - total
        self.total_measurements[control] += t_msg - total

#load through every file
for i in files:
    if i.endswith(".csv"):
        data_sheet = open(i, "r")
        print(i)#prints file name
        time_array = []
        for x in data_sheet:
            title = x.split(",")
            if(title[1] == "MSG"):
                continue
            #adds measurements to array within dict
            if title[1] not in UWB_dict:
                UWB_birth(title[1], float(title[9]))
            elif title[1] in UWB_dict:
                UWB_dict[title[1]].add_measurement(float(title[9]))
            time_array.append(float(title[0]))

        #iterates through all dict keys
        try:
            for outer_index in range (0,len(UWB_dict)):

                #counts total measurements
                UWB_dict[names_array[outer_index]].add_total_measurements()

                #gets the total time in a file
                UWB_dict[names_array[outer_index]].total_time_msg(time_array, UWB_dict[names_array[outer_index]].total_measurements[control], control)

                #iterates through all measurements from objs in dict
                last_val = 0
                inner_index = 0 #decleration of looop index

                while inner_index < len(UWB_dict[names_array[outer_index]].measurement_array):

                    #counts number of missed messages
                    if UWB_dict[names_array[outer_index]].measurement_array[inner_index] == 0 or UWB_dict[names_array[outer_index]].measurement_array[inner_index] == last_val or UWB_dict[names_array[outer_index]].measurement_array[inner_index] > (ground_truth[control] + 5) or UWB_dict[names_array[outer_index]].measurement_array[inner_index] < (ground_truth[control] - 5):
                        last_val = UWB_dict[names_array[outer_index]].measurement_array[inner_index]
                        UWB_dict[names_array[outer_index]].add_dropped_msg(inner_index)
                        inner_index -= 1
                    else:
                        last_val = UWB_dict[names_array[outer_index]].measurement_array[inner_index]

                    inner_index +=1#controls the loop index

                #calculate standard deviation
                UWB_dict[names_array[outer_index]].standard_deviation()#try / pass is a temp solution

                #Calculate average difference
                UWB_dict[names_array[outer_index]].avg_dist()#try / pass is a temp solution

        except IndexError:
            pass

        #individual graphs
        plt.figure(1)
        plt.title('DECA-Blue vs HUMATICS-Green vs DW_THALES-Red at ' + str(round((UWB_dict[names_array[0]].measurement_array[0])/5)*5) + ' m')
        plt.legend(loc = 'upper left',frameon = False,)
        plt.plot(UWB_dict[names_array[0]].measurement_array,'bo')
        plt.plot(UWB_dict[names_array[1]].measurement_array,'ro')
        plt.plot(UWB_dict[names_array[2]].measurement_array,'go')
        plt.ylabel('Distance (m)')
        plt.xlabel('Instance of Measurement - Every .5 seconds')
        plt.grid()
        #plt.show()

        #reset obj
        reset_objs()
        control += 1

        continue
    else:
        continue

#Tyler Error Graph
plt.figure(8)
plt.title('Humatics Error vs Distance')
tyler_point = []
for k in range (0, len(UWB_dict[names_array[2]].avg_dist_array)):
    tyler_point.append(((UWB_dict[names_array[2]].avg_dist_array[k] - ground_truth[k])/(UWB_dict[names_array[2]].avg_dist_array[k] + ground_truth[k]))*100)
plt.ylabel('Error (%)')
plt.xlabel('Ground Truth Distance (m)')
for x in range (0, len(ground_truth)):
    ground_truth[x] = int((round(ground_truth[x]/5)*5))
plt.xticks(np.arange(len(ground_truth)), ground_truth)
plt.errorbar(np.arange(len(ground_truth)), tyler_point, yerr = UWB_dict[names_array[2]].standard_deviation_array, fmt = 'go' )
plt.legend(["Humatics Standard Deviation"], loc='upper left', numpoints=1)
plt.grid()
plt.show()

if skeleton_key:
    #all-file graphs - standard deviation
    plt.figure(2)
    plt.title('Standard Deviation - DECA-Blue vs  HUMATICS-Green vs DW_THALES-Red')
    plt.plot(UWB_dict[names_array[0]].standard_deviation_array,'bo')
    plt.plot(UWB_dict[names_array[1]].standard_deviation_array,'ro')
    plt.plot(UWB_dict[names_array[2]].standard_deviation_array,'go')
    plt.ylabel('Distance (m)')
    plt.xlabel('File Number - (# x 10 = Distance in m))')
    plt.grid()

    #all-file graphs - average difference (no DW_THALES)
    plt.figure(3)
    plt.title('Average Measurement - DECA-Blue vs  HUMATICS-Green')
    plt.plot(UWB_dict[names_array[0]].avg_dist_array,'bo')
    plt.plot(UWB_dict[names_array[1]].avg_dist_array,'ro')
    plt.plot(UWB_dict[names_array[2]].avg_dist_array,'go')
    plt.ylabel('Distance (m)')
    plt.xlabel('File Number - (# x 10 = Distance in m))')
    plt.grid()

    #all-file graph - missed messages
    objects = ("DECA"," HUMATICS", "DW_THALES")
    y_pos = np.arange(len(objects))
    performance = [UWB_dict[names_array[0]].all_dropped_msg, UWB_dict[names_array[1]].all_dropped_msg, UWB_dict[names_array[2]].all_dropped_msg]
    plt.figure(4)
    plt.subplot(2,1,1)
    plt.title('Total Missed Messages')
    plt.xlabel('UWB')
    plt.ylabel('Number of Missed Messages')
    plt.xticks(y_pos, objects)
    plt.bar(y_pos, performance, align = "center", alpha = 0.5, color = 'violet')
    plt.grid()

    #individual graph - missed messages
    index = np.arange(control)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=.5)
    plt.subplot(2,1,2)
    plt.title('Missed Messages')
    bar_width = 0.3
    rects1 = plt.bar(index, UWB_dict[names_array[0]].dropped_msg_array, bar_width, color = 'r')
    rects2 = plt.bar(index + bar_width,UWB_dict[names_array[1]].dropped_msg_array, bar_width, color = 'b')
    rects3 = plt.bar(index + bar_width + bar_width, UWB_dict[names_array[2]].dropped_msg_array, bar_width, color = 'g')
    plt.legend(["DW API", "Deca", "Humatics"])
    plt.ylabel('# of Missed Messages')
    plt.xlabel('Ground Truth Distance (m)')

    plt.xticks(np.arange(len(ground_truth)), ground_truth)
    plt.xticks(index + bar_width, (ground_truth))
    plt.grid()

    #DW_API vs GT dist
    a, b = lobf(ground_truth, UWB_dict[names_array[2]].avg_dist_array)
    yfit = [a + b * xi for xi in ground_truth]
    dydx = diff(UWB_dict[names_array[2]].avg_dist_array) / diff(ground_truth) # calculate derivatives
    plt.figure(5)
    plt.title('Humatics Average vs Ground Truth')
    plt.plot(ground_truth, UWB_dict[names_array[2]].avg_dist_array ,'go')
    plt.plot(ground_truth, yfit, 'r-')
    plt.legend(["Humatics Avg Dist", equation(ground_truth, UWB_dict[names_array[2]].avg_dist_array)])
    plt.ylabel('UWB Distance (m)')
    plt.xlabel('Laser Distance (m)')
    for x in range (0, len(ground_truth)):
        ground_truth[x] = int((round(ground_truth[x]/5)*5))
    plt.grid()
    #shows given figure
    plt.show()

    #individual standard deviation
    plt.figure(6)
    plt.title('DW API Standard Deviation vs Ground Truth Distance (m)')
    plt.xlabel('Ground Truth Distance (m)')
    plt.ylabel('Distance (m)')
    plt.bar(np.arange(len(ground_truth)), UWB_dict[names_array[0]].standard_deviation_array, align = "center", alpha = 0.5)
    plt.xticks(np.arange(len(ground_truth)), ground_truth)
    plt.legend(["Standard Deviation"])
    plt.grid()

    drop_percent_array = []
    #for k in range (0, len(UWB_dict[names_array[0]].dropped_msg_array)):
    #    percent = float((float(UWB_dict[names_array[0]].dropped_msg_array[k]) / UWB_dict[names_array[0]].total_measurements[k] * 100))
    #    drop_percent_array.append(percent)
    plt.figure(7)
    plt.title("DW API Drop % vs Distance (m)")
    plt.xlabel("Distance (m)")
    plt.ylabel("Drop %")
    #plt.bar(np.arange(len(ground_truth)), drop_percent_array, align = "center", alpha = 0.5)
    plt.legend(["Drop %"])
    plt.grid()





#ground truths
# outside 5-100m : 5.515, 9.8595 , 15.525, 20.951, 25.4355, 29.6215, 34.495, 39.890, 44.781, 49.685, 55.503, 59.766, 64.510, 69.197, 75.401, 80.969, 85.608, 90.390, 94.688, 100.35
