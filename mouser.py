import pyautogui
import argparse
import time

class Mouser:
    def __init__(self, delay=5, movement=10):
        self.delay = delay
        self.movement = movement
        pass

    def move_to(self, x, y):
        pyautogui.moveTo(x, y)

    def click(self, x=None, y=None, button='left'):
        if x is not None and y is not None:
            self.move_to(x, y)
        pyautogui.click(button=button)

    def move_mouse_every_n_seconds(self):
        try:
            print("Ctrl+C to stop the program.")
            while True:
                x, y = pyautogui.position()
                time.sleep(self.delay)
                self.move_to(x + self.movement, y+ self.movement)
                time.sleep(self.delay)
                self.click(x, y)
        except KeyboardInterrupt:
            print("Program stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Move mouse periodically to avoid idle.")
    parser.add_argument("--delay", type=float, default=5.0, help="seconds between movements/clicks")
    parser.add_argument("--movement", type=int, default=10, help="pixels to move each step")

    args = parser.parse_args()

    mouser = Mouser(delay=args.delay, movement=args.movement)
    mouser.move_mouse_every_n_seconds()