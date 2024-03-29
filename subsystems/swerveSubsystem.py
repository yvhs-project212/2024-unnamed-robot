import logging
import wpilib
from wpimath.geometry import Translation2d, Rotation2d, Pose2d
from pathplannerlib.path import PathPlannerPath, PathConstraints, GoalEndState

from swervepy import u, SwerveDrive, TrajectoryFollowerParameters
from swervepy.impl import CoaxialSwerveModule

from constants import PHYS, MECH, ELEC, OP, SW
import subsystems.swerveComponents as swerveComponents
import commands2
import commands2.button
logger = logging.getLogger("project212_robot")


class swerveSubsystem(commands2.Subsystem):
    def __init__(self):
        self.DriverController = commands2.button.CommandXboxController(OP.driver_controller)
        
        self.navx_adapter = swerveComponents.gyro_component_class(**swerveComponents.gyro_param_values)
        self.gyro = self.navx_adapter.navx
        self.gyro.zeroYaw()


        # The Azimuth component included the absolute encoder because it needs
        # to be able to reset to absolute position.
        #
        self.lf_enc = swerveComponents.absolute_encoder_class(ELEC.LF_encoder_DIO, SW.lf_enc_zeropos)
        self.lb_enc = swerveComponents.absolute_encoder_class(ELEC.LB_encoder_DIO, SW.lb_enc_zeropos)
        self.rb_enc = swerveComponents.absolute_encoder_class(ELEC.RB_encoder_DIO, SW.rb_enc_zeropos)
        self.rf_enc = swerveComponents.absolute_encoder_class(ELEC.RF_encoder_DIO, SW.rf_enc_zeropos)

        # Determine what the current reading of the 4 encoders should be, given
	    # that SW.XX_enc_zeropos says where the wheels face front
	    #
        """
        lf_enc_pos = self.lf_enc.absolute_position_degrees - SW.lf_enc_zeropos
        rf_enc_pos = self.rf_enc.absolute_position_degrees - SW.rf_enc_zeropos
        lb_enc_pos = self.lb_enc.absolute_position_degrees - SW.lb_enc_zeropos
        rb_enc_pos = self.rb_enc.absolute_position_degrees - SW.rb_enc_zeropos
        """
        lf_enc_pos = self.lf_enc.absolute_position_degrees
        rf_enc_pos = self.rf_enc.absolute_position_degrees
        lb_enc_pos = self.lb_enc.absolute_position_degrees
        rb_enc_pos = self.rb_enc.absolute_position_degrees
        logger.info(f"Encoder positions: LF={lf_enc_pos}, RF={rf_enc_pos}, RB={rb_enc_pos}, LB={lb_enc_pos}")
        
        self.modules = (
            # Left Front module
            CoaxialSwerveModule(
                drive=swerveComponents.drive_component_class(
                    id_=ELEC.LF_drive_CAN_ID,
                    parameters=swerveComponents.drive_params,
                ),
                azimuth=swerveComponents.azimuth_component_class(
                    id_=ELEC.LF_steer_CAN_ID,
                    azimuth_offset=Rotation2d.fromDegrees(lf_enc_pos),
                    parameters=swerveComponents.azimuth_params,
                    absolute_encoder=self.lf_enc,
                ),
                placement=Translation2d(*swerveComponents.module_locations["LF"]),
            ),
            # Right Front module
            CoaxialSwerveModule(
                drive=swerveComponents.drive_component_class(
                    id_=ELEC.RF_drive_CAN_ID,
                    parameters=swerveComponents.drive_params,
                ),
                azimuth=swerveComponents.azimuth_component_class(
                    id_=ELEC.RF_steer_CAN_ID,
                    azimuth_offset=Rotation2d.fromDegrees(rf_enc_pos),
                    parameters=swerveComponents.azimuth_params,
                    absolute_encoder=self.rf_enc,
                ),
                placement=Translation2d(*swerveComponents.module_locations["RF"]),
            ),
            # Left Back module
            CoaxialSwerveModule(
                drive=swerveComponents.drive_component_class(
                    id_=ELEC.LB_drive_CAN_ID,
                    parameters=swerveComponents.drive_params,
                ),
                azimuth=swerveComponents.azimuth_component_class(
                    id_=ELEC.LB_steer_CAN_ID,
                    azimuth_offset=Rotation2d.fromDegrees(lb_enc_pos),
                    parameters=swerveComponents.azimuth_params,
                    absolute_encoder=self.lb_enc,
                ),
                placement=Translation2d(*swerveComponents.module_locations["LB"]),
            ),
            # Right Back module
            CoaxialSwerveModule(
                drive=swerveComponents.drive_component_class(
                    id_=ELEC.RB_drive_CAN_ID,
                    parameters=swerveComponents.drive_params,
                ),
                azimuth=swerveComponents.azimuth_component_class(
                    id_=ELEC.RB_steer_CAN_ID,
                    azimuth_offset=Rotation2d.fromDegrees(rb_enc_pos),
                    parameters=swerveComponents.azimuth_params,
                    absolute_encoder=self.rb_enc,
                ),
                placement=Translation2d(*swerveComponents.module_locations["RB"]),
            ),
        )

        self.speed_limit_ratio = 1.0
        if OP.speed_limit:
            if OP.speed_limit > OP.max_speed:
                wpilib.reportWarning("Speed limit is greater than max_speed and won't be used")
            else:
                self.speed_limit_ratio = OP.speed_limit / OP.max_speed

        self.angular_velocity_limit_ratio = 1.0
        if OP.angular_velocity_limit:
            if OP.angular_velocity_limit > OP.max_angular_velocity:
                wpilib.reportWarning("Angular velocity limit is greater than max_angular_velocity and won't be used")
            else:
                self.angular_velocity_limit_ratio = (
                    OP.angular_velocity_limit / OP.max_angular_velocity)
        
    def log_data(self):
        for pos in ("LF", "RF", "LB", "RB"):
            encoder = getattr(self, f"{pos.lower()}_enc")
            wpilib.SmartDashboard.putNumber(f"{pos} absolute encoder", encoder.absolute_position_degrees)
            wpilib.SmartDashboard.putNumber(f"{pos} absolute encoder", encoder.absolute_position_degrees)

    @staticmethod
    def deadband(value, band):
        return value if abs(value) > band else 0

    def process_joystick_input(self, val, deadband=0.1, exponent=1, limit_ratio=1.0, invert=False):
        """
        Given a raw joystick reading, return the processed value after adjusting
        for real-world UX considerations:
          * apply a deadband to ignore jitter around zero
          * apply an exponent for greater low-velocity control
        """
        deadbanded_input = self.deadband(val, deadband)
        input_sign = +1 if val > 0 else -1  # this works for val=0 also
        invert_sign = -1 if invert else +1
        # abs required for fractional exponents
        scaled_input = limit_ratio * abs(deadbanded_input) ** exponent
        return invert_sign * input_sign * scaled_input

    def get_translation_input(self, invert=True):
        raw_stick_val = self.DriverController.getRawAxis(OP.translation_joystick_axis)
        return self.process_joystick_input(raw_stick_val, invert=invert,
                                           limit_ratio=self.speed_limit_ratio)

    def get_strafe_input(self, invert=True):
        raw_stick_val = self.DriverController.getRawAxis(OP.strafe_joystick_axis)
        return self.process_joystick_input(raw_stick_val, invert=invert,
                                           limit_ratio=self.speed_limit_ratio)

    def get_rotation_input(self, invert=True):
        raw_stick_val = self.DriverController.getRawAxis(OP.rotation_joystick_axis)
        return self.process_joystick_input(
            raw_stick_val, invert=invert, limit_ratio=self.angular_velocity_limit_ratio)
                
    def getSwerve(self) -> SwerveDrive:
        return SwerveDrive(self.modules, self.navx_adapter, OP.max_speed, OP.max_angular_velocity)
        
    def getSwerveTeleopCommand(self, swerve: SwerveDrive):
        return swerve.teleop_command(
                translation=self.get_translation_input,
                strafe=self.get_strafe_input,
                rotation=self.get_rotation_input,
                field_relative=SW.field_relative,
                drive_open_loop=SW.drive_open_loop,
            )

