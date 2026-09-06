"""Screws, nuts, balls and bearings: the small steel of the machine.

Every part here is drawn along its own +Z.  A screw's head is below
z = 0 and its shank runs up from there, so `translate` puts the head's
seat where the plastic is; a nut and a bearing run from z = 0 to their
thickness; a ball is centred.  Threads are represented by the shank at
the design's own major diameter and the bore a fit over it.
"""

import math

from solid2 import cylinder, sphere
from solid_node.parameters import Length

from simulation import hardware, materials
from simulation.part import ScadPart, curve


def hexagon(flats, height):
    """A hex prism of `flats` across flats, vertices on +-Y so the flats
    face +-X, from z = 0 to `height`."""
    return cylinder(r=flats / math.sqrt(3), h=height, _fn=6).rotate([0, 0, 30])


class M3Screw(ScadPart):
    """An ISO 4762 M3 socket cap screw, shank of `length`."""

    color = materials.STEEL

    length = Length(min=0)

    def render(self):
        head = (curve('cylinder', r=hardware.M3_HEAD_DIAMETER / 2,
                      h=hardware.M3_HEAD)
                .translate([0, 0, -hardware.M3_HEAD]))
        shank = curve('cylinder', r=hardware.M3_SHANK / 2, h=self.length)
        return head + shank


class M3ButtonScrew(ScadPart):
    """An ISO 7380 M3 button-head screw, shank of `length`."""

    color = materials.STEEL

    length = Length(min=0)

    def render(self):
        head = (curve('cylinder', r=hardware.M3_BUTTON_HEAD_DIAMETER / 2,
                      h=hardware.M3_BUTTON_HEAD)
                .translate([0, 0, -hardware.M3_BUTTON_HEAD]))
        shank = curve('cylinder', r=hardware.M3_SHANK / 2, h=self.length)
        return head + shank


class M5Screw(ScadPart):
    color = materials.STEEL

    length = Length(min=0)

    def render(self):
        head = (curve('cylinder', r=hardware.M5_HEAD_DIAMETER / 2,
                      h=hardware.M5_HEAD)
                .translate([0, 0, -hardware.M5_HEAD]))
        shank = curve('cylinder', r=hardware.M5_SHANK / 2, h=self.length)
        return head + shank


class M3Nut(ScadPart):
    color = materials.STEEL

    def render(self):
        return (hexagon(hardware.M3_NUT_FLATS, hardware.M3_NUT)
                - curve('cylinder', r=hardware.M3_SHANK / 2 + hardware.FIT,
                        h=3 * hardware.M3_NUT, center=True))


class M5Nut(ScadPart):
    color = materials.STEEL

    def render(self):
        return (hexagon(hardware.M5_NUT_FLATS, hardware.M5_NUT)
                - curve('cylinder', r=hardware.M5_SHANK / 2 + hardware.FIT,
                        h=3 * hardware.M5_NUT, center=True))


class Ball(ScadPart):
    """The hollow ball of a rod-end joint: a 6 mm ball on a sleeve, bored
    for its M3 screw, centred on the ball with the sleeve along Z -- the
    long end toward -Z, which an assembly points at the horn."""

    color = materials.STEEL

    def render(self):
        length = hardware.BALL_SLEEVE_IN + hardware.BALL_SLEEVE_OUT
        sleeve = (curve('cylinder', r=hardware.BALL_SLEEVE_DIAMETER / 2, h=length)
                  .translate([0, 0, -hardware.BALL_SLEEVE_IN]))
        return (curve('sphere', r=hardware.BALL_DIAMETER / 2) + sleeve
                - curve('cylinder', r=hardware.BALL_BORE / 2,
                        h=3 * length, center=True))


class Bearing(ScadPart):
    """A shielded ball bearing as its steel envelope: a ring from z = 0
    to its width."""

    color = materials.STEEL

    bore = Length(min=0)
    outer = Length(min=0)
    width = Length(min=0)

    def render(self):
        return (curve('cylinder', r=self.outer / 2, h=self.width)
                - curve('cylinder', r=self.bore / 2, h=3 * self.width, center=True))
