class ElevatorError(Exception):
    def __init__(self, message="The Elevator has broken down and terminates it work!"):
        self.message = message
        super().__init__(self.message)


class SuccessElevatorJob(Exception):
    def __init__(self, message="The Elevator did a great job!"):
        self.message = message
        super().__init__(self.message)
