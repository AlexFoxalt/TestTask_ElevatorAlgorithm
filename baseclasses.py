import logging
from random import randint
from time import sleep
from colorama import Fore

from config import MIN_PERSONSET, \
    MAX_PERSONSET, \
    MAX_TOTAL_FLOORS, \
    MIN_TOTAL_FLOORS, \
    MAX_CABINE_PERSONS, \
    ELEVATOR_SPEED, \
    PERSONS_CLR, \
    FLOOR_NUM_CLR, \
    BUILDING_CLR, \
    ELEVATOR_CLR, \
    NORMAL_MODE
from errors import ElevatorError, SuccessElevatorJob
from utils import random_floor_except_current, get_direction, count_buttons, fak

logging.basicConfig(level=logging.DEBUG)


class Person:
    def __init__(self, current_floor: int, total_floors: int):
        self.name = fak.first_name()
        self.total = total_floors
        self.current = current_floor
        self.target = random_floor_except_current(self.current, self.total)
        self.go_up, self.go_down = get_direction(self.current, self.target)

    def __repr__(self):
        return f"Person(name={self.name}, current={self.current}, target={self.target})"

    def renew_target(self):
        self.target = random_floor_except_current(self.current, self.total)
        self.go_up, self.go_down = get_direction(self.current, self.target)

    def set_current(self):
        self.current = self.target


class Floor:
    def __init__(self, num: int):
        self.num = num
        self.personset = list()
        self.up_btn, self.down_btn = None, None
        self.is_last = False

    def __repr__(self):
        return f"Floor(num={self.num}, persons={len(self.personset) if self.personset else 0})"

    def generate_personset(self, total_floors: int):
        self.personset = [Person(self.num, total_floors) for _ in range(randint(MIN_PERSONSET, MAX_PERSONSET))]
        self.up_btn, self.down_btn = count_buttons(self.personset)

    @classmethod
    def generate_floors(cls):
        response = []
        total_floors = randint(MIN_TOTAL_FLOORS, MAX_TOTAL_FLOORS)
        for num in range(1, total_floors + 1):
            floor = cls(num)
            floor.generate_personset(total_floors)
            response.append(floor)
        response[-1].is_last = True
        return response

    def move_to_empty_cabin(self, count):
        response = self.personset[:count]
        self.personset = self.personset[count:]
        return response


