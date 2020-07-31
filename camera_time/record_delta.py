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
	global epochs
	global delta

	basePath = os.getcwd()#directory with .mpk files
	fileList = [x for x in np.sort(os.listdir(basePath)) if x.endswith('.mpk')]
	w_dir = basePath + "/csv_cam_time/"
	epochs = []
	delta = []

def msg_to_csv():
	for fileName in fileList:
		with open(basePath + '/'+fileName,"rb") as f:
			up = msgpack.Unpacker(f)
			for d in up:
				epochs.append(d[0] / 1e9)

def fn_time_delta():
	for x in range (0, len(epochs)):
		if x > 0:
			d = (epochs[x] - epochs[x-1])
			delta.append(d)
	return delta

def total_time():
	return epochs[len(epochs)-1] - epochs[0]

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
	msg_to_csv()
	do_plot()
run()
