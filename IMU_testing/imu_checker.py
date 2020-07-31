'''
train UDP tester
'''

import sys, struct, pyimu
import msgpack
import numpy
import os
import matplotlib.pyplot as plt

dirName = '/home/rtuser/damian/IMU_testing'

count = 0

class Imu():
    def __init__(self, size):
        self.size = size #individual imu packet size
        self.errors = 0

    """
    Returns a list of imu msg objects, build as a dictionary with timestamp and data keys
    """
    def parseMsgBlock(self, data, t):
        if (len(data) % self.size != 0):
            print("Unexpected IMU message format!")
            return

        # ~ print "imu msg size %d" % len(data)

        msgs = []
        for i in range(int(len(data)/self.size)):
            try:
                tmp = {"epoch_ns" : t, "data": pyimu.pstr_to_imu(data[i*self.size: i*self.size + self.size])}
                msgs.append(tmp)
            except Exception as e:
                print("Caught IMU parsing error %s" % e)
                self.errors += 1

        return msgs

def unpack_piper(data):

    piper_msg = {}

    piper_msg['interface_type'] = struct.unpack('>B', data[0:1])[0]
    piper_msg['telegram_type'] = struct.unpack('>B', data[1:2])[0]
    piper_msg['transmitter_class'] = struct.unpack('>H', data[2:4])[0]
    piper_msg['transmitter_id'] = struct.unpack('>H', data[4:6])[0]
    piper_msg['rsn'] = struct.unpack('>H', data[6:8])[0]
    piper_msg['tsn'] = struct.unpack('>H', data[8:10])[0]
    piper_msg['length'] = struct.unpack('>H', data[10:12])[0]

    piper_msg['nsecs'] = struct.unpack('>Q', data[12:20])[0]
    piper_msg['tag_id'] = struct.unpack('>I', data[20:24])[0]
    piper_msg['edge_id'] = struct.unpack('>I', data[24:28])[0]
    piper_msg['offset'] = struct.unpack('>I', data[28:32])[0]
    piper_msg['est_error'] = struct.unpack('>I', data[32:36])[0]
    piper_msg['status'] = struct.unpack('>I', data[36:40])[0]
    piper_msg['vendor_data'] = []
    for i in range(32):
        piper_msg['vendor_data'].append(struct.unpack('>B', data[40+i:40+i+1])[0])

    piper_msg['crc'] = struct.unpack('>I', data[72:76])[0]

    return piper_msg

imu = Imu(38)
radars = {}
imus = {}
last_imu = {}
rad_time = {}
imu_dict = dict()
last_time = {}
directory = numpy.sort(os.listdir(dirName))
for fileName in directory:
    if fileName.endswith(".mpk"):
        with open(dirName + '/' + fileName,"rb") as f:
            up = msgpack.Unpacker(f)
            for d in up:
                try:
                    b = d[-1] #last element is the UDP data

                    # if (b[3] == 12): #12 is continental in Thales header
                    #
                    #     sensor_type = struct.unpack('>H', b[2:4])[0]   #sensor type (bosch, imu, etc)
                    #     sensor_id = struct.unpack('>H', b[4:6])[0]    #sensor id (c2e id)
                    #     epoch = struct.unpack('>Q', b[10:18])[0]     #timestamp! (from c2e, ns)
                    #
                    #     if sensor_id not in radars:
                    #         radars[sensor_id] = pycontinental.Continental()
                    #         rad_time[sensor_id] = -1
                    #
                    #     data = b[20:-2]
                    #     rad = radars[sensor_id].process(data, len(data), 0)
                    #
                    #     if (rad):
                    #         count += 1
                    #         last_time =  epoch/1e9
                    #         if radars[sensor_id].data["mode"] == 1:
                    #             pass
                    #             # ~ print "Obj"
                    #         elif radars[sensor_id].data["mode"] == 2:
                    #             # print("clu")
                    #             if rad_time[sensor_id] > -1 and epoch/1e9 - rad_time[sensor_id] > 0.08:
                    #                 print("rad time jump", sensor_id, epoch/1e9 - rad_time[sensor_id])
                    #             rad_time[sensor_id] = epoch/1e9
                    #             # print(sensor_type,sensor_id, epoch/1e9)
                    #             # break

                    if (b[3] == 10):
                        # print("imu")
                        sensor_id = struct.unpack('>H', b[4:6])[0]
                        epoch = struct.unpack('>Q', b[10:18])[0]     #timestamp! (from c2e, ns)
                        data = b[20:-2]
                        if sensor_id not in imus:
                            imus[sensor_id] = []
                            last_imu[sensor_id] = -1
                        if sensor_id not in last_time and epoch > 1.5e18:
                            last_time[sensor_id] = epoch/1e9
                        elif sensor_id in last_time:

                            msgs = imu.parseMsgBlock(data, epoch)
                            if (msgs):

                                if epoch < 1.5e18:
                                    epoch = last_time[sensor_id] + .06
                                    error_msg = msgs
                                else:
                                    epoch = epoch / 1e9
                                if sensor_id not in imu_dict.keys():
                                        imu_dict[sensor_id] = {"epoch":[msgs[-1]["epoch_ns"]/1e9],"drop_count":[0]}
                                if last_imu[sensor_id] > -1 and not msgs[-1]['data']['msg_counter'] - last_imu[sensor_id] == 6:
                                    print("Imu skip",sensor_id, msgs[-1]['data']['msg_counter'] - last_imu[sensor_id] - 6)
                                    #[y['data']['msg_counter'] for y in msgs]

                                    if (msgs[-1]['data']['msg_counter'] - last_imu[sensor_id] - 6) <= 6 and not (msgs[-1]['data']['msg_counter'] - last_imu[sensor_id] - 6) == -65536:
                                        imu_dict[sensor_id]["drop_count"].append(imu_dict[sensor_id]["drop_count"][-1] + (msgs[-1]['data']['msg_counter'] - last_imu[sensor_id] - 6))
                                        imu_dict[sensor_id]["epoch"].append(epoch)
                                # else:
                                    # print("IMU good ", sensor_id)

                                # print([y['data']['msg_counter'] for y in msgs])

                                last_imu[sensor_id] = msgs[-1]['data']['msg_counter']
                                last_time[sensor_id] =  epoch
                            else:
                                print('error')
                            #imus[sensor_id].append(msgs)
                        # for i in range(6):
                        #
                        #     print(pyimu.pstr_to_imu(b[20:20+38]))


                            # ~ print radars[sensor_id].data["s_data"]["obj_status"]

                    elif b[3] == 20:

                        if len(b) == 76:
                            piper_msg = unpack_piper(b)
                            print("Piper msgs, ID: {}, edge: {}, offet: {}, status: {}, time: {}, timeDiff: {}".format(piper_msg['tag_id'],piper_msg['edge_id'],piper_msg['offset'],piper_msg['status'],piper_msg['nsecs']/1e9,last_time-piper_msg['nsecs']/1e9))
                        else:
                            print("Piper msg error, length: {} not 76.".format(len(b)))

                    else:
                        print("Other: ", b[3])
                except EOFError:
                    print("End of file!")
                    print(count)
                    break
    # [[y['data']['msg_counter'] for y in x] for x in imus[476]]

def plot_it():
    e = 0
    color = ["b","r","g","m"]
    for i in imu_dict.keys():
        plt.plot([x-imu_dict[i]["epoch"][0] for x in imu_dict[i]["epoch"]],imu_dict[i]["drop_count"], color[e] + '-', label = "IMU " + str(i))
        e+=1
    plt.legend()
    plt.show()
