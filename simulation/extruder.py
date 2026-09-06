"""The Bowden extruder on the front top beam.

The bracket sits on the beam and cradles the gearmotor with its axis
along the beam, 26 mm up; the printed body is bolted to the gearhead
and hangs from it, so the body stands beside the bracket along the beam.
extruder.scad draws the body for the printer -- its module is
``rotate([90, 0, 0])`` of the geometry it authors -- so the part is
turned back and then set with the motor axis along the beam, the
filament path horizontal, its entry outside the frame and its push-fit
pointing at the centre.  A vertical path would have put the push-fit
through the beam.

The assembly frame is the beam's: origin at the beam's axis midpoint on
its top face, X along the beam, Y toward the printer's centre, Z up.
"""

import math

from solid2 import cube
from solid_node.node import AssemblyNode

from simulation import hardware, materials, scad
from simulation.effector import PushFit
from simulation.fasteners import Bearing, M3Nut, M3Screw, M5Nut, M5Screw
from simulation.layout import (
    EXTRUDER_BODY_DEPTH,
    EXTRUDER_BRACKET_SCREWS,
    EXTRUDER_CRADLE_HEIGHT,
    EXTRUDER_ENTRY_Z,
    EXTRUDER_FILAMENT,
    EXTRUDER_IDLER_X,
    EXTRUDER_IDLER_Y,
    EXTRUDER_MOTOR_AXIS,
    EXTRUDER_MOTOR_SCREW_ANGLE,
    EXTRUDER_MOTOR_SCREW_RADIUS,
    EXTRUDER_NUT_Y,
)
from simulation.part import PrintedPart, ScadPart, curve
from simulation.place import along_minus_x, along_minus_z, along_y

#: Where the body's own frame stands in the assembly's: its motor axis
#: (x 16, z 21) on the cradle's (z 26), its front face (y 0) 37.5 along
#: the beam so the 40 mm motor behind its face covers the 29 mm bracket.
BODY_ORIGIN = (37.5, 21.0, 10.0)

BRACKET_SCREW = 8.0
MOTOR_SCREW = 25.0
#: extruder.scad drills three of the gearmotor's four holes -- the fourth
#: is where the filament path and idler are -- at these angles about the
#: motor axis in the body's own frame.
MOTOR_SCREW_ANGLES = (135.0, 225.0, 315.0)
IDLER_SCREW = 20.0


def body_point(x, y, z):
    """A point of extruder.scad's own frame in the assembly's: its X up,
    its Y back along the beam, its Z out from the centre."""
    return [BODY_ORIGIN[0] - y, BODY_ORIGIN[1] - z, BODY_ORIGIN[2] + x]


class ExtruderBracket(PrintedPart):
    """frame_extruder.scad: base on the XY plane, cradle axis along Y."""

    def render(self):
        return scad.frame_extruder.frame_extruder()


class ExtruderBody(PrintedPart):
    """extruder.scad as drawn for the printer, less the five "removable
    supports" it prints across the idler bearing's cavity -- 0.5 mm
    walls a builder breaks out before the bearing goes in.  They are cut
    where the drawing puts them, inside the cavity only, in the drawing's
    own frame and then turned as the module turns itself."""

    def render(self):
        cavity = (curve('cylinder', r=8.5, h=5.25).rotate([90, 0, 0]).translate([31, 9.5, 21])
                  + cube([20, 5.25, 18.5]).translate([31, 4.25, 10.75])
                  + cube([10, 5.25, 8]).translate([20, 4.25, 16]))
        supports = None
        for z in range(15, 28, 3):
            wall = cube([20, 20, 0.5], center=True).translate([36, 10, z])
            supports = wall if supports is None else supports + wall
        return scad.extruder.extruder() - (supports & cavity).rotate([90, 0, 0])


class Gearmotor(ScadPart):
    """The PG35L gearmotor: gearhead face on the XY plane, body down -Z,
    boss and shaft up +Z, four tapped holes in the face."""

    color = materials.MOTOR

    def render(self):
        body = (curve('cylinder', r=hardware.PG35L_DIAMETER / 2, h=hardware.PG35L_LENGTH)
                .translate([0, 0, -hardware.PG35L_LENGTH]))
        boss = curve('cylinder', r=hardware.PG35L_BOSS_DIAMETER / 2, h=hardware.PG35L_BOSS)
        shaft = curve('cylinder', r=hardware.PG35L_SHAFT / 2, h=hardware.PG35L_SHAFT_LENGTH)
        motor = body + boss + shaft
        for k in range(4):
            angle = math.radians(EXTRUDER_MOTOR_SCREW_ANGLE + 90 * k)
            motor -= (curve('cylinder', r=hardware.M3_SHANK / 2 + hardware.FIT, h=6)
                      .translate([EXTRUDER_MOTOR_SCREW_RADIUS * math.cos(angle),
                                  EXTRUDER_MOTOR_SCREW_RADIUS * math.sin(angle), -5.9]))
        return motor


