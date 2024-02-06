import wpilib
import rev
import commands2
from subsystems.armSubsystem import ArmSubsystem
import constants

class ArmisUp (commands2.Command):

    def __init__(self, armSubsystem: ArmSubsystem) -> None:
        super().__init__()
        self.armSubsystem = armSubsystem
        self.timer = wpilib.Timer()

    def initialize(self):
        self.timer.start()

    def execute(self):
        self.armSubsystem.arm_up(speed=1)
    
    def isFinished(self):
        return False
    
    def end(self, interrupted: bool):
        self.armSubsystem.arm_stop()


class ArmisDown (commands2.Command):

    def __init__(self, armSubsystem: ArmSubsystem) -> None:
        super().__init__()
        self.armSubsystem = armSubsystem
        self.timer = wpilib.Timer()

    def initialize(self):
        self.timer.start()

    def execute(self):
        self.armSubsystem.arm_down(speed=1)

    def isFinished(self):
        return False
    
    def end(self, interrupted: bool):
        self.armSubsystem.arm_stop()

class ArmWithJoystick (commands2.Command):

    def __init__(self, armSubsystem: ArmSubsystem) -> None:
        super().__init__()
        self.armSubsystem = armSubsystem
        self.timer = wpilib.Timer()

    def initialize(self):
        self.timer.start()

    def execute(self):
        self.armSubsystem.armwithjoystick(constants.OP.operator_joystick_port)

    def isFinished(self):
        return False
    
    def end(self, interrupted: bool):
        self.armSubsystem.arm_stop()

