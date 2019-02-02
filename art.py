#30/1/2019
#this is python 2.7, not python 3
#author: Cabbache
#copyright!
#visit my gallery in the creative server on play.extremecraft.net, /p v gallery

import threading
import time
import math
import sys
import os

from scipy.misc import imread
from minecraft.networking.connection import Connection
from minecraft.networking.packets import PlayerPositionAndLookPacket
from minecraft.networking.packets import PositionAndLookPacket
from minecraft.networking.packets import Packet, clientbound, serverbound
from minecraft.networking.packets.serverbound.play import PlayerBlockPlacementPacket
from minecraft.networking.packets.serverbound.play import HeldItemChangePacket
from minecraft.networking.packets.serverbound.play import ClickWindowPacket
from minecraft.networking.packets.serverbound.play import UseItemPacket
from minecraft.networking.packets.serverbound.play import CreativeInventoryActionPacket
from thread import *

from minecraft.networking.types import (
	Enum, BitFieldEnum, Vector, Position, PositionAndLook
)

#colors = [[[r,g,b],[id]],[[r,g,b],[id]],...]
#values where obtained by averaging the RGB of the image of the texture of the block
colors = [
	#terracotta
	[[209, 178, 161], [159,0]],#white
	[[113,108,137], [159,3]],#light blue
	[[161,83,37], [159,1]],#orange
	[[186,133,35], [159,4]],#yellow
	[[37,22,16],[159,15]],#black
	[[74,59,91],[159,11]],#blue
	[[77,51,35],[159,12]],#brown
	[[86,91,91],[159,9]],#cyan
	[[57,42,35],[159,7]],#gray
	[[76, 83, 42],[159,13]],#green
	[[103, 117, 52],[159,5]],#lime
	[[149, 88, 108],[159,2]],#magenta
	[[161, 78, 78],[159,6]],#pink
	[[118,70,86],[159,10]],#purple
	[[143, 61, 46],[159,14]],#red
	#wool
	[[53,57,157], [35,11]],#blue
	[[21,137,145], [35,9]],#cyan
	[[58,175,217], [35,3]],#light blue
	[[248,197,39], [35,4]],#yellow
	[[240,118,19], [35,1]],#orange
	[[114,71,40], [35,12]],#brown
	[[160,39,34], [35,14]],#red
	[[112,185,25], [35,5]],#lime
	[[237,141,172], [35,6]],#pink
	[[84,109,27], [35,13]],#green
	[[189,68,179], [35,2]],#magenta
	[[121,42,172], [35,10]], #purple
	[[62,68,71], [35,7]],#gray
	[[192,192,192], [35,8]],#light gray
	[[233, 236, 236], [35,0]],#white
	#planks
	[[169, 91, 51],[5,4]],
	[[61, 39, 18],[5,5]],
	[[195, 179, 123],[5,2]],
	[[154, 110, 77],[5,3]],
	[[156, 127, 78],[5,0]],
	[[103, 77, 46],[5,1]],
	#others
	[[0,51,102], [22, 0]],#lapiz
	[[236, 233, 226], [155,0]],#quartz top
	[[218, 210, 158], [24,0]],#sandstone top
	[[239, 251, 251], [80,0]]#snow
]

queue = []
zeroQueue = []
lock = threading.Lock()
exit = False
placement = [0,0,0]
shift = 0.4
sample = 10
isWaiting = False
verbose = False
chatText = ""

#CHANGE THESE
USR="user"
PWD="pass"

pos_look = PlayerPositionAndLookPacket.PositionAndLook()

pos_look_set = threading.Condition(lock)
def updatePosition():
	conn.write_packet(PositionAndLookPacket(
		x		 = pos_look.x,
		feet_y	= pos_look.y,
		z		 = pos_look.z,
		yaw	   = pos_look.yaw,
		pitch	 = pos_look.pitch,
		on_ground = True))

def h_position_and_look(packet):
	with lock:
		packet.apply(pos_look)
		pos_look_set.notify_all()

def same(arr1, arr2):
	if len(arr1) != len(arr2):
		return False
	for x in range(len(arr1)):
		if arr1[x] != arr2[x]:
			return False
	return True

def head(angle):
	pos_look.pitch = (pos_look.pitch + float(angle)) % 360
	print("pitch: " + str(pos_look.pitch))

def holdItem(slotNum):
	heldItem = HeldItemChangePacket()
	heldItem.slot = slotNum
	conn.write_packet(heldItem)

def moveTo(x, y, z, speed):
	distx = pos_look.x - x
	disty = pos_look.y - y
	distz = pos_look.z - z
	distance = distFrom(x,y,z)
	pos_look.x -= speed*(distx/distance)
	pos_look.y -= speed*(disty/distance)
	pos_look.z -= speed*(distz/distance)

def goTo(x,y,z,delay):
		x = float(x) + shift
		y = float(y)
		z = float(z) + shift
		while distFrom(x,y,z) > 0.1:
			moveTo(x, y, z, 0.2)
			time.sleep(delay)#0.0285 this makes significant change

