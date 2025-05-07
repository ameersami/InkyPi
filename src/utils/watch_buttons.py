import RPi.GPIO as GPIO
from threading import Thread

class Worker(Thread):
    BUTTONS = [29, 31, 36, 18]
    LABELS = ["A", "B", "C", "D"]

    def __init__(self, increment, decrement):
        Thread.__init__(self)
        print('The button watcher has started')
        self._end_function = False
        self.increment = increment
        self.decrement = decrement
        
        # Setup GPIO
        GPIO.setmode(GPIO.BOARD)  # Use the physical pin numbering
        for button in self.BUTTONS:
            GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set each pin as input with pull-up resistors
            GPIO.add_event_detect(button, GPIO.FALLING, callback=self.handle_button, bouncetime=200)  # Falling edge detection

    def stop(self):
        self._end_function = True
        GPIO.cleanup()  # Clean up the GPIO settings when done

    def run(self):
        while not self._end_function:
            pass

    def handle_button(self, channel):
        try:
            index = self.BUTTONS.index(channel)
            gpio_number = self.BUTTONS[index]
            label = self.LABELS[index]

            print(f"Button press detected on GPIO #{gpio_number} label: {label}")
            
            if gpio_number == 29:
                self.increment()
            elif gpio_number == 31:
                self.decrement()
        except Exception as e:
            # assuming you want to log errors (you'd need a logger, though)
            print(f"Failed to process button press: {str(e)}")
            raise RuntimeError("Failed to process button press.")
