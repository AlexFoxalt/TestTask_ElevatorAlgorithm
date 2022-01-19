from random import randint
from faker import Faker

fak = Faker()


def get_direction(current: int, target: int) -> tuple[bool, bool]:
    return target > current, target < current


def random_floor_except_current(current: int, total: int) -> int:
    response = randint(1, total)
    if response == current:
        return random_floor_except_current(current, total)
    else:
        return response


def count_buttons(personset: list) -> tuple[int, int]:
    up_btn = len(tuple(pers for pers in personset if pers.go_up))
    down_btn = len(tuple(pers for pers in personset if pers.go_down))
    return up_btn, down_btn
