from Tkinter import *
import sabertooth
import autopy
from os import system
from platform import system as platform

SCREEN_TOP_BAR_HEIGHT = 23
WINDOW_TOP_BAR_HEIGHT = 22
MARGIN = 20

# brew install libpng
# CFLAGS="-Wno-return-type" pip install git+https://github.com/potpath/autopy.git

class Joystick:
	def __init__(self, s, r):
		self.lockXPosition = False
		self.lockYPosition = False
		self.steering = False

		self.sideLength = s
		self.circleRadius = r

		self.circleInitX = self.sideLength / 2
		self.circleInitY = self.sideLength / 2
		self.circleMouseOffsetX = 0
		self.circleMouseOffsetY = 0
		self.prevCirclePosX = 0
		self.prevCirclePosY = 0

		self.root = Tk()
		self.root.wm_title("Joystick")

		# Mac OS X hack to bring the window in front of the terminal
		if platform() == 'Darwin':  
			system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

		self.screenWidth = self.root.winfo_screenwidth()
		self.screenHeight = self.root.winfo_screenheight()
		self.root.geometry('%dx%d+%d+%d' % (
			self.sideLength, 
			self.sideLength, 
			0,#self.screenWidth / 2 - self.sideLength / 2, 
			0)#self.screenHeight / 2 - self.sideLength / 2)
		)
		self.topLeftX = self.root.winfo_rootx()
		self.topLeftY = self.root.winfo_rooty()
		# autopy.mouse.smooth_move(1,1)

		self.canvas = Canvas(
			self.root, 
			width=self.sideLength, 
			height=self.sideLength, 
			background="gray",
			highlightthickness=0
		)
		self.yAxis = self.canvas.create_line(
			self.circleInitX,
			0,
			self.circleInitX,
			self.sideLength,
			fill="red",
			dash=(2,2)
		)
		self.xAxis = self.canvas.create_line(
			0,
			self.circleInitY,
			self.sideLength,
			self.circleInitY,
			fill="red",
			dash=(2,2)
		)
		self.circle = self.canvas.create_oval(
			self.circleInitX - self.circleRadius,
			self.circleInitY - self.circleRadius,
			self.circleInitX + self.circleRadius,
			self.circleInitY + self.circleRadius,
			fill="black"
		)

		self.canvas.tag_bind(self.circle, '<ButtonPress-1>', self.onCircleMouseDown) 
		self.root.bind('<B1-Motion>', self.onMouseMove)
		self.root.bind('<ButtonRelease-1>', self.onMouseUp)
		self.root.bind('<KeyPress>', self.onKeyPress)
		self.root.bind('<KeyRelease>', self.onKeyRelease)

		self.canvas.pack()
		self.root.mainloop()

	def onCircleMouseDown(self, event):
		self.steering = True

		self.circleMouseOffsetX = event.x - self.circleInitX
		self.circleMouseOffsetY = event.y - self.circleInitY
		self.prevCirclePosX = self.circleInitX
		self.prevCirclePosY = self.circleInitY

		print "\tLeft\tRight"
		# print "\nmouseDown - ", str(self.circleMouseOffsetX), str(self.circleMouseOffsetY)
	    # print self.prevCirclePosX, self.prevCirclePosY

	def onMouseMove(self, event):
		if self.steering:
			if self.lockXPosition:
				newCirclePosX = self.prevCirclePosX
				newCirclePosY = event.y - self.circleMouseOffsetY
			elif self.lockYPosition:
				newCirclePosY = self.prevCirclePosY
				newCirclePosX = event.x - self.circleMouseOffsetX
			else:
				newCirclePosX = event.x - self.circleMouseOffsetX
				newCirclePosY = event.y - self.circleMouseOffsetY

			if newCirclePosX < 0:
				newCirclePosX = 0
			if newCirclePosY < 0:
				newCirclePosY = 0
			if newCirclePosX > self.sideLength:
				newCirclePosX = self.sideLength
			if newCirclePosY > self.sideLength:
				newCirclePosY = self.sideLength

			self.canvas.move(
				self.circle, 
				newCirclePosX - self.prevCirclePosX,
				newCirclePosY - self.prevCirclePosY
			)

			self.prevCirclePosX = newCirclePosX
			self.prevCirclePosY = newCirclePosY

			m1Speed, m2Speed = sabertooth.convertToMotorSpeeds(newCirclePosX, newCirclePosY, self.sideLength)
			s = "\t" + str(m1Speed) + "\t" + str(m2Speed) + "\r"
			sys.stdout.write("                               \r") # Clear the old line first
			sys.stdout.write(s)
			sys.stdout.flush()

	def onMouseUp(self, event):
		if self.steering:
			self.canvas.move(
				self.circle, 
				self.circleInitX - self.prevCirclePosX, 
				self.circleInitY - self.prevCirclePosY
			)
			self.steering = False

	def onKeyPress(self, event):
		if self.steering and event.keycode in [131330, 131332, 131074, 131076]:
			if event.keycode in [131330, 131074]:
				self.lockXPosition = True
			else:
				self.lockYPosition = True

	def onKeyRelease(self, event):
		if event.keycode in [131330, 131332, 131074, 131076]:
			if event.keycode in [131330, 131074]:
				self.lockXPosition = False
			else:
				self.lockYPosition = False

			if self.steering:
				autopy.mouse.move(
					self.prevCirclePosX + self.root.winfo_rootx(),
					self.prevCirclePosY + self.root.winfo_rooty()
				)
				# When autopy moves the mouse, both a mouseUp then a mouseDown event will fire. This causes
				# some bad things to happen, so I'm just absorbing the next instance of each of these events
				# with a dummy handler then setting it back to the correct handler from within them.
				self.root.bind('<ButtonRelease-1>', self.onNextMouseUp)
				self.canvas.tag_bind(self.circle, '<ButtonPress-1>', self.onNextMouseDown) 

	def onNextMouseUp(self, event):
		self.root.bind('<ButtonRelease-1>', self.onMouseUp)

	def onNextMouseDown(self, event):
		self.canvas.tag_bind(self.circle, '<ButtonPress-1>', self.onCircleMouseDown) 


sc = Joystick(500, 8)
