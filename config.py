from colorama import Fore

# True= after arriving, persons will leave floor
# False= after arriving, persons will stand in queue from the end with new target floor
NORMAL_MODE = False

# Min and max num of possible persons per floor
MAX_PERSONSET = 10
MIN_PERSONSET = 0

# Min and max num of possible floors
MAX_TOTAL_FLOORS = 20
MIN_TOTAL_FLOORS = 5

MAX_CABINE_PERSONS = 5  # Changing of this value makes UI look ugly
ELEVATOR_SPEED = 1

# Colors
BUILDING_CLR = Fore.BLACK
FLOOR_NUM_CLR = Fore.YELLOW
ELEVATOR_CLR = Fore.RED
PERSONS_CLR = Fore.GREEN
