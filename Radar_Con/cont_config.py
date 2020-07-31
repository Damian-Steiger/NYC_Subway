  #!/usr/bin/python
import socket, struct, sys, time
import crcmod
from bitstring import Bits, BitArray
#arguments: device_id, port, filter
# example -- cont_config.py 1 8090 print

##### STEPS: run "print" statement and also "filters" statement

ip_addr = "10.4.128.11"
# ip_addr = "10.4.128.71"
udp_port = int(sys.argv[2])
dst_port = 8000

# Constants defined as per Connumication Protocols ICD
INTERFACE_TYPE_VOBC_RADAR=1009
TELEGRAM_TYPE_RFC=1
TELEGRAM_TYPE_PERIODIC_UPDATE=10
RECEIVER_CLASS_VOBC_CLASS_VALUE=1
RECEIVER_CLASS_RADAR_CLASS_VALUE=12    		#11 or 12 for CAN1, 13 for CAN0
TRANSMITTER_CLASS_VOBC_CLASS_VALUE=1
TRANSMITTER_CLASS_RADAR_CLASS_VALUE=9

#16 bit crc function x^16 + x^15 + x^2 + 1
crc16 = crcmod.mkCrcFun(0x18005, initCrc=0xFFFF, xorOut=0x0000)

def readRadar():
	data = sock.recv(1024)
	m_sen = data[10:12]
	m_sen = int(strToBin(m_sen),2)
	time_can = data[34:42]
	time_can = int(strToBin(time_can),2)/1000000000
	data = data[41:-2]
	canIDint = int(strToBin(data[:4][::-1]),2)
	db = strToBin(data[4:])
	db = ''.join([db[i:i+8][::-1] for i in range(0,64,8)])
	radarRaw = [canIDint, db, m_sen, time_can]
	return radarRaw

def addThalesProtocol(command):			#should be depracated
	interface_type = INTERFACE_TYPE_VOBC_RADAR
	interface_version = 0
	telegram_type = TELEGRAM_TYPE_PERIODIC_UPDATE
	receiver_class = RECEIVER_CLASS_RADAR_CLASS_VALUE
	receiver_id = int(sys.argv[1]) # adaptor ID
	transmitter_class = TRANSMITTER_CLASS_VOBC_CLASS_VALUE
	transmitter_id = 1066 # VOBC ID
	time_year = 2017
	time_month = 2
	time_day = 28
	time_hour = 0
	time_minute = 0
	time_second = 0
	time_millisecond = 0
	rsn = 0
	tsn = 100
	length = 20  # always 20 bytes for command and TSN&CRC frame
	database_compatibility_number = 0

	thHDR = [
		struct.pack('>H',interface_type),
		struct.pack('>B',interface_version),
		struct.pack('>B',telegram_type),
		struct.pack('>H',receiver_class),
		struct.pack('>H',receiver_id),
		struct.pack('>H',transmitter_class),
		struct.pack('>H',transmitter_id),
		struct.pack('>H',time_year),
		struct.pack('>H',time_month),
		struct.pack('>H',time_day),
		struct.pack('>H',time_hour),
		struct.pack('>H',time_minute),
		struct.pack('>H',time_second),
		struct.pack('>H',time_millisecond),
		struct.pack('>H',rsn),
		struct.pack('>H',tsn),
		struct.pack('>B',database_compatibility_number),
		struct.pack('>H',length)
		]

	for byte in command: # append command
		thHDR += [struct.pack('>B',byte)]

	return b"".join(thHDR)

def strToBin(s):
	return ''.join('{0:08b}'.format(ord(b),'b') for b in s)
#start socket
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)	#allow address to be reused after improper close
sock.bind(('', udp_port))

## RADAR Configs
if sys.argv[3] == 'o1':
	cfg_msg = [0x00, 0x02, 0x00, 0x00, 0xFD, 0x20, 0x80, 0x00, 0x08, 0x84, 0x01, 0x00] # o + q + d=260m + 0dB