def distFrom(x,y,z):
	distx = x - pos_look.x
	disty = y - pos_look.y
	distz = z - pos_look.z
	return math.sqrt(math.pow(distx, 2) + math.pow(disty, 2) + math.pow(distz, 2))

def place(slotNum, x, y, z):
	holdItem(slotNum)
	place = PlayerBlockPlacementPacket()
	place.location = Position(x, y, z)
	place.face = place.Face.TOP   # See networking.types.BlockFace.
	place.hand = place.Hand.MAIN  # See networking.types.RelativeHand
	place.x = 0
	place.y = 0
	place.z = 0
	conn.write_packet(place)

#calculate the closest coordinate that when map is opened, there is no border, just plot surface
def getClosest(coor):
	sy = math.floor((coor - 64.0)/128.0)
	found = False
	incr = 0
	befI = 0
	while not(found):
		for n in xrange(-150, 150):#brute force, increase range if no solutions found
			for z in xrange(9, 30):
				if 128*(sy+incr) == 90 + (n*158) + z:
					found = True
					break
			if found:
				break
		befI = incr
		incr += 1 if coor > 0 else -1
	closest = 128*(sy+befI) + 64
	return int(closest)

def get128():
	sendChat("/p a")
	time.sleep(0.7)
	sendChat("/p h")
	time.sleep(1)
	goTo(pos_look.x, 70, pos_look.z+3,0.02)
	sendChat("/p delete")
	time.sleep(1)
	sendChat("/p confirm")
	result = 0
	while result == 0:
		closX = getClosest(pos_look.x + (5 if pos_look.x > 0 else -5))
		closZ = getClosest(pos_look.z + (5 if pos_look.z > 0 else -5))
		print("Heading " + str(closX) + ", " + str(closZ))
		goTo(closX, 70, closZ, 0.03)
		print("arrived")
		sendChat("/sethome")
		time.sleep(1)
		sendChat("/p claim")
		result = waitFor(["This plot is already claimed", "You successfully claimed the plot"], 5)
		if result == -1:
			print "result = -1"
			return
		elif result == 0:
			print "plot is claimed"
	time.sleep(1)
	sendChat("/home")
	time.sleep(5)
	sendChat("/p flag set time 5000")

def drawImage(length, width, cont, intell):
	basey = 67
	global exit
	if not(cont):
		if intell and len(im) == 128 and len(im[0]) == 128:
			get128()
		basex = int(math.floor(pos_look.x))
		basez = int(math.floor(pos_look.z))
		start = [0, 0]
		filus = open("Last.txt", "w")
		filus.write("0\n0\n"+str(basex)+"\n"+str(basez))
		filus.close()
	else:
		with open("Last.txt") as filus:
			start = [int(filus.readline()), int(filus.readline())]
			basex = int(filus.readline())
			basez = int(filus.readline())

	pos_look.pitch = 90
	del zeroQueue[:]
	print("starting: " + str(basex) + " " + str(basey) + " " + str(basez))
	oldID = [0,0]
	first = True
	begin = time.time()
	delay = 0.03
	cnt = 0
	for sx in range(start[0], width):
		for sz in range(start[1] if first else 0, length):
			if exit:
				return
			first = False
			inn = False
			x = int(round(float(pos_look.x)))
			y = int(round(float(pos_look.y)))
			z = int(round(float(pos_look.z)))
			zLen = len(zeroQueue)
			while len(zeroQueue) > 0:
				zero = zeroQueue[0]
				inn = True
				goTo(zero[0], basey, zero[2], delay)
				itemID = rgbToBlockID(im[zero[2] - basez][zero[0] - basex])
				getItem(36, itemID)
				place(0, zero[0], y - 3, zero[2])
				zeroQueue.remove(zero)
			if inn:
				getItem(36, oldID)
			newPosX = basex + sx
			newPosZ = (basez + sz) if sx % 2 == 0 else (basez+length-sz-1)
			goTo(newPosX, basey, newPosZ, delay)#delay
			delay += -0.00001 if zLen == 0 else (0.001)#slow down if lagg (getting zeroes)
			colorz = newPosZ - basez
			itemID = rgbToBlockID(im[colorz][sx])
			if not(same(itemID,oldID)):
				getItem(36, itemID)
				oldID[0] = itemID[0]
				oldID[1] = itemID[1]
			if len(queue) > 2:
				print("queue: " + str(len(queue)))
			for j in range(len(queue)):
				try:
					prePlacement = queue[j]
					if time.time() - prePlacement[3] > 5:
						zero = [prePlacement[0], prePlacement[1], prePlacement[2]]
						zeroQueue.append(zero)
						queue.remove(prePlacement)
						print("no Confirmation")
				except:
					pass
			x = int(round(float(pos_look.x)))
			y = int(round(float(pos_look.y)))
			z = int(round(float(pos_look.z)))
			place(0, x, y - 3, z)
			placement = [x,y-3,z, int(time.time())]
			queue.append(placement)
			if cnt == sample:
				cnt = 0
				pos_look.pitch = 90
				spe = time.time() - begin
				begin = time.time()
				spe = float(sample)/spe
				left = float(length*(width - sx) - sz)
				est = left/spe
				est /= 60.0
				perc = 100.0*(1.0 - left/(width*length))
				print("@ %.3f block / s (%f m), del=%f -> %.3f%%" % (spe, est, delay, perc))
				last = open("Last.txt", "w")
				last.write(str(sx) + "\n" + str(sz) + "\n" + str(basex) + "\n" + str(basez))
				last.close()
			cnt += 1
	print("Done.")		