class DriveGear(ScadPart):
    """An MK7 drive gear along +Z: the toothed body from 0 with its hob
    groove 3 mm up, the hub beyond it."""

    color = materials.STEEL

    HOB_STATION = 3.0

    def render(self):
        toothed = curve('cylinder', r=hardware.MK7_DIAMETER / 2, h=hardware.MK7_TOOTHED)
        hob = (curve('cylinder', r=hardware.MK7_DIAMETER, h=hardware.MK7_HOB_WIDTH)
               - curve('cylinder', r=hardware.MK7_HOB_DIAMETER / 2,
                       h=hardware.MK7_HOB_WIDTH + 2).translate([0, 0, -1]))
        hub = (curve('cylinder', r=hardware.MK7_HUB_DIAMETER / 2, h=hardware.MK7_HUB)
               .translate([0, 0, hardware.MK7_TOOTHED]))
        gear = toothed - hob.translate([0, 0, self.HOB_STATION - hardware.MK7_HOB_WIDTH / 2]) + hub
        return gear - curve('cylinder', r=hardware.PG35L_SHAFT / 2 + hardware.FIT,
                            h=3 * (hardware.MK7_TOOTHED + hardware.MK7_HUB), center=True)


class Extruder(AssemblyNode):

    bracket = ExtruderBracket()
    bracket_screws = M3Screw(length=BRACKET_SCREW).repeat(3)
    bracket_nuts = M3Nut().repeat(3)
    motor = Gearmotor()
    body = ExtruderBody()
    motor_screws = M3Screw(length=MOTOR_SCREW).repeat(3)
    gear = DriveGear()
    idler = Bearing(bore=hardware.BEARING_625[0], outer=hardware.BEARING_625[1],
                    width=hardware.BEARING_625[2])
    idler_screw = M5Screw(length=IDLER_SCREW)
    idler_nut = M5Nut()
    pushfit = PushFit()

    def render(self):
        standoff = hardware.STANDOFF
        # the bracket, its long side along the beam, screwed into the top slot
        self.bracket.rotate(-90, [0, 0, 1]).translate([0, 0, standoff])
        for screw, nut, x in zip(self.bracket_screws, self.bracket_nuts, EXTRUDER_BRACKET_SCREWS):
            along_minus_z(screw).translate([x, 0, 3.6 + 2 * standoff])
            along_minus_z(nut.rotate(30, [0, 0, 1])).translate(
                [x, 0, -hardware.SLOT_LIP_DEPTH - standoff])

        # the body: undo its print turn, stand it up, set it by its origin
        (self.body.rotate(-90, [1, 0, 0]).rotate(-90, [0, 1, 0]).rotate(90, [0, 0, 1])
         .translate(list(BODY_ORIGIN)))

        # the motor's face against the body's back, shaft along -X into it
        face = body_point(EXTRUDER_MOTOR_AXIS[0], EXTRUDER_BODY_DEPTH, EXTRUDER_MOTOR_AXIS[1])
        self.motor.rotate(90, [0, 1, 0]).translate([face[0] - standoff, face[1], face[2]])
        for screw, degrees in zip(self.motor_screws, MOTOR_SCREW_ANGLES):
            angle = math.radians(degrees)
            seat = body_point(EXTRUDER_MOTOR_AXIS[0] + EXTRUDER_MOTOR_SCREW_RADIUS * math.cos(angle),
                              0.0,
                              EXTRUDER_MOTOR_AXIS[1] + EXTRUDER_MOTOR_SCREW_RADIUS * math.sin(angle))
            along_minus_x(screw).translate([seat[0] + standoff, seat[1], seat[2]])

        # the drive gear on the shaft, hob at the filament
        gear_end = body_point(EXTRUDER_MOTOR_AXIS[0],
                              EXTRUDER_FILAMENT[1] - self.gear.HOB_STATION + standoff,
                              EXTRUDER_MOTOR_AXIS[1])
        self.gear.rotate(-90, [0, 1, 0]).translate(gear_end)

        # the idler bearing on its M5, nut in the trap behind
        cavity = (EXTRUDER_IDLER_Y[0] + EXTRUDER_IDLER_Y[1]) / 2
        bearing_end = body_point(EXTRUDER_IDLER_X, cavity - hardware.BEARING_625[2] / 2,
                                 EXTRUDER_MOTOR_AXIS[1])
        self.idler.rotate(-90, [0, 1, 0]).translate(bearing_end)
        head = body_point(EXTRUDER_IDLER_X, 0.0, EXTRUDER_MOTOR_AXIS[1])
        along_minus_x(self.idler_screw).translate([head[0] + standoff, head[1], head[2]])
        nut = body_point(EXTRUDER_IDLER_X, EXTRUDER_NUT_Y[0] + standoff, EXTRUDER_MOTOR_AXIS[1])
        along_minus_x(self.idler_nut).translate(nut)

        # the push-fit in the body's exit, pointing at the centre
        foot = body_point(EXTRUDER_FILAMENT[0], EXTRUDER_FILAMENT[1], hardware.PUSHFIT_STUB)
        along_y(self.pushfit).translate(foot)

    @property
    def tube_seat(self):
        """Where the Bowden tube starts, in the assembly's frame."""
        foot = body_point(EXTRUDER_FILAMENT[0], EXTRUDER_FILAMENT[1], hardware.PUSHFIT_STUB)
        return [foot[0], foot[1] + self.pushfit.seat, foot[2]]

    @property
    def filament_entry(self):
        """Where the filament enters the body, in the assembly's frame."""
        return body_point(EXTRUDER_FILAMENT[0], EXTRUDER_FILAMENT[1], EXTRUDER_ENTRY_Z)