class Elevator:
    def __init__(self, floorset: list[Floor]):
        self.floorset = floorset
        self.current = 0
        self.max_target = int()
        self.cabin = list()
        self.max_cabin_size = MAX_CABINE_PERSONS
        self.go_up = True
        self.go_down = False
        self.status = "<waiting for commands>"
        self.step = 0
        self.total_persons = 0

    # UI _______________________________________________________________________________________________________________

    def send_scheme(self):
        """
        Initial information about our building
        :return: None
        """
        response = []
        for floor in self.floorset[::-1]:
            persons_targets = ["{:02d}".format(prs.target) for prs in floor.personset]
            self.total_persons += len(floor.personset)
            if not persons_targets:
                persons_targets = ['<empty>']
            response.append(Fore.WHITE + f"[{floor.num}\t| {' ,'.join(persons_targets)}]")

        total_floors = len(self.floorset)
        response = [Fore.GREEN + f"Success! The building is built :)\n"
                                 f"Total floors: {total_floors}\n"
                                 f"Total persons: {self.total_persons}\n"
                                 f"Normal mode: {'ON' if NORMAL_MODE else 'OFF'}\n\n"] + response
        response = "\n".join(response)
        print(response + "\n\n")

    def send_log(self):
        """
        Console UI

        :return:
        """
        self.step += 1

        if self.go_up:
            direction = "↑"
        else:
            direction = "↓"

        response = [BUILDING_CLR + f"___//=====" +
                    ELEVATOR_CLR + f"{direction}[" +
                    FLOOR_NUM_CLR + f"{'{:02d}'.format(self.current) if self.total_persons else ':)'}" +
                    ELEVATOR_CLR + f"]{direction}"]
        if NORMAL_MODE:
            response[0] += BUILDING_CLR + f"=====\\\\_____\t(step №{self.step})\t(ppl: {self.total_persons})"
        else:
            response[0] += BUILDING_CLR + f"=====\\\\_____\t(step №{self.step})"

        for floor in self.floorset[::-1]:
            persons_targets = ["{}({:02d}{})".format(prs.name, prs.target, "↑" if prs.go_up else "↓") for prs in
                               floor.personset]
            if not persons_targets:
                persons_targets = ['<empty>']

            if floor.num == self.current:
                persons_cabin = ["{:02d}".format(prs.target) for prs in self.cabin]
                persons_cabin = "{:<14}".format(','.join(persons_cabin))
                response.append(f"[" +
                                FLOOR_NUM_CLR + f"{floor.num}\t" +
                                BUILDING_CLR + f"|" +
                                ELEVATOR_CLR + f"[{persons_cabin}]" +
                                BUILDING_CLR + f"| " +
                                PERSONS_CLR + f"{' ,'.join(persons_targets)}" +
                                BUILDING_CLR + f"]")
            else:
                if floor.num < self.current:
                    response.append(f"[" +
                                    FLOOR_NUM_CLR + f"{floor.num}\t" +
                                    BUILDING_CLR + f"|                | " +
                                    PERSONS_CLR + f"{' ,'.join(persons_targets)}" +
                                    BUILDING_CLR + f"]")
                else:
                    response.append(f"[" +
                                    FLOOR_NUM_CLR + f"{floor.num}\t" +
                                    BUILDING_CLR + f"|       " +
                                    ELEVATOR_CLR + f"||" +
                                    BUILDING_CLR + f"       | " +
                                    PERSONS_CLR + f"{' ,'.join(persons_targets)}" +
                                    BUILDING_CLR + f"]")

        response = "\n".join(response)
        print(response + "\n\n")

    # Utils ____________________________________________________________________________________________________________

    def set_status(self, status: str):
        self.status = status

    def get_current_personset(self):
        # Current index of personset = current floor num - 1
        return self.floorset[self.current - 1].personset

    def release_the_arrivals(self, arrivals):
        self.cabin = [prs for prs in self.cabin if prs not in arrivals]

    def calculate_empty_slots(self):
        cabin_size = len(self.cabin)
        return self.max_cabin_size - cabin_size

    # Commands _________________________________________________________________________________________________________

    def execute_first(self):
        """
        Executes first step of Elevator, and starts endless process:

        execute  →  move_next
           ↑            ↓
        move_next  ←  execute

        :return: None
        """
        self.send_scheme()
        # Take persons from first floor, if there are no persons - go next
        if self.floorset[self.current].personset:
            self.cabin = self.floorset[self.current].move_to_empty_cabin(self.max_cabin_size)
            self.max_target = max(self.cabin, key=lambda i: i.target).target
        else:
            self.max_target = self.floorset[-1].num

        self.move_next()

    def move_next(self):
        """
        Moves Elevator throw floorset, set direction and configures current floor value

        :return: None
        """
        # Elevator direction setup and renew
        if self.go_up:
            if self.current >= self.max_target:
                self.go_up, self.go_down = False, True
        elif self.go_down:
            if self.current <= self.max_target:
                self.go_up, self.go_down = True, False
        else:
            logging.error("Somehow Elevator has no direction, so it can't calculate next floor number")
            raise ElevatorError()

        # Set new current floor value according to direction
        if self.go_up:
            self.current += 1
        elif self.go_down:
            self.current -= 1

        self.execute()

    def execute(self):
        """
        Main process, manipulates with floor, cabin and persons

        :return: None
        """
        # Since our Elevator is real life prototype, we don't want time machine, so let's set the speed
        sleep(ELEVATOR_SPEED)

        # Let's check, maybe current floor is someone's target floor
        arrived_their_target = [prs for prs in self.cabin if prs.target == self.current]

        # If we found someone, let these persons go out from cabin
        if arrived_their_target:
            self.release_the_arrivals(arrived_their_target)

            # Set new current floor and renew target floors for arrived persons
            for prs in arrived_their_target:
                prs.set_current()
                prs.renew_target()

        # If cabin is full just go next floor
        if len(self.cabin) == self.max_cabin_size:
            self.send_log()
            self.move_next()

        # Calculate how many empty slots in the cabin after persons went out
        empty_slots = self.calculate_empty_slots()

        current_personset = self.get_current_personset()
        # If there are no 'waiters' on current floor, skip this part
        if current_personset:
            # Form a list of persons to enter
            if self.cabin:
                # So if Elevator already moves somewhere with persons, let's take only guys, with same direction target
                if self.go_up:
                    persons_to_enter = [prs for prs in current_personset if prs.go_up][:empty_slots]
                elif self.go_down:
                    persons_to_enter = [prs for prs in current_personset if prs.go_down][:empty_slots]
                else:
                    logging.error("Somehow Elevator has no direction, so it can't decide who should enter")
                    raise ElevatorError()

            # If Elevator cabin is empty, and there are still left persons on floor
            else:
                majority_up = [prs for prs in current_personset if prs.go_up]
                majority_down = [prs for prs in current_personset if prs.go_down]

                # According to the tech task, first, let's calculate who's the majority
                majority_up_size = len(majority_up)
                majority_down_size = len(majority_down)

                # At the last floor majority will always be 'majority_down'
                if self.floorset[self.current - 1].is_last:
                    persons_to_enter = majority_down
                # Here the situation is reversed
                elif self.current == 1:
                    persons_to_enter = majority_up

                # If there is no majority, let the first guy in queue decide where we go
                if majority_up_size == majority_down_size:
                    if current_personset[0].go_up:
                        persons_to_enter = majority_up
                    else:
                        persons_to_enter = majority_down

                # Default cases, where majority is possible to calculate
                elif majority_up_size > majority_down_size:
                    persons_to_enter = majority_up
                elif majority_up_size < majority_down_size:
                    persons_to_enter = majority_down
                else:
                    logging.error("Somehow Elevator can't calculate majority on the floor")
                    raise ElevatorError()

                # Lets fill cabin to the max.value, and no more!
                persons_to_enter = persons_to_enter[:empty_slots]

            # Update cabin
            self.cabin.extend(persons_to_enter)
            # Remove entered persons from waiters
            self.floorset[self.current - 1].personset = [
                prs for prs in self.floorset[self.current - 1].personset if prs not in persons_to_enter
            ]

        # Add persons that arrived to "waiters" pool, or let them go to their business if NORMAL_MODE
        if not NORMAL_MODE:
            self.get_current_personset().extend(arrived_their_target)
        else:
            # Change value of total persons according to size of arrived persons
            self.total_persons -= len(arrived_their_target)

            # Here we deciding where the Elevator should go, when cabin and floor are empty
            if not self.cabin and not current_personset:
                # Searching for floor, where there is at least 1 waiter
                for floor in self.floorset:
                    if floor.personset:
                        # Find, set, go
                        self.max_target = floor.num
                        break

        # Recalculate new max.target value according to the Elevator's direction if cabin not empty
        if self.cabin:
            if self.go_up:
                self.max_target = max(self.cabin, key=lambda i: i.target).target
            elif self.go_down:
                self.max_target = min(self.cabin, key=lambda i: i.target).target
            else:
                logging.error("Somehow Elevator has no direction, so it can't calculate new max.target")
                raise ElevatorError()

        self.send_log()

        # If the Elevator working with NORMAL_MODE=True, here is exit from loop
        if not self.total_persons:
            raise SuccessElevatorJob()

        self.move_next()
