"""The effector and what hangs from it: the hot end in its clamp, the
push-fit on top, and the three ball-joint screws on the arms.

The effector is drawn for the printer with a 16 mm pocket 4 deep in its
upper half and an M5 thread in its lower half.  On the machine the
J-Head's collar goes in the pocket and the Bowden push-fit in the
thread, so it is mounted the other way up: one half turn about X puts
the pocket down and the thread up, and carries the drawing's arms from
30/150/270 degrees to 330/210/90, which are Marlin's towers.  The
assembly's origin is the effector's centre on its joint plane.
"""

import math

from solid2 import cube
from solid_node.node import AssemblyNode
from solid_node.motion.joints import Prismatic

from simulation import hardware, materials, scad
from simulation.fasteners import Ball, M3ButtonScrew, M3Nut, M3Screw
from simulation.layout import (
    EFFECTOR_MOUNT_RADIUS,
    EFFECTOR_OFFSET,
    EFFECTOR_SEPARATION,
    TOWER_ANGLES,
)
from simulation.part import PrintedPart, ScadPart, curve
from simulation.place import along_minus_x, along_minus_z, along_x

#: The screws through the effector into the clamp: 8 mm of effector, the
#: 0.76 the collar stands the plate off by, and 7 into the plate and
#: shroud.  Five, not six: the effector has six holes but the clamp is a
#: C around the groove and its slot takes the sixth position, so
#: hotend_fan.scad drills `[60:60:359]` -- five.
CLAMP_SCREW = 16.0
CLAMP_SCREW_ANGLES = (30.0, 90.0, 150.0, 210.0, 330.0)

#: Where a ball's centre stands off an arm's centre plane and where its
#: screw's head seats: the same joint as the carriage's.  Each screw runs
#: in through the horn to a nut in the hex channel the arm is drawn with
#: (16 mm long, centred), so an M3 x 25 reaches a nut standing at 5.5.
BALL_STATION = EFFECTOR_SEPARATION / 2 + hardware.BALL_SLEEVE_IN + hardware.STANDOFF
CLAMP_STATION = BALL_STATION + hardware.BALL_SLEEVE_OUT + hardware.STANDOFF
JOINT_SCREW = 25.0
NUT_STATION = 5.5

#: How far the collar stands proud of the effector's face: the collar the
#: groove-mount standard gives against the pocket the drawing cuts.
COLLAR_PROUD = hardware.JHEAD_COLLAR - 4.0

#: Half a tenth off, wherever two faces would otherwise meet.  The groove
#: is drawn 4.7 for the 4.6 plate so that it has this much either side.
STANDOFF = 0.05
PLATE_STANDOFF = 0.05


class Effector(PrintedPart):
    """effector.scad, centred on its joint plane, pocket up as drawn."""

    def render(self):
        return scad.effector.effector()


class Shroud(PrintedPart):
    """hotend_fan.scad: the groove clamp plate on the XY plane and the fan
    shroud rising from it, as drawn for the printer."""

    def render(self):
        return scad.hotend_fan.hotend_fan()


class PushFit(ScadPart):
    """A PC4-M5 push-fit, along +Z from its stub's foot: stub, body,
    collet, bored for the tube, which seats on the stub's top."""

    color = materials.BRASS

    def render(self):
        stub = (curve('cylinder', r=hardware.PUSHFIT_STUB_DIAMETER / 2,
                      h=hardware.PUSHFIT_STUB - STANDOFF)
                .translate([0, 0, STANDOFF]))
        body = (curve('cylinder', r=hardware.PUSHFIT_BODY_DIAMETER / 2, h=hardware.PUSHFIT_BODY)
                .translate([0, 0, hardware.PUSHFIT_STUB]))
        collet = (curve('cylinder', r=hardware.PUSHFIT_COLLET_DIAMETER / 2,
                        h=hardware.PUSHFIT_COLLET)
                  .translate([0, 0, hardware.PUSHFIT_STUB + hardware.PUSHFIT_BODY]))
        bore = (curve('cylinder', r=hardware.PUSHFIT_BORE / 2, h=20)
                .translate([0, 0, self.seat]))
        filament = curve('cylinder', r=hardware.FILAMENT_DIAMETER / 2 + 0.2, h=40, center=True)
        return stub + body + collet - bore - filament

    @property
    def height(self):
        return hardware.PUSHFIT_STUB + hardware.PUSHFIT_BODY + hardware.PUSHFIT_COLLET

    @property
    def seat(self):
        """Where the tube's end sits, up from the stub's foot: on the floor
        the body's bore leaves over the stub."""
        return hardware.PUSHFIT_STUB + 0.5


