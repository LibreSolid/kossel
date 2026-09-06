"""The printed carriage on its block, with the ball-joint screw."""

from solid_node.node import AssemblyNode

from simulation import hardware, scad
from simulation.fasteners import Ball, M3ButtonScrew, M3Nut, M3Screw
from simulation.layout import (
    CARRIAGE_HORN_Y,
    CARRIAGE_HORN_Z,
    CARRIAGE_SCREW_PATTERN,
    CARRIAGE_SEPARATION,
)
from simulation.part import PrintedPart
from simulation.place import along_minus_x, along_minus_y, along_x
from simulation.rail import Block

#: The carriage's plate, from carriage.scad.
PLATE = 6.0

#: The carriage's four screws into the block: the lower two through 6 mm
#: of plate, the upper two down through 13 mm of horn and belt clamp,
#: because the drawing runs those holes through both and leaves the head
#: nowhere to sit but on top.
PLATE_SCREW = 10.0
HORN_SCREW = 18.0
HORN_TOP = 13.0

#: Where a ball's centre stands off the carriage's centre plane: the horn
#: face plus the hollow ball's sleeve.
BALL_STATION = CARRIAGE_SEPARATION / 2 + hardware.BALL_SLEEVE_IN + hardware.STANDOFF

#: Where each joint screw's head seats: on the sleeve's outer end.  The
#: screw runs in through the horn to the lock nut trapped inside it --
#: "Lock nuts for ball joints", the hex cones from x = 4 to 12 in
#: carriage.scad -- so an M3 x 20 reaches a nut standing at 9.5.
CLAMP_STATION = BALL_STATION + hardware.BALL_SLEEVE_OUT + hardware.STANDOFF
JOINT_SCREW = 20.0
NUT_STATION = 9.5


class Carriage(PrintedPart):
    """carriage.scad, in its own frame: plate on the XY plane, X across,
    Y up the tower, Z toward the printer's centre."""

    def render(self):
        return scad.carriage.carriage()


class CarriageAssembly(AssemblyNode):
    """Block, carriage and the joint hardware, in the tower's frame with
    the rail's base on the XZ plane and the block's centre at Z = 0: +Y
    toward the centre, Z up.

    The carriage is drawn flat with its horns along +Y; on the tower its
    plate normal is the radial and its horns point up, which is one
    quarter turn about X and a half turn about Y -- the second so that
    +X stays the tower's +X rather than its mirror.
    """

    block = Block()
    carriage = Carriage()
    plate_screws = M3Screw(length=PLATE_SCREW).repeat(2)
    horn_screws = M3Screw(length=HORN_SCREW).repeat(2)
    joint_screws = M3ButtonScrew(length=JOINT_SCREW).repeat(2)
    joint_nuts = M3Nut().repeat(2)
    balls = Ball().repeat(2)

    def render(self):
        seat = hardware.BLOCK_HEIGHT  # the block's top, off the rail base
        (self.carriage
         .rotate(-90, [1, 0, 0])
         .rotate(180, [0, 1, 0])
         .translate([0, seat + hardware.STANDOFF, 0]))
        half = CARRIAGE_SCREW_PATTERN / 2
        for screw, x in zip(self.plate_screws, (-half, half)):
            along_minus_y(screw).translate([x, seat + PLATE + 2 * hardware.STANDOFF, -half])
        for screw, x in zip(self.horn_screws, (-half, half)):
            along_minus_y(screw).translate([x, seat + HORN_TOP + 2 * hardware.STANDOFF, half])

        axis_y = seat + CARRIAGE_HORN_Z
        axis_z = CARRIAGE_HORN_Y
        for side, screw, nut, ball in zip((-1, 1), self.joint_screws, self.joint_nuts, self.balls):
            # the sleeve's -Z end toward the horn; the screw's +Z shank inward
            inward = along_x if side < 0 else along_minus_x
            outward = along_minus_x if side < 0 else along_x
            outward(ball).translate([side * BALL_STATION, axis_y, axis_z])
            inward(screw).translate([side * CLAMP_STATION, axis_y, axis_z])
            # the trap's hexagon stands with its vertices up the tower
            inward(nut.rotate(30, [0, 0, 1])).translate([side * NUT_STATION, axis_y, axis_z])
