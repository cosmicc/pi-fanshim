import atexit
import time
from threading import Thread

import plasma
import RPi.GPIO as GPIO

__version__ = '0.0.2'


class FanShim():
    def __init__(self, pin_fancontrol=18, pin_button=17, button_poll_delay=0.05):
        """FAN Shim.

        :param pin_fancontrol: BCM pin for fan on/off
        :param pin_button: BCM pin for button

        """
        self._pin_fancontrol = pin_fancontrol
        self._pin_button = pin_button
        self._poll_delay = button_poll_delay
        self._button_press_handler = None
        self._button_release_handler = None
        self._button_hold_handler = None
        self._button_hold_time = 2.0
        self._t_poll = None

        # My added parameters
        self.pwm_freq = 6
        self.pwm_speed = 70
        self.fan_state = True
        self.pwm_on_speed = self.pwm_speed

        atexit.register(self._cleanup)

        # Original Version DT 06 12 2019
        # GPIO.setwarnings(False)
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(self._pin_fancontrol, GPIO.OUT)

        # My Version
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        # Still need this if want button to work !! BUT if I have this line get errors have not fixed yet
        GPIO.setup(self._pin_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._pin_fancontrol, GPIO.OUT)
        self.pwm_out = GPIO.PWM(self._pin_fancontrol, 1)
        self.pwm_out.start(0)
        self.pwm_out.ChangeFrequency(self.pwm_freq)
        self.pwm_out.ChangeDutyCycle(self.pwm_speed)

        self.__no_heading_yet = True

        plasma.set_clear_on_exit(True)
        plasma.set_light_count(1)
        plasma.set_light(0, 0, 0, 0)

    def log_to_file(self, log_line):
        if self.__no_heading_yet:
            self.__no_heading_yet = False
            self.__log_file = open("/var/log/fanshim.log", 'w')
            self.__log_file.write("Current Temp,Target Temp,CPU Freq,Automatic,Fan State \n")
        self.__log_file.write(log_line)
        self.__log_file.flush()
        return

    def start_polling(self):
        """Start button polling."""
        if self._t_poll is None:
            self._t_poll = Thread(target=self._run)
            self._t_poll.daemon = True
            self._t_poll.start()

    def stop_polling(self):
        """Stop button polling."""
        if self._t_poll is not None:
            self._running = False
            self._t_poll.join()

    def on_press(self, handler=None):
        """Attach function to button press event."""
        def attach_handler(handler):
            self._button_press_handler = handler
            self.start_polling()

        if handler is not None:
            attach_handler(handler)
        else:
            return attach_handler

    def on_release(self, handler=None):
        """Attach function to button release event."""
        def attach_handler(handler):
            self._button_release_handler = handler
            self.start_polling()

        if handler is not None:
            attach_handler(handler)
        else:
            return attach_handler

    def on_hold(self, handler=None):
        """Attach function to button hold event."""
        def attach_handler(handler):
            self._button_hold_handler = handler
            self.start_polling()

        if handler is not None:
            attach_handler(handler)
        else:
            return attach_handler

    def set_hold_time(self, hold_time):
        """Set the button hold time in seconds.

        :param hold_time: Amount of time button must be held to trigger on_hold (in seconds)

        """
        self._button_hold_time = hold_time

    def get_fan(self):
        # Original Version
        """Get current fan state."""
        # return GPIO.input(self._pin_fancontrol)
        # My Version
        return self.fan_state

    def toggle_fan(self):
        """Toggle fan state."""
        # Original Version
        # return self.set_fan(False if self.get_fan() else True)
        # My Version
        return self.set_fan(False if self.get_fan() else True)

    def set_fan(self, status):
        """Set the fan on/off.

        :param fan_state: True/False for on/off

        """
        # Original Version
        #GPIO.output(self._pin_fancontrol, True if fan_state else False)
        # return True if fan_state else False
        # My version
        if status:
            self.pwm_out.ChangeDutyCycle(self.pwm_on_speed)
            self.fan_state = True
        else:
            self.pwm_out.ChangeDutyCycle(0)
            self.fan_state = False

    def set_light(self, r, g, b):
        """Set LED.

        :param r: Red (0-255)
        :param g: Green (0-255)
        :param b: Blue (0-255)

        """
        plasma.set_light(0, r, g, b)
        plasma.show()

    def _cleanup(self):
        self.stop_polling()

    def _run(self):
        self._running = True
        last = 1

        while self._running:
            current = self.get_fan()
            # Transition from 1 to 0
            if last > current:
                self._t_pressed = time.time()
                self._hold_fired = False

                if callable(self._button_press_handler):
                    self._t_repeat = time.time()
                    Thread(target=self._button_press_handler).start()

            if last < current:
                if callable(self._button_release_handler):
                    Thread(target=self._button_release_handler, args=(self._hold_fired,)).start()

            if current == 0:
                if not self._hold_fired and (time.time() - self._t_pressed) > self._button_hold_time:
                    if callable(self._button_hold_handler):
                        Thread(target=self._button_hold_handler).start()
                    self._hold_fired = True

            last = current

            time.sleep(self._poll_delay)
