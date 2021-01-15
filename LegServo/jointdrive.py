import math
from LegServo.servo_ax12a import *


# Class definition of ax12a-controller class, defines interface to the robot
# ===============================================================================
# Implements the interface between leg- and servo class
# ------------------------------------------------------------------------------
# Provides all required methods that allow the leg class to control the servo
# Implements all necessary codomain conversion between leg- and servo values
# Limits values too valid servo values
# Servo uses ticks from 0 to 1023 for angle and speed
# Leg uses angles in radian and rotation per minit for speed
# todo: Defines zero angle as average of min- and max value -> positive and negativ angles are allowed!!!
# todo: Pass through Errors correctly
class JointDrive(ServoAx12a):
    # Definition of public class attributes
    # ----------------------------------------------------------------------

    # 1 time calculation for offsets
    # todo: second offset
    # todo: Zero angle offset of servo in radian
    _ANGLE_RADIAN_ZERO = (ServoAx12a._ANGLE_MAX_DEGREE - ServoAx12a._ANGLE_MIN_DEGREE) * math.pi / 360

    # Max angleoffset of servo in radian

    _ANGLE_RADIAN_MAX = ServoAx12a._ANGLE_MAX_DEGREE * 2 * math.pi / 360

    # Min angleoffset of servo in radian

    _ANGLE_RADIAN_MIN = ServoAx12a._ANGLE_MIN_DEGREE * 2 * math.pi / 360

    # Ticks per rad
    _ANGLE_UNIT = ServoAx12a._ANGLE_MAX_TICKS / (
                (ServoAx12a._ANGLE_MAX_DEGREE - ServoAx12a._ANGLE_MIN_DEGREE) * math.pi * 2 / 360)

    # Factor for speed to ticks
    _SPEED_TO_TICKS = ServoAx12a._SPEED_MAX_TICKS / ServoAx12a._SPEED_MAX_RPM

    # Factor for ticks to speed
    _TICKS_TO_SPEED = ServoAx12a._SPEED_MAX_RPM / ServoAx12a._SPEED_MAX_TICKS

    # Constructor, defines the following variables: counterClockWise, angleOffset, angleMax, angleMin
    def __init__(self, id, ccw=False, aOffset=0.0, aMax=math.pi * 2, aMin=-math.pi * 2):

        # id -> id of servo, cw -> rotating direction, aOffset -> angle offset,
        self.id = id
        self.counterClockWise = ccw
        self.aMax = JointDrive._ANGLE_RADIAN_MAX
        self.aMin = JointDrive._ANGLE_RADIAN_MIN

        # aMax -> maximum angle allowed, aMin -> minimum angle allowed
        if aMax > aMin:
            if aMax < self.aMax:
                self.aMax = aMax
            if aMin > self.aMin:
                self.aMin = aMin

        self.aOffset = aOffset
        self.curAngel = 0
        self.error = 0
        # access to Constructor to superclass (Servo)
        super().__init__(id)

    # Converts angle in radian to servo ticks
    # angle -> in radian, returns angle in servo ticks

    def __convertAngleToTicks(self, angle: float) -> int:

        if angle < self.aMin + self.aOffset or angle > self.aMax + self.aOffset:
            angle = self.aMin
        # control Servo from the right side
        if self.counterClockWise:
            angle = self._ANGLE_RADIAN_MAX - angle + self.aOffset
        else:
            angle = self._ANGLE_RADIAN_MIN + angle - self.aOffset

        return int(round(abs((self._ANGLE_UNIT * angle))))

   # def __convertByteToInt(nByte: list) -> int:
    #
     #   if nByte is not None and isinstance(nByte, list):
      #      nByte.reverse()
       #     n = len(nByte)
        #    res = 0
         #   for byte in nByte:
          #      res += byte << (8 * (n - 1))
           #     n -= 1
#
 #           return res
  #      else:
   #         return -1

    # Converts servo ticks to angle in radian
    # ticks -> servo ticks, returns angle in radian
    def __convertTicksToAngle(self, ticks: int) -> float:
        # convert bytes into one integer

        # if ccw
        if self.counterClockWise:
            angle = JointDrive._ANGLE_RADIAN_MAX - (ticks / self._ANGLE_UNIT) + self.aOffset
        else:
            angle = (ticks / self._ANGLE_UNIT) + self.aOffset

        return angle

    # Converts speed in rpm to servo ticks
    # speed -> value in rpm
    def __convertSpeedToTicks(self, speed: float) -> int:
        if speed >= self._SPEED_MAX_RPM:
            ticks = int(round(self._SPEED_MAX_TICKS))
        else:
            ticks = int(round(self._SPEED_TO_TICKS * speed))

        return ticks

    # Converts ticks to speed in rpm
    # ticks -> servo ticks
    def __convertTicksToSpeed(self, ticks: int) -> float:
        # Not needed Right now?
        # Check when its used -> when to use
        speed = ticks * JointDrive._TICKS_TO_SPEED
        return speed

    # Public methods
    # ----------------------------------------------------------------------
    # Get current angle of servo
    # returns angle in radian
    def getCurrentJointAngle(self) -> float:
        self.curAngel = self.__convertTicksToAngle(self.getPresentPosition())
        return self.curAngel

    # Set servo to desired angle
    # angle -> in radian,
    # speed -> speed of movement, speed < 0 -> no speed set, speed = 0 -> maximum speed
    def setDesiredJointAngle(self, angle: float, trigger: bool = False) -> bool:

        success = self.setGoalPosition(self.__convertAngleToTicks(angle), trigger)
        if success:
            self.curAngel = angle

        return success

    # Set servo to desired angle
    # angle -> in radian,
    # speed -> speed of movement in rpm, speed = 0 -> maximum speed
    def setDesiredAngleSpeed(self, angle: float, speed: float = 0, trigger: bool = False) -> bool:
        speed_in_ticks = self.__convertSpeedToTicks(speed)
        angle_in_ticks = self.__convertAngleToTicks(angle)

        success = self.setGoalPosSpeed(angle_in_ticks, speed_in_ticks, trigger)

        return success

    # Set speed value of servo
    # speed -> angle speed in rpm
    def setSpeedValue(self, speed, trigger=False):
        speed_in_ticks = self.__convertSpeedToTicks(speed)
        success = self.setMovingSpeed(speed_in_ticks, trigger)

        return success
