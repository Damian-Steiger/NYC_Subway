#!/usr/bin/python3

import msgpack
import numpy as np
import os
import csv
import matplotlib.pyplot as plt

def init():
	global basePath
	global fileList
	global w_dir
	global fileName_array
	global delta

	basePath = os.getcwd()#directory with .mpk files
	fileList = [x for x in np.sort(os.listdir(basePath)) if x.endswith('.jpg')]
	w_dir = basePath + "/csv_cam_time/"
	fileName_array = []
	delta = []

def msg_to_csv():
	try:
		os.mkdir(w_dir)
	except OSError:
		print("Directory \""+str(w_dir)+"\" already exists, was not created.")
	for fileName in fileList:
		with open(basePath + '/'+fileName,"rb") as f:
			open(w_dir + fileName[:(len(fileName)-4)]+".csv",mode='x').close()
			up = msgpack.Unpacker(f)
			print(up)
			with open((w_dir + fileName[:(len(fileName)-4)] + ".csv"),
			mode='w') as w_file:
				for d in up:
					print(d)
					qd = pyquanergy.getQF(d[-1])

def fn_time_delta():
	for fileName in fileList:
		fileName_array.append(int(fileName[:len(fileName)-4]) / 1e9)
	for x in range (0, len(fileName_array)):
		if x > 0:
			d = (fileName_array[x] - fileName_array[x-1])
			delta.append(d)
	return delta

def total_time():
	return fileName_array[len(fileName_array)-1] - fileName_array[0]

def avg_time():
	total = 0
	for x in range (0,len(delta)):
		total += delta[x]
	total = (total / len(delta))
	return total

def do_plot():
	plt.grid()
	plt.plot(fn_time_delta(), "bo")
	plt.title("Time Between Camera Files")
	plt.legend(["Delta"])
	plt.ylabel("Time Difference (s)")
	plt.xlabel("Instance") #almost real time
	plt.figtext(.025, .025, " Total Elapsed Time: " + str(total_time())
				+ "s\n Average Delta: " + str(avg_time()) + "s")
	plt.show()

def run():
	init()
	do_plot()
run()
print(delta)
