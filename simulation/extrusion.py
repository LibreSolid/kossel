"""OpenBeam 15 x 15, the frame's stock, cut to a declared length."""

from solid2 import square
from solid_node.parameters import Length

from simulation import hardware, materials
from simulation.layout import EXTRUSION
from simulation.part import ScadPart


def profile():
    """The 15 x 15 section with its four T-slots, centred.

    The opening is drawn for the 6 x 2.5 tabs the vertex carries into it
    and the cavity behind it for an M3 nut; see `hardware`.
    """
    section = square([EXTRUSION, EXTRUSION], center=True)
    for angle in (0, 90, 180, 270):
        opening = (square([hardware.SLOT_OPENING, hardware.SLOT_LIP_DEPTH + 0.01],
                          center=True)
                   .translate([0, EXTRUSION / 2 - hardware.SLOT_LIP_DEPTH / 2]))
        cavity_depth = hardware.SLOT_DEPTH - hardware.SLOT_LIP_DEPTH
        cavity = (square([hardware.SLOT_CAVITY, cavity_depth], center=True)
                  .translate([0, EXTRUSION / 2 - hardware.SLOT_LIP_DEPTH
                              - cavity_depth / 2]))
        section -= (opening + cavity).rotate([0, 0, angle])
    return section


class Extrusion(ScadPart):
    """A length of OpenBeam, drawn along +Z from 0 to `length`."""

    color = materials.ALUMINIUM

    length = Length(min=0)

    def render(self):
        return profile().linear_extrude(self.length)
