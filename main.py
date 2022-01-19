import baseclasses
from colorama import Back, Style, Fore

from errors import SuccessElevatorJob

if __name__ == '__main__':
    try:
        fs = baseclasses.Floor.generate_floors()
        el = baseclasses.Elevator(fs)
        el.execute_first()
    except KeyboardInterrupt:
        print(Back.RED + Fore.BLACK + 'Someone broke the Elevator :(' + Style.RESET_ALL)
    except SuccessElevatorJob:
        print(Back.GREEN + Fore.BLACK + 'The Elevator did its job and went to rest!' + Style.RESET_ALL)
