import wpilib
from wpimath.geometry import Translation2d, Rotation2d, Pose2d
from pathplannerlib.path import PathPlannerPath, PathConstraints, GoalEndState

from swervepy import u, SwerveDrive, TrajectoryFollowerParameters
import commands2
import math

import swervepy
def getAutoCommand(swerve: SwerveDrive, forwardDistance: float):
    follower_params = TrajectoryFollowerParameters(
        max_drive_velocity=0.5 * (u.m / u.s),
        theta_kP=1,
        xy_kP=1,
    )

    bezier_points = PathPlannerPath.bezierFromPoses([
        Pose2d(0.0, 0, Rotation2d.fromDegrees(0)),
        Pose2d(forwardDistance, 0, Rotation2d.fromDegrees(0)),
        #Pose2d(5.0, 3.0, Rotation2d.fromDegrees(90)),
    ])
    path = PathPlannerPath(
        bezier_points,
        PathConstraints(3.0, 3.0, 2 * math.pi, 4 * math.pi),
        GoalEndState(0.0, Rotation2d.fromDegrees(-90)),     # Zero velocity and facing 90 degrees clockwise
    )
    first_path = True  # reset robot pose to initial pose in trajectory
    open_loop = True
    return swerve.follow_trajectory_command(path, follower_params, first_path, open_loop)