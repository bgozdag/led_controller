import datetime
import threading
from abc import ABC

def log(output):
    print("{} - {}".format(datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3], output))


class LEDColor(ABC):
    def execute(self):
        log(self.__class__.__name__)


class RedLED(LEDColor):
    def execute(self):
        log("\033[91mRedLED\033[39m")


class BlueLED(LEDColor):
    def execute(self):
        log("\033[94mBlueLED\033[39m")


class GreenLED(LEDColor):
    def execute(self):
        log("\033[92mGreenLED\033[39m")


class ClearLED(LEDColor):
    pass


class LEDState(ABC, threading.Thread):
    def __init__(self) -> None:
        super().__init__()
        self.stop_event = threading.Event()
        self.stop_event.set()
        self.daemon = True

    def start(self):
        if self.is_alive():
            return
        else:
            super().start()

    def run(self):
        self.stop_event.clear()
        log(self.__class__.__name__ + " start")

    def stop(self):
        log(self.__class__.__name__ + " stop")
        ClearLED().execute()


class EcoLEDState(LEDState):
    def __init__(self) -> None:
        super().__init__()

    def run(self):
        super().run()
        while not self.stop_event.is_set():
            RedLED().execute()
            self.stop_event.wait(2.4)
            BlueLED().execute()
            self.stop_event.wait(1.2)

    def stop(self):
        self.stop_event.set()
        super().stop()


class RandomLEDState(LEDState):
    def __init__(self) -> None:
        super().__init__()

    def run(self):
        super().run()
        while not self.stop_event.is_set():
            GreenLED().execute()
            self.stop_event.wait(.5)
            ClearLED().execute()
            self.stop_event.wait(1)

    def stop(self):
        self.stop_event.set()
        super().stop()


class ErrorLEDState(LEDState):
    def __init__(self) -> None:
        super().__init__()

    def run(self):
        super().run()
        RedLED().execute()

    def stop(self):
        super().stop()


class AuthorizedLEDState(LEDState):
    def __init__(self) -> None:
        super().__init__()

    def run(self):
        super().run()
        BlueLED().execute()

    def stop(self):
        super().stop()


class LEDController:

    def __init__(self) -> None:
        self.active_states = []
        self.visible_state = None
        self.states = (
            ErrorLEDState(),
            RandomLEDState(),
            EcoLEDState(),
            AuthorizedLEDState(),
        )

    def activate(self, state):
        if state not in self.active_states:
            self.active_states.append(state)
        self.set_visible()

    def deactivate(self, state):
        if state in self.active_states:
            self.active_states.remove(state)
        self.set_visible()

    def set_visible(self):
        self.active_states.sort(key=lambda x: self.states.index(x))
        log(self.active_states)
        if len(self.active_states) > 0 and not (type(self.visible_state) == type(self.active_states[0])):
            if self.visible_state is not None:
                self.visible_state.stop()
                self.visible_state = None
            self.visible_state = type(self.active_states[0])()
        elif len(self.active_states) == 0:
            self.visible_state.stop()
            self.visible_state = None
        for state in self.states:
            if (type(state) != type(self.visible_state) and not state.stop_event.is_set()):
                state.stop()
        if len(self.active_states) > 0 and not self.visible_state.is_alive():
            self.visible_state.start()


if __name__ == "__main__":
    led_controller = LEDController()
    while True:
        index = int(input()) - 1
        if led_controller.states[index] not in led_controller.active_states:
            led_controller.activate(led_controller.states[index])
        else:
            led_controller.deactivate(led_controller.states[index])