if sys.argv[3] == 'o2':
	cfg_msg = [0x00, 0x02, 0x00, 0x00, 0xFD, 0x20, 0x80, 0x00, 0x08, 0x8C, 0x01, 0x00] # o + q + e + d=260m + 0dB
if sys.argv[3] == 'c3':
	cfg_msg = [0x00, 0x02, 0x00, 0x00, 0xFD, 0x20, 0x80, 0x00, 0x10, 0x84, 0x01, 0x00] # c + q + d=260m + 0dB


if sys.argv[3] == 'o4':
	cfg_msg = [0x00, 0x02, 0x00, 0x00, 0xFD, 0x20, 0x80, 0x00, 0x08, 0x80, 0x01, 0x00] # o + d=260m + 0dB
if sys.argv[3] == 'c5':
	cfg_msg = [0x00, 0x02, 0x00, 0x00, 0xFD, 0x20, 0x80, 0x00, 0x10, 0x80, 0x01, 0x00] # c + d=260m + 0dB

if sys.argv[3] == 'cq1960':
	cfg_msg = [0x00, 0x02, 0x00, 0x00, 0xFD, 0x18, 0x80, 0x00, 0x10, 0x84, 0x01, 0x00] # cluster + dMAX=196m + 0dB

if sys.argv[3] == 'cq1969':
	cfg_msg = [0x00, 0x02, 0x00, 0x00, 0xFD, 0x18, 0x80, 0x00, 0x70, 0x84, 0x01, 0x00] # cluster + dMAX=196m + -9dB

if sys.argv[3] == 'c1969':
	cfg_msg = [0x00, 0x02, 0x00, 0x00, 0xFD, 0x18, 0x80, 0x00, 0x70, 0x80, 0x01, 0x00] # cluster + dMAX=196m + -9dB
if sys.argv[3] == 'c1960':
	cfg_msg = [0x00, 0x02, 0x00, 0x00, 0xFD, 0x18, 0x80, 0x00, 0x10, 0x80, 0x01, 0x00] # cluster + dMAX=196m + 0dB
if sys.argv[3] == 'c2609':
	cfg_msg = [0x00, 0x02, 0x00, 0x00, 0xFD, 0x20, 0x80, 0x00, 0x70, 0x80, 0x01, 0x00] # cluster + dMAX=260m + -9dB
if sys.argv[3] == 'c2600':
	cfg_msg = [0x00, 0x02, 0x00, 0x00, 0xFD, 0x20, 0x80, 0x00, 0x10, 0x80, 0x01, 0x00] # cluster + dMAX=260m + 0dB

if sys.argv[3] == 'onoq':
	cfg_msg = [0x00, 0x02, 0x00, 0x00, 0xFD, 0x18, 0x80, 0x00, 0x68, 0x80, 0x01, 0x00] # object + dMAX=196m + -9dB

#Filters - OBJECT
if sys.argv[3] == 'o8tar':
	cfg_msg = [0x02, 0x02, 0x00, 0x00, 0x86, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00] #fil_msg0: 8 targets
if sys.argv[3] == 'o86tar':
	cfg_msg = [0x02, 0x02, 0x00, 0x00, 0x86, 0x00, 0x00, 0x00, 0x38, 0x00, 0x00, 0x00] #fil_msg1: 86 targets
if sys.argv[3] == 'o100tar':
	cfg_msg = [0x02, 0x02, 0x00, 0x00, 0x86, 0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00] #fil_msg1: 100 targets
if sys.argv[3] == 'o2dB':
	cfg_msg = [0x02, 0x02, 0x00, 0x00, 0xAE, 0x08, 0x20, 0x0F, 0xCD, 0x00, 0x00, 0x00] #fil_msg2: Min 2dBsm

if sys.argv[3] == 'onotar':
	cfg_msg = [0x02, 0x02, 0x00, 0x00, 0x82, 0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00] #fil_msg1: no target filter
