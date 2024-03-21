import wpilib
import rev
import commands2
from subsystems.armSubsystem import ArmSubsystem
import constants

class ArmWithJoystick (commands2.Command):

    def __init__(self, armSubsystem: ArmSubsystem) -> None:
        self.armSubsystem = armSubsystem
        self.addRequirements(armSubsystem)
        self.joystickInput = wpilib.XboxController(constants.OP.operator_controller).getLeftY
 
    def execute(self):
        self.armSubsystem.armwithjoystick(self.joystickInput())

    def isFinished(self):
        return False
    
    def end(self, interrupted: bool):
        self.armSubsystem.arm_stop()
        
class armToGround(commands2.command):

    def __init__(self, armSubsystem: ArmSubsystem) -> None:
        super().__init__()
        self.armSubsystem = armSubsystem
 
    def execute(self):
        self.armSubsystem.armToGround()

    def isFinished(self):
        return False
    
    def end(self, interrupted: bool):
        self.armSubsystem.arm_stop()
        
class armToAmp(commands2.command):

    def __init__(self, armSubsystem: ArmSubsystem) -> None:
        super().__init__()
        self.armSubsystem = armSubsystem
 
    def execute(self):
        self.armSubsystem.armToAmp()

    def isFinished(self):
        return False
    
    def end(self, interrupted: bool):
        self.armSubsystem.arm_stop()
        
class stopArm(commands2.command):

    def __init__(self, armSubsystem: ArmSubsystem) -> None:
        super().__init__()
        self.armSubsystem = armSubsystem
 
    def execute(self):
        self.armSubsystem.arm_stop()

    def isFinished(self):
        return False
    
    def end(self, interrupted: bool):
        self.armSubsystem.arm_stop()

class armWithInput (commands2.Command):

    def __init__(self, armSubsystem: ArmSubsystem, input: float) -> None:
        self.armSubsystem = armSubsystem
        self.input = input
 
    def execute(self):
        self.armSubsystem.arm_up(self.input)

    def isFinished(self):
        if self.armSubsystem.armLimitSwitch.get():
            return False
        else:
            return True
    
    def end(self, interrupted: bool):
        self.armSubsystem.arm_stop()
