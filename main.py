from flask import Flask, render_template  # to run Flask
import RPi.GPIO as GPIO
import motor
import audio

# define pins
left_sensor_pin = 14
middle_sensor_pin = 15
right_sensor_pin = 18

start_button_pin = 26
left_button_pin = 23
right_button_pin = 24

# set gpio mode
GPIO.setmode(GPIO.BCM)

# set up all pins
GPIO.setup(start_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(left_sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(middle_sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(right_sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# create a Flask objec called app
app = Flask(__name__)


# config variables
turn_size = 250  # grootte van de hoek als hij 90 graden draait
sensor_check_interval = 1  # hoe vaak de sensor gecontrolleerd wordt, kleiner is vaker
drive_before_turn_duration = 120  # hoe ver de kart rechtdoor rijdt voor een turn
check_crosspoint_check_turn = 80  # hoe ver de kart moet draaien om te controloren of er een kruispunt is
max_correction = 100  # de grootte van de hoek die maximaal gedraaid mag worden bij een correctie
correction_fault_continue_length = 10  # hoe ver de kart moet doorrijden wanneer over de max_correction is heengegaan
reverse_after_turn_length = 30  # hoe ver achteruit gereden moet worden bij de turn
max_white_length = 150  # hoe ver de kart rechtdoor mag rijden over wit voordat er gezocht wordt naar de lijn
drive_when_crosspoint_center = 80  # hoe ver de kart rechtdoor moet rijden wanneer deze rechtdoor over een crossing gaat
level_6 = False

# ------------- END OF SETUP -----------------

manual_direction = "center"
past_crossing = 0
stopped = True


# render de homepage als die geopend wordt
@app.route("/")
def home():
	return render_template('main.html')


@app.route("/midden")
def route_midden():
	print("Start driving, no direction given")
	global stopped

	stopped = False

	audio.play("midden")
	drive()


@app.route("/links")
def route_links():
	print("Start driving, direction given: left")
	global manual_direction
	global stopped

	manual_direction = "left"
	stopped = False

	audio.play("links")
	drive()


@app.route("/rechts")
def route_rechts():
	print("Start driving, direction given: right")

	global manual_direction
	global stopped

	manual_direction = "right"
	stopped = False

	audio.play("rechts")
	drive()


# rij rechtdoor en check sensoren
def drive():	
	# rijdt totdat sensor_check_interval bereikt is
	while (stopped is False):
		i = 0
		while (i < sensor_check_interval):
			motor.left_forward()
			motor.right_forward()
			i += 1
		sensor_check()


def sensor_check():
	if (GPIO.input(left_sensor_pin) == 0 and GPIO.input(middle_sensor_pin) == 1 and GPIO.input(right_sensor_pin) == 1):
		correct("left")

	if (GPIO.input(left_sensor_pin) == 1 and GPIO.input(middle_sensor_pin) == 1 and GPIO.input(right_sensor_pin) == 0):
		correct("right")

	if (GPIO.input(left_sensor_pin) == 0 and GPIO.input(middle_sensor_pin) == 0 and GPIO.input(right_sensor_pin) == 1):
		check_crosspoint()
		#turn("left")

	if (GPIO.input(left_sensor_pin) == 1 and GPIO.input(middle_sensor_pin) == 0 and GPIO.input(right_sensor_pin) == 0):
		check_crosspoint()
		#turn("right")

	if (GPIO.input(left_sensor_pin) == 0 and GPIO.input(middle_sensor_pin) == 0 and GPIO.input(right_sensor_pin) == 0):
		crossing_found()

	if (level_6 is True):
		if (GPIO.input(left_sensor_pin) == 1 and GPIO.input(middle_sensor_pin) == 1 and GPIO.input(
				right_sensor_pin) == 1):
			drive_white()


# rijdt totdat er weer een lijn gevonden is
def drive_white():
	# rijdt totdat sensor_check_interval bereikt is
	i = 0
	while (i < max_white_length and GPIO.input(left_sensor_pin) == 1 and GPIO.input(middle_sensor_pin) == 1 and GPIO.input(right_sensor_pin) == 1):
		motor.left_forward()
		motor.right_forward()
		i += 1

	if (i >= max_white_length):
		correct("right")
		correct("left")


# correct the kart to a direction
def correct(correct_direction):
	print("Correcting " + correct_direction)

	correction_count = 0
	line_found = False

	# corrigeer totdat lijn weer in het midden is of dat de lijn kwijt is
	while (line_found is False and correction_count < max_correction):
		# draai allebei de wielen de tegengestelde kant op
		if (correct_direction == "right"):
			motor.left_forward()
			motor.right_reverse()
		if (correct_direction == "left"):
			motor.right_forward()
			motor.left_reverse()
		
		# kijkt of de kart weer op de lijn zit
		if (GPIO.input(left_sensor_pin) == 1 and GPIO.input(middle_sensor_pin) == 0 and GPIO.input(right_sensor_pin) == 1):
			line_found = True
			
		correction_count += 1

	if (correction_count >= max_correction):
		# weer terug draaien
		print("Line not found, turning back")
		while correction_count > 0:
			if (correct_direction == "right"):
				motor.left_reverse()
				motor.right_forward()
			if (correct_direction == "left"):
				motor.right_reverse()
				motor.left_forward()

			correction_count -= 1
		
		i = 0
		while (i < correction_fault_continue_length):
			motor.left_forward()
			motor.right_forward()
			i += 1

			
def check_crosspoint():
	print("Checking crosspoint")
	i = 0
	crossing_found_check = False
	
	if (GPIO.input(left_sensor_pin) == 0 and GPIO.input(middle_sensor_pin) == 0 and GPIO.input(right_sensor_pin) == 1):
		while i < check_crosspoint_check_turn:
			motor.right_forward()
			i += 1
			if (GPIO.input(left_sensor_pin) == 0 and GPIO.input(middle_sensor_pin) == 0 and GPIO.input(right_sensor_pin) == 0):
				crossing_found_check = True
				crossing_found()
		
		if (crossing_found_check == False):
			print("No crossing found")
			print("Turning back")
			i = 0
			while i < check_crosspoint_check_turn:
				motor.right_reverse()
				i += 1
			turn("left")
					
	if (GPIO.input(left_sensor_pin) == 1 and GPIO.input(middle_sensor_pin) == 0 and GPIO.input(right_sensor_pin) == 0):
		while i < check_crosspoint_check_turn:
			motor.left_forward()
			i += 1
			if (GPIO.input(left_sensor_pin) == 0 and GPIO.input(middle_sensor_pin) == 0 and GPIO.input(right_sensor_pin) == 0):
				crossing_found_check = True
				crossing_found()
				
		if (crossing_found_check is False):
			print("No crossing found")
			print("Turning back")
			i = 0
			while i < check_crosspoint_check_turn:
				motor.left_reverse()
				i += 1
			turn("right")


# draai de kart een richting op
def turn(direction):
	print("Turning 90 degrees " + direction)

	i = 0
	# rij een stuk rechtdoor zodat de kart de weg niet kwijtraakt
	while (i < drive_before_turn_duration):
		motor.left_forward()
		motor.right_forward()
		i += 1

	i = 0
	if (direction == "left"):
		audio.play("links")
		while (i < turn_size):
			motor.right_forward()
			motor.left_reverse()
			i += 1
	if (direction == "right"):
		audio.play("rechts")
		while (i < turn_size):
			motor.left_forward()
			motor.right_reverse()
			i += 1

	i = 0
	while (i < reverse_after_turn_length):
		motor.left_reverse()
		motor.right_reverse()
		i += 1

	
def crossing_found():
	print("Crossing found")
	global past_crossing
	if (past_crossing == 0):
		past_crossing = 1
		audio.play("kruispunt")
		if (manual_direction != "center"):
			turn(manual_direction)
		else:
			i = 0
			while (i < drive_when_crosspoint_center):
				motor.left_forward()
				motor.right_forward()
				i += 1
	else:
		audio.play("einde")
		print("Already crossed. Shutting down")
		global stopped
		stopped = True
		GPIO.cleanup()


if __name__ == "__main__":
	# have the local host server listen on port 8085
	app.run(host='0.0.0.0', port=8085, debug=False)  # if permission denied; change port
