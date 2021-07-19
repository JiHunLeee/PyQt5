import sys
import RPi.GPIO as GPIO
import time
from PyQt5.QtWidgets import *
from PyQt5 import uic 
from PyQt5.QtCore import *

pinTrigger = 0
pinEcho = 1
piezo = 13
servomoter = 17
led = 20
led2 = 21


min = 2
max = 10.5


GPIO.setmode(GPIO.BCM)
GPIO.setup(pinTrigger, GPIO.OUT)
GPIO.setup(pinEcho, GPIO.IN)
GPIO.setup(piezo, GPIO.OUT)
GPIO.setup(servomoter, GPIO.OUT)
GPIO.setup(led,GPIO.OUT)
GPIO.setup(led2,GPIO.OUT)

GPIO.output(led,False)
GPIO.output(led2,False)

pwm2 = GPIO.PWM(servomoter, 50)
pwm2.start(min)

pwm = GPIO.PWM(piezo, 1.0)

melody = [293, 391, 493, 587, 587, 523, 493, 440, 493, 391, 493,
 587, 783, 783, 783, 880, 693, 659, 698, 440, 554, 698, 880, 783,
  698, 659, 698, 783, 698, 659, 587, 523, 493, 523, 587, 523, 391,
   440]


class Thread(QThread):
	threadEvent = pyqtSignal(int)
	def __init__(self, parent = None):
		super().__init__(parent)
		self.n=0
		self.isRun = False

	def run(self):
		pwm.start(50.0)
		while self.isRun:
			pwm.ChangeFrequency(melody[self.n])
			time.sleep(0.2)
			self.n += 1
			if self.n >= 38:
				self.isRun= False
				pwm.stop()
				self.n = 0 

class Thread2(QThread):
	threadUltra = pyqtSignal(float)
	def __init__(self, parent = None):
		super().__init__(parent)
		self.distance = 0.0
		self.isRun = False

	def run(self):
		while self.isRun:
			self.distance = self.measure()
			self.threadUltra.emit(self.distance)
#			self.ui.label_5.setText("%.2fcm"%distance)
			time.sleep(0.5)
			if (self.distance <= 5.00):
				pwm.start(50.0)
				pwm.ChangeFrequency(melody[7])
				print("너무 가깝습니다")
				time.sleep(0.5)
				pwm.stop()
				time.sleep(0.1)
			elif (5 <  self.distance <= 10):
			#elif (distance <= 10) << 이게 좀 더 맞는말
				pwm.start(50.0)
				pwm.ChangeFrequency(melody[7])
				print("가깝습니다")
				time.sleep(0.5)
				pwm.stop()
				time.sleep(1)
			elif (10 <  self.distance <= 15):
				pwm.start(50.0)
				pwm.ChangeFrequency(melody[7])
				print("여유가 많습니다")
				time.sleep(0.5)
				pwm.stop()
				time.sleep(1.5)
			

	def measure(self):
		GPIO.output(pinTrigger,True)
		time.sleep(0.0001)
		GPIO.output(pinTrigger, False)
		start = time.time()
		while GPIO.input(pinEcho) == False:
			start = time.time()
		while GPIO.input(pinEcho) == True:
			stop = time.time()

		elapsed = stop - start
		distance = (elapsed * 19000)/2
		return distance

class myWindow(QWidget):
	def __init__(self,parent = None):
		super().__init__(parent)
		self.ui = uic.loadUi("Project.ui",self)
		self.ui.show()
		self.th = Thread(self)
		self.th.daemon = True
		self.th.threadEvent.connect(self.threadEvenHandler)
		self.y = Thread2(self)
		self.y.daemon = True
		self.y.threadUltra.connect(self.threadEvenHandler1)

	def slot_on(self):
		self.ui.label.setText("LED ON!!")
		GPIO.output(led,True)
	def slot_off(self):
		self.ui.label.setText("LED OFF!!")
		GPIO.output(led,False)
	def slot_on2(self):
		self.ui.label_3.setText("LED ON!!")
		GPIO.output(led2,True)
	def slot_off2(self):
		self.ui.label_3.setText("LED OFF!!")
		GPIO.output(led2,False)
	def slot_piezo_on(self):

		if not self.th.isRun:
			self.th.isRun = True
			self.th.start()


	def slot_piezo_off(self):

		if self.th.isRun:
			self.th.isRun = False
		pwm.stop()

	def threadEvenHandler(self, n):
		pass
	def threadEvenHandler1(self, distance):
		self.ui.label_5.setText("%.2fcm"%distance)

	def slot_ultra_on(self):
		if not self.y.isRun:
			self.y.isRun = True
			self.y.start()

	def slot_ultra_off(self):
		if self.y.isRun:
			self.y.isRun= False

	def slot_moter_up(self):

		moter_dial = self.ui.lcdNumber.value()+5
		pwm2.ChangeDutyCycle(12) #(moter_dial /18)+6)

		#self.ui.lcdNumber.display(moter_dial) 설정한값을 초과해서 넘어가게됨
		self.ui.horizontalSlider.setValue(moter_dial)



	def slot_moter_down(self):

		moter_dial = self.ui.lcdNumber.value()-5
		if moter_dial < 0:
			pass
		else:
			pwm2.ChangeDutyCycle(moter_dial/18)
			self.ui.horizontalSlider.setValue(moter_dial)


	def slot_moterbar(self):
		moter_dial = self.ui.lcdNumber.value()
		avg= min + (((max-min)/180)*moter_dial)
		pwm2.ChangeDutyCycle(avg)


	def slot_moterdial(self):

		moter_dial = self.ui.lcdNumber.value()
		avg= min + (((max-min)/180)*moter_dial)
		pwm2.ChangeDutyCycle(avg)


	def slot_exit(self):
		print("Bye")
		pwm.ChangeDutyCycle(0.0)
		GPIO.cleanup()
		sys.exit()

#	def slot_buser_on(self):
#		self.ui.label_2.setText("buser on!!")

if __name__ == "__main__":
	app = QApplication(sys.argv)
	myapp = myWindow()
	app.exec_()
