import RPi.GPIO as GPIO
import time
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class FrontControl(threading.Thread):
	
	daemon = True
	
	CONTROL_PIN = 17
	PWM_FREQ = 50
	STEP=15
	
	right_max = 95
	left_max = 15
	center = 60
	
	pwm = None

	def __init__(self):
		threading.Thread.__init__(self)
		GPIO.setup(self.CONTROL_PIN, GPIO.OUT)
		self.pwm = GPIO.PWM(self.CONTROL_PIN, self.PWM_FREQ)
		self.pwm.start(0)
		
	def run(self):
		while True:
			time.sleep(1)
	
	def angle_to_duty_cycle(self, angle=0):
		duty_cycle = (0.05 * self.PWM_FREQ) + (0.19 * self.PWM_FREQ * angle / 180)
		return duty_cycle
		
	def change_angle(self, percentage):
		#dc = self.angle_to_duty_cycle(percentage*(self.right_max-self.left_max)+self.left_max)
		if percentage>=0.5:
			angle = (percentage-0.5)*(self.right_max-self.center)*2+self.center
		else:
			angle = self.center-(0.5-percentage)*(self.center-self.left_max)*2
		dc = self.angle_to_duty_cycle(angle)
		self.pwm.ChangeDutyCycle(dc)
		
	def angle_test(self):
		self.change_angle(0)
		time.sleep(1)
		self.change_angle(1)
		time.sleep(1)
		change_angle(0.5)
		time.sleep(1)
		

class RearControl(threading.Thread):
	
	daemon = True
	
	MOTOR_CONTROL_PIN1 = 22
	MOTOR_CONTROL_PIN2 = 23
	MOTOR_PWM_PIN = 24
	
	MOTER_PWM_FREQ = 1000
	
	motor_pwm = None
	
	duty_cycle_max = 50
	
	
	def __init__(self):
		threading.Thread.__init__(self)
		GPIO.setup(self.MOTOR_CONTROL_PIN1, GPIO.OUT)
		GPIO.setup(self.MOTOR_CONTROL_PIN2, GPIO.OUT)
		GPIO.setup(self.MOTOR_PWM_PIN, GPIO.OUT)
		self.motor_pwm = GPIO.PWM(self.MOTOR_PWM_PIN, self.MOTER_PWM_FREQ)
		self.motor_pwm.start(0)
		self.set_forward()
		#self.set_reverse()
	
	def run(self):
		while True:
			time.sleep(1)
		
	def set_forward(self):
		GPIO.output(self.MOTOR_CONTROL_PIN1, False)
		GPIO.output(self.MOTOR_CONTROL_PIN2, True)
		
	def set_reverse(self):
		GPIO.output(self.MOTOR_CONTROL_PIN1, True)
		GPIO.output(self.MOTOR_CONTROL_PIN2, False)
	
	def set_stop(self):
		GPIO.output(self.MOTOR_CONTROL_PIN1, False)
		GPIO.output(self.MOTOR_CONTROL_PIN2, False)
		
	def set_speed(self,percentage):
		dc = self.duty_cycle_max*percentage
		self.motor_pwm.ChangeDutyCycle(dc)
		
	def move_test(self):
		self.set_speed(0)
		time.sleep(1)
		
		#self.set_forward()
		#self.set_speed(0.5)
		#time.sleep(2)
		#self.set_speed(0)
		#time.sleep(1)
		
		
		self.set_reverse()
		self.set_speed(0.5)
		time.sleep(2)
		self.set_speed(0)
		time.sleep(1)
		
		self.set_stop()
		time.sleep(2)
		
		

if __name__ == '__main__':
	
	front_control = FrontControl()
	#front_control.angle_test()
	rear_control = RearControl()
	rear_control.move_test()
	while True:
		time.sleep(1)
	
		
	
