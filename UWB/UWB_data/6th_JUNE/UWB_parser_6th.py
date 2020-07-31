#!/usr/bin/python
import csv, re, math, os
import matplotlib.pyplot as plt
import numpy as np

#all-file variables
directory = '/home/rtuser/Desktop/damian/UWB/UWB_data/6th_JUNE'
DECA_standard_deviation_array = []
FULL_standard_deviation_array = []
DECA_average_measurement = []
FULL_average_measurement = []
difference_array = []
FULL_count = 0
DECA_count = 0
DECA_count_array = []
FULL_count_array = []
control = 0
titles = []
ground_truth = ['9.692','19.713','29.600','39.781','49.704','59.691','69.656','79.701','89.682','99.697','109.739',
                '119.604','129.908','139.589','149.523','179.743','190.240','200.213','220','230','240','250','260']

#load through every file
files = os.listdir(directory)
files.sort()
for index in files:
    if index.endswith(".csv"):

        #individual graph variables
        DECA_data_array_unrefined = []
        FULL_data_array_unrefined = []
        total_DECA = 0
        total_FULL = 0
        FULL_count_file = 0
        DECA_count_file = 0

        #read the file, parse it using the commas into an array
        data_sheet = open(index, "r")
        for x in data_sheet:
            test = x.split(",")
            if test[1] == "DECA_RANGE":
             DECA_data_array_unrefined.append(test[8])
            elif test[1] == "FULL_RANGE_INFO":
             FULL_data_array_unrefined.append(test[8])

        #Convert "DECA_data_array_unrefined" to floats
        DECA_data_array_refined = [float(x) for x in DECA_data_array_unrefined]

        #convert "FULL_data_array_refined" to meters and into floats
        FULL_data_array_between = [float(x) for x in FULL_data_array_unrefined]
        FULL_data_array_refined = [x/1000 for x in FULL_data_array_between]

        #counts number of missed packages
        for i in range(0,len(DECA_data_array_refined)-1):
            if DECA_data_array_refined[i] == DECA_data_array_refined[i+1]:
                DECA_count += 1
                DECA_count_file += 1
        FULL_count = FULL_count + FULL_data_array_refined.count(0)
        FULL_count_file = FULL_data_array_refined.count(0)
        DECA_count_array.append(DECA_count_file)
        FULL_count_array.append(FULL_count_file)

        #Removes missed messages
        i = 0
        while i < len(DECA_data_array_refined)-1:
            if DECA_data_array_refined[i] == DECA_data_array_refined[i+1]:
                del DECA_data_array_refined[i]
            else:
                i += 1
        FULL_data_array_refined = filter(lambda a: a != 0, FULL_data_array_refined)

        #Calculate Standard Deviation
        DECA_standard_deviation = max(DECA_data_array_refined) - min(DECA_data_array_refined)
        FULL_standard_deviation = max(FULL_data_array_refined) - min(FULL_data_array_refined)
        DECA_standard_deviation_array.append(DECA_standard_deviation)
        FULL_standard_deviation_array.append(FULL_standard_deviation)

        #Calculate average difference
        for x in DECA_data_array_refined:
            total_DECA = total_DECA + x
        total_DECA = total_DECA / len(DECA_data_array_refined)
        for x in FULL_data_array_refined:
            total_FULL = total_FULL + x
        total_FULL = total_FULL / len(FULL_data_array_refined)
        average_difference = math.sqrt(math.pow((total_FULL - total_DECA),2))
        difference_array.append(average_difference)
        DECA_average_measurement.append(total_DECA)
        FULL_average_measurement.append(total_FULL)

        #calculates title number
        titles.append(10*(round(DECA_data_array_refined[0]/10)))

        #individual graphs
        plt.figure(1)
        plt.title('DECA-Blue vs HUMATICS-Green at ' + str(titles[control]) + ' m')
        plt.plot([0,120],[ground_truth[control],ground_truth[control]],'-r', label = 'Ground Truth')
        plt.legend(loc = 'upper left',frameon = False,)
        plt.plot(DECA_data_array_refined,'bo')
        plt.plot(FULL_data_array_refined,'go')
        plt.ylabel('Distance (m)')
        plt.xlabel('Instance of Measurement - Every .5 seconds')
        plt.grid()
        plt.show()

        #keeping track of file index
        control += 1

#end of file loading loop
        continue
    else:
        continue

#all-file graphs - standard deviation
plt.figure(2)
plt.title('Standard Deviation - DECA-Blue vs  HUMATICS-Green')
plt.plot(DECA_standard_deviation_array,'bo')
plt.plot(FULL_standard_deviation_array,'go')
plt.ylabel('Distance (m)')
plt.xlabel('File Number - (# x 10 = Distance in m))')
plt.grid()

#all-file graphs - average difference
plt.figure(3)
plt.subplot(2,1,1)
plt.title('Average Measurement - DECA-Blue vs  HUMATICS-Green')
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=.5)
plt.plot(DECA_average_measurement,'bo')
plt.plot(FULL_average_measurement,'go')
plt.ylabel('Distance (m)')
plt.xlabel('File Number - (# x 10 = Distance in m))')
plt.grid()
plt.subplot(2,1,2)
plt.title('Average Difference')
plt.plot(difference_array, 'ro')
plt.ylabel('Distance (m)')
plt.xlabel('File Number - (# x 10 = Distance in m))')
plt.grid()

#all-file graph - missed messages
objects = ("DECA"," HUMATICS")
y_pos = np.arange(len(objects))
performance = [DECA_count, FULL_count]
plt.figure(4)
plt.subplot(2,1,1)
plt.title('Total Missed Messages')
plt.xlabel('UWB')
plt.ylabel('Number of Missed Messages')
plt.xticks(y_pos, objects)
plt.bar(y_pos, performance, align = "center", alpha = 0.5)
plt.grid()

#individual graph - missed messages
index = np.arange(control)
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=.5)
plt.subplot(2,1,2)
plt.title('Missed Messages (DECA-Blue vs HUMATICS-Green)')
bar_width = 0.35
rects1 = plt.bar(index, DECA_count_array, bar_width, color = 'b')
rects2 = plt.bar(index + bar_width, FULL_count_array, bar_width, color = 'g')
plt.ylabel('# of Missed Messages')
plt.xlabel('File Number - (# x 10 = Distance in m))')
plt.xticks(index + bar_width, (titles))
plt.grid()
plt.show()