if sys.argv[3] == 'onodB':
	cfg_msg = [0x02, 0x02, 0x00, 0x00, 0xAA, 0x08, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00] #fil_msg2: no dB filter


#Filters - CLUSTER
if sys.argv[3] == 'c8tar':
	cfg_msg = [0x02, 0x02, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00] #fil_msg0: 8 targets
if sys.argv[3] == 'c86tar':
	cfg_msg = [0x02, 0x02, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x38, 0x00, 0x00, 0x00] #fil_msg1: 86 targets
if sys.argv[3] == 'c100tar':
	cfg_msg = [0x02, 0x02, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00] #fil_msg1: 100 targets
if sys.argv[3] == 'c2dB':
	cfg_msg = [0x02, 0x02, 0x00, 0x00, 0x2E, 0x08, 0x20, 0x0F, 0xCD, 0x00, 0x00, 0x00] #fil_msg2: Min 2dBsm

if sys.argv[3] == 'cnodB':
	cfg_msg = [0x02, 0x02, 0x00, 0x00, 0x2A, 0x80, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00] #fil_msg2: no dB filter
if sys.argv[3] == 'cnotar':
	cfg_msg = [0x02, 0x02, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00] #fil_msg1: no target filter
if sys.argv[3] == 'filters':
	cfg_msg = [0x02, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00] #fil_msg1: no target filter

if sys.argv[3] !='print':
	data = addThalesProtocol(cfg_msg)
	crc = crc16(data)
	data += chr(crc >> 8)      # crc msb
	data += chr(crc & 0xff)    # crc lsb
	sock.sendto(data, (ip_addr, dst_port))
	print '\n'

#######-----------------------------------------------########

while True:
	[canIDint, db, m_sen, time_can] = readRadar()
	if canIDint == 0x201 and sys.argv[3] == 'print':
		print 'm_sen:	',m_sen
		print 'ReadNVM:	',int(db[6:7][::-1],2)
		print 'WriteNVM:	',int(db[7:8][::-1],2)
		print 'MaxDistance:	',2*int((db[22:24]+db[8:16])[::-1],2),'m'
		print 'PowerCfg:	',-3*int((db[39:40]+db[24:26])[::-1],2),'dB'
		print '(Obj:1, Clu:2):	',int((db[42:44])[::-1],2)
		print 'Quality:	',int((db[44:45])[::-1],2)
		print 'Extended:	',int((db[45:46])[::-1],2)
		print '\n'

	if canIDint == 0x203:
		nClusterFil = int(db[3:8][::-1],2)
		nObjectFil = int(db[11:16][::-1],2)
		print 'Clu:', nClusterFil, ' and  Obj:', nObjectFil

	if canIDint == 0x204:
		filType = int(db[7:8][::-1],2)
		filInd = int(db[3:7][::-1],2)
		filAct = int(db[2:3][::-1],2)
		filMin = int(((db[16:24]+db[8:12])[::-1]),2)
		filMax = int(((db[32:40]+db[24:28])[::-1]),2)
		print filType, filInd, filAct, filMin, filMax
		print '\n'

	if canIDint == 0x600 and sys.argv[3][0]== 'c':
		nearTar = int(db[0:8][::-1],2)
		farTar = int(db[8:16][::-1],2)
		print ('near:',nearTar,'far:', farTar)
		# print '\n'

	if canIDint == 0x60a and sys.argv[3][0]== 'o':
		numTar = int(db[0:8][::-1],2)
		db = int(db[56:][::-1],2)*0.5
		print 'numTar:', numTar
		# print '\n'

	if canIDint == 0x60b and sys.argv[3][0]== 'o':
		velL = Bits(bin=((db[46:48]+db[32:40])[::-1]))
		velLong = ((velL).uint)*0.25 - 128.0		# longitudinal Doppler Velocity, m/s
		print 'vel:', velL, velLong
		# print '\n'
