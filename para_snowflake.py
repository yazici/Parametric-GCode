#Parametric GCode Star
#
# by Dave Menninger
#
#Generates a six pointed star in GCode.
#Goal is to generate snowflakes algorithmically.
#
#This code is derived from Allan Ecker's
#source: http://www.thingiverse.com/thing:849
#
#License: CC-BY-SA

#Import the needed libraries
import math, random


#Rounding function
# Input: num=int, float, or string; r=int  
# Output: string  
def myRound(num, r=0):  
	if type(num) is str:  
		num = float(num)  
	num += 0.5/(10**r)  
	if r == 0:  
		return str(int(num))  
	else:
		num = str(num)  
		return num[:num.find('.')+r+1]

#sG1 Code Object
class G1Code:
	def __init__(self, X=0, Y=0, Z=0, F=0):
		self.X = X
		self.Y = Y
		self.Z = Z
		self.F = F

	def __str__(self):
		#Added rounding
		string = "G1 X" + myRound(self.X,2) + " Y" + myRound(self.Y,2) + " Z" + myRound(self.Z,2) + " F" + str(self.F)
		return string

	#Rotate the XY point of the GCode
	def rotate(self, Theta):
		OldX = self.X
		OldY = self.Y
		self.X = OldX * math.cos(Theta) - OldY * math.sin(Theta)
		self.Y = OldX * math.sin(Theta) + OldY * math.cos(Theta)

	#Add relative moves
	def relative_move(self, XMove, YMove):
		OldX = self.X
		OldY = self.Y
		self.X = OldX + XMove
		self.Y = OldY + YMove

	#Clone Method
	def Clone(self):
		CloneCode = G1Code(self.X, self.Y, self.Z, self.F)
		return CloneCode

#List of G1Codes
class myPolyLine:
	def __init__(self):
		self.listofcodes = []
		
	def __str__(self):
		string_output = ""
		for gcode in self.listofcodes:
			string_output += str(gcode) + "\n"
		return string_output
		
	#add a single G1Code to the list
	def append(self,gcode):
		self.listofcodes.append(gcode)
		
	#add another myPolyLine to the end of this myPolyLine
	def extend(self,polyline):
		for gcode in polyline.listofcodes:
			self.listofcodes.append(gcode.Clone())
			
	#method to make a clone of the myPolyLine
	def Clone(self):
		ClonePolyLine = myPolyLine()
		for gcode in self.listofcodes:
			ClonePolyLine.append(gcode.Clone())
		return ClonePolyLine
		
	#rotate each individual G1Code within
	def rotate(self,angle):
		for gcode in self.listofcodes:
			gcode.rotate(angle)
			
	#mirror the list of G1Codes around the x axis
	#this may be a counter-intuitive name - rename to mirrorY?
	def mirrorX(self):
		for gcode in self.listofcodes:
			gcode.Y = -1*(gcode.Y)
			
	#reverse the order of the list of G1Codes
	def reverse(self):
		self.listofcodes.reverse()
		
	#bump whole list of G1Codes up in the z direction
	def bumpZ(self, layer_thickness):
		for gcode in self.listofcodes:
			gcode.Z = gcode.Z + layer_thickness


filename = "snowflake.gcode"

#Open the output file and paste on the "headers"
FILE = open(filename,"w")

#make half an arm with "spikes"
arm_length = 20.0
arm_thickness = 1.0
#num_spikes = 4
num_spikes = random.randint(2,5)
gap_size = (arm_length/num_spikes)/2.0
spacer = 0.5

SpikyArm = myPolyLine()
ThisGCode = G1Code(X=arm_thickness, Y=arm_thickness/2.0, Z=1.11, F=1500)
SpikyArm.append(ThisGCode)

for spike_n in range(0,num_spikes):
	#spike_length = arm_length/2.0
	spike_length = random.random()*(arm_length/2.0)
	x1 = spacer + gap_size*((spike_n*2))
	y1 = arm_thickness/2.0
	x2 = spacer + x1 + spike_length*math.cos(math.radians(30.0))
	y2 = spike_length*math.sin(math.radians(30.0))
	x3 = spacer + x1 + gap_size
	y3 = arm_thickness/2.0
	ThisGCode = G1Code(X=x1, Y=y1, Z=1.11, F=1500)
	SpikyArm.append(ThisGCode)
	ThisGCode = G1Code(X=x2, Y=y2, Z=1.11, F=1500)
	SpikyArm.append(ThisGCode)
	ThisGCode = G1Code(X=x3, Y=y3, Z=1.11, F=1500)
	SpikyArm.append(ThisGCode)

ThisGCode = G1Code(X=arm_length, Y=arm_thickness/2.0, Z=1.11, F=1500)
SpikyArm.append(ThisGCode)

#make a mirror image of the first half of the arm
otherHalf = SpikyArm.Clone()
otherHalf.mirrorX()
otherHalf.reverse()

#make a pointy tip
ThisGCode = G1Code(X=arm_length+(arm_length/10.0),Y=0,Z=1.11, F=1500)

#join em together
SpikyArm.append(ThisGCode)
SpikyArm.extend(otherHalf)

#join together 6 rotated copies of the spiky arm
ThisGCodeStar = myPolyLine()
for a in range(6):
	SpikyArm.rotate(math.radians(-60))
	ThisGCodeStar.extend(SpikyArm)

FILE.writelines(str(ThisGCodeStar)) #output the whole snowflake (one layer)
FILE.writelines("M103\n")

z_steps = 7
layer_thickness = 0.35

for z_step in range(z_steps):
	ThisGCodeStar.bumpZ(layer_thickness)
	FILE.writelines("M101\n")
	FILE.writelines(str(ThisGCodeStar))
	FILE.writelines("M103\n")

ThisGCode.Z = ThisGCode.Z + 10
FILE.writelines(str(ThisGCode)+ "\n")
FILE.writelines("M104 S0\n")

FILE.close