def sendChat(msg):
	packet = serverbound.play.ChatPacket()
	packet.message = msg
	conn.write_packet(packet)

#the closest r,g,b point in 3D space with pythagoras
def rgbToBlockID(rgb_array):
	shortest = 500
	block_id = [0,0]
	for color in colors:
		difR = rgb_array[0] - color[0][0]
		difG = rgb_array[1] - color[0][1]
		difB = rgb_array[2] - color[0][2]
		distance = math.sqrt(pow(difR, 2) + pow(difG, 2) + pow(difB, 2))
		if distance < shortest:
			shortest = distance
			block_id = color[1]
	return block_id

def getItem(slot, item_id):
	item_fetch = CreativeInventoryActionPacket()
	item_fetch.slot = slot #36-44 are main inv
	item_fetch.item_id = item_id[0]
	item_fetch.count = 1
	item_fetch.nbt = 0x00
	item_fetch.col = item_id[1] #do if context is not > 389
	conn.write_packet(item_fetch)

def updater(abc):
	while True:
		time.sleep(0.05)
		if exit:
			sys.exit(0)
		updatePosition()

def update_change(pkt):
	if pkt.block_state_id == 0:
		coords = [pkt.location.x, pkt.location.y, pkt.location.z]
		zeroQueue.append(coords)
		print("recieved 0")#(a block got destroyed)
	for placement in queue:
		if placement[0] == pkt.location.x and placement[1] == pkt.location.y and placement[2] == pkt.location.z:
			queue.remove(placement)

def goCreative():
	with lock:
		pos_look_set.wait()
	print("got position")
	sendChat("/login "+PWD)
	time.sleep(0.5)
	sendChat("/go creative")

def die():
	global exit
	print "lost Connection (wrong password?)"
	exit = True
	sys.exit(0)

def waitFor(chStrings, maxDur):
	global chatText
	global isWaiting
	isWaiting = True
	begin = time.time()
	maxTime = begin+maxDur
	while time.time() < maxTime:
		for string in chStrings:
			if string in chatText:
				isWaiting = False
				chatText = ""
				return chStrings.index(string)
	isWaiting = False
	chatText = ""
	return -1

def print_chat(chat_packet):
	global chatText
	global isWaiting
	if verbose:
		print chat_packet.json_data
	if isWaiting:
		chatText += chat_packet.json_data

def UI(abc):
	global verbose
	global exit
	global chatText
	while not(exit):
		command = raw_input(">> ").split(':')
		action = command[0]
		if action == "ch":
			sendChat(command[1])
		elif action == "place":
			x = int(round(float(pos_look.x)))
			y = int(round(float(pos_look.y)))
			z = int(round(float(pos_look.z)))
			place(0, x, y - int(command[1]), z)
		elif action == "draw":
			if len(command) == 1:
				drawImage(len(im), len(im[0]), False, False)
				continue
			if command[1] == "cont" and os.path.exists("Last.txt"):
				drawImage(len(im), len(im[0]), True, False)
			elif command[1] == "intel":
				drawImage(len(im), len(im[0]), False, True)
		elif action == "discon":
			conn.disconnect()
			posUpdate.stop()
		elif action == "connect":
			conn.connect()
		elif action == "goto":
			goTo(command[1], command[2], command[3], 0.0285)
		elif action == "exit":
			exit = True
			sys.exit(0)
		elif action == "get":
			getItem(0x24, [command[1],0])
		elif action == "head":
			head(command[1])
		elif action == "coords":
			print(str(pos_look.x) + " " + str(pos_look.y) + " " + str(pos_look.z))
			print(str(pos_look.yaw) + " " + str(pos_look.pitch))
		elif action == "verb":
			verbose = not(verbose)
		elif action == "waitfor":
			print str(waitFor([command[1]], 5))
		else:
			print "invalid command"

print("Started")

if not(os.path.isfile("pic.jpg")):
	print("pic.jpg does not exist! Exiting.")
	sys.exit(0)

im = imread("pic.jpg")
print("loaded image (" + str(len(im)) + "x" + str(len(im[0])) + ")")

conn = Connection('play.extremecraft.net', username=USR, handle_exit=die)
conn.register_packet_listener(h_position_and_look, PlayerPositionAndLookPacket)
conn.register_packet_listener(update_change, clientbound.play.BlockChangePacket)
conn.register_packet_listener(print_chat, clientbound.play.ChatMessagePacket)
conn.connect()

goCreative()
thread = threading.Thread(target = UI, args=("a",))
posUpdate = threading.Thread(target = updater, args=("a",))
thread.start()
posUpdate.start()
