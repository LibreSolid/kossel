"""A diagonal rod: a carbon tube with a rod end at each end.

Drawn with the carriage-end socket centre on the origin and the rod
running down -Z to the effector-end socket at `-diagonal_rod`.  The
housings' axes lie along Y; the machine spins the rod about its own axis
so that they lie as near their screws as the pose allows.
"""

import math

from solid2 import cube
from solid_node.node import AssemblyNode
from solid_node.motion.joints import Prismatic, Revolute
from solid_node.parameters import Length

from simulation import hardware, materials
from simulation.part import ScadPart, curve


class Tube(ScadPart):
    """The carbon-fibre tube, along +Z from 0 to `length`."""

    color = materials.CARBON

    length = Length(min=0)

    def render(self):
        return (curve('cylinder', r=hardware.TUBE_DIAMETER / 2, h=self.length)
                - curve('cylinder', r=hardware.TUBE_BORE / 2, h=self.length + 2)
                .translate([0, 0, -1]))


class RodEnd(ScadPart):
    """A Traxxas 5347 rod end: a ring around the ball, socket centre on
    the origin, ring axis along Y, and a stem down -Z that the carbon
    tube is glued over, `ROD_END_TUBE_DEPTH` deep from the tube's end
    face at `ROD_END_REACH`.

    The socket is flared into a cone either side so that the ball's
    sleeve passes through at the swing the machine asks; the lip between
    the flares is what keeps the ball.  The stem begins well under the
    ball, because the sleeve's end sweeps 3 mm below the ball's centre at
    that swing, and it is slim, because the effector's horn is a cone the
    leaning rod has to clear.
    """

    color = materials.NYLON

    #: Where the neck under the ring ends and the stem begins.
    STEM_TOP = -hardware.BALL_DIAMETER / 2 - 1.5

    def render(self):
        radius = hardware.ROD_END_HOUSING_DIAMETER / 2
        width = hardware.ROD_END_HOUSING_WIDTH
        ring = curve('cylinder', r=radius, h=width, center=True).rotate([90, 0, 0])
        neck_top = -hardware.BALL_DIAMETER / 2 - 0.2
        neck = (cube([2.8, width, neck_top - self.STEM_TOP + 0.5])
                .translate([-1.4, -width / 2, self.STEM_TOP - 0.5]))
        stem_end = -(hardware.ROD_END_REACH + hardware.ROD_END_TUBE_DEPTH)
        stem = (curve('cylinder', r=hardware.ROD_END_STEM_DIAMETER / 2,
                      h=self.STEM_TOP - stem_end)
                .translate([0, 0, stem_end]))
        body = ring + neck + stem
        body -= curve('sphere', r=hardware.ROD_END_SOCKET / 2)
        flare = radius * 1.2
        rise = flare / math.tan(math.radians(hardware.ROD_END_FLARE))
        cone = curve('cylinder', r1=0, r2=flare, h=rise)
        body -= cone.rotate([-90, 0, 0])
        body -= cone.rotate([90, 0, 0])
        return body


class Rod(AssemblyNode):
    """joint-composition-order (ADR-093): declared spin, lean, swing,
    then rise -- innermost first -- so binding all four from one law
    (`Kossel`'s `delta_rod`) reproduces today's
    ``T(station) . Rz(azimuth) . Ry(-tilt) . Rz(spin)`` exactly.  Every
    anchor is the default origin, which is right only because a rod has
    no rest placement of its own: the carriage-end socket centre a
    Rod's own frame is drawn about (see the module docstring) IS the
    point every one of the four freedoms turns or slides about, whatever
    per-copy station `Kossel.render()` later translates it to
    (joint-frame-follows-declarer, ADR-097 -- the anchor is read in
    Rod's own undrawn frame, never the placed one).
    """

    diagonal_rod = Length(min=0)

    tube_length = diagonal_rod - Length(2 * hardware.ROD_END_REACH)

    #: About its own axis; from vertical (bound with the POSITIVE lean
    #: delta_rod returns, the axis carrying today's `-tilt` sign); toward
    #: the effector; with its carriage.
    spin = Revolute(axis=(0, 0, 1), unit='deg')
    lean = Revolute(axis=(0, -1, 0), unit='deg')
    swing = Revolute(axis=(0, 0, 1), unit='deg')
    rise = Prismatic(axis=(0, 0, 1), unit='mm')

    tube = Tube(length=tube_length)
    ends = RodEnd().repeat(2)

    def render(self):
        self.tube.rotate(180, [1, 0, 0]).translate([0, 0, -hardware.ROD_END_REACH])
        self.ends[1].rotate(180, [1, 0, 0]).translate([0, 0, -self.diagonal_rod])