class JHeadHolder(ScadPart):
    """The PEEK nozzle holder of a J-Head Mk V-B, collar top on the XY
    plane and the part hanging down -Z: collar, groove, finned body."""

    color = materials.PEEK

    def render(self):
        collar = (curve('cylinder', r=hardware.JHEAD_COLLAR_DIAMETER / 2, h=hardware.JHEAD_COLLAR)
                  .translate([0, 0, -hardware.JHEAD_COLLAR]))
        groove_top = -hardware.JHEAD_COLLAR
        groove = (curve('cylinder', r=hardware.JHEAD_GROOVE_DIAMETER / 2, h=hardware.JHEAD_GROOVE)
                  .translate([0, 0, groove_top - hardware.JHEAD_GROOVE]))
        body_top = groove_top - hardware.JHEAD_GROOVE
        body = (curve('cylinder', r=hardware.JHEAD_BODY_DIAMETER / 2, h=hardware.JHEAD_BODY)
                .translate([0, 0, body_top - hardware.JHEAD_BODY]))
        holder = collar + groove + body
        first = body_top - hardware.JHEAD_BODY + 5.0
        for fin in range(hardware.JHEAD_FINS):
            z = first + fin * hardware.JHEAD_FIN_PITCH
            ring = (curve('cylinder', r=hardware.JHEAD_BODY_DIAMETER, h=hardware.JHEAD_FIN_GROOVE)
                    - curve('cylinder', r=hardware.JHEAD_FIN_ROOT / 2,
                            h=hardware.JHEAD_FIN_GROOVE + 2).translate([0, 0, -1]))
            holder -= ring.translate([0, 0, z])
        return holder - curve('cylinder', r=hardware.JHEAD_BORE / 2, h=100, center=True)

    @property
    def foot(self):
        """The body's bottom face, where the brass begins."""
        return -(hardware.JHEAD_COLLAR + hardware.JHEAD_GROOVE + hardware.JHEAD_BODY)


class Nozzle(ScadPart):
    """The brass of the J-Head: heater block and nozzle, block top on the
    XY plane, tip at -NOZZLE_REACH below the block."""

    color = materials.BRASS

    def render(self):
        block = (cube([hardware.BLOCK_SIDE, hardware.BLOCK_SIDE, hardware.BLOCK_TALL], center=True)
                 .translate([0, 0, -hardware.BLOCK_TALL / 2]))
        # the cone welded half a millimetre up into the block
        weld = 0.5
        tip = (curve('cylinder', r1=0.5, r2=4.0, h=hardware.NOZZLE_REACH + weld)
               .translate([0, 0, -hardware.BLOCK_TALL - hardware.NOZZLE_REACH]))
        bore = (curve('cylinder', r=hardware.FILAMENT_DIAMETER / 2 + 0.2,
                      h=hardware.BLOCK_TALL + 1.5)
                .translate([0, 0, -hardware.BLOCK_TALL - 0.5]))
        return block + tip - bore


class EffectorAssembly(AssemblyNode):
    """joint-frame-follows-declarer (ADR-097): `Kossel.render()` never
    places the effector, so its own rest frame IS the machine's, and
    these three axes are the machine's own -- no anchor, the origin
    being the effector's centre on its joint plane, the point all three
    slides are measured from."""

    slide_x = Prismatic(axis=(1, 0, 0), unit='mm')
    slide_y = Prismatic(axis=(0, 1, 0), unit='mm')
    rise = Prismatic(axis=(0, 0, 1), unit='mm')

    effector = Effector()
    shroud = Shroud()
    holder = JHeadHolder()
    nozzle = Nozzle()
    pushfit = PushFit()
    clamp_screws = M3Screw(length=CLAMP_SCREW).repeat(5)
    joint_screws = M3ButtonScrew(length=JOINT_SCREW).repeat(6)
    joint_nuts = M3Nut().repeat(6)
    balls = Ball().repeat(6)

    def render(self):
        self.effector.rotate(180, [1, 0, 0])
        # the collar seated on the pocket floor, the plate in the groove
        self.holder.translate([0, 0, -STANDOFF])
        plate_top = -STANDOFF - hardware.JHEAD_COLLAR - PLATE_STANDOFF
        self.shroud.rotate(180, [1, 0, 0]).translate([0, 0, plate_top])
        self.nozzle.translate([0, 0, self.holder.foot - 2 * STANDOFF])
        self.pushfit.translate([0, 0, STANDOFF])
        # six screws down through the effector into the clamp
        for screw, degrees in zip(self.clamp_screws, CLAMP_SCREW_ANGLES):
            angle = math.radians(degrees)
            along_minus_z(screw).translate(
                [EFFECTOR_MOUNT_RADIUS * math.cos(angle),
                 EFFECTOR_MOUNT_RADIUS * math.sin(angle),
                 4.0 + STANDOFF])
        # the three arms' joints
        for arm, angle in enumerate(TOWER_ANGLES):
            a = math.radians(angle)
            ux, uy = math.cos(a), math.sin(a)
            centre = [EFFECTOR_OFFSET * ux, EFFECTOR_OFFSET * uy, 0]
            turn = angle + 90
            for side in (-1, 1):
                index = 2 * arm + (side > 0)
                inward = along_x if side < 0 else along_minus_x
                outward = along_minus_x if side < 0 else along_x
                (outward(self.balls[index]).translate([side * BALL_STATION, 0, 0])
                 .rotate(turn, [0, 0, 1]).translate(centre))
                (inward(self.joint_screws[index]).translate([side * CLAMP_STATION, 0, 0])
                 .rotate(turn, [0, 0, 1]).translate(centre))
                (inward(self.joint_nuts[index]).translate([side * NUT_STATION, 0, 0])
                 .rotate(turn, [0, 0, 1]).translate(centre))

    @property
    def nozzle_tip(self):
        """The tip below the joint plane."""
        return self.holder.foot - 2 * STANDOFF - hardware.BLOCK_TALL - hardware.NOZZLE_REACH

    @property
    def tube_seat(self):
        """Where the Bowden tube's end sits, above the joint plane."""
        return self.pushfit.seat
