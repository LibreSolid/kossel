"""The two printed vertices of a tower.

Both are `vertex.scad` with a height and a use, drawn centred on their
own height.  Both come off the printer with two 0.5 mm pads under their
slim ends -- "Pads to improve print bed adhesion" -- that reach 6 mm past
the beam faces; a builder cuts them off before the beams go on, and so
does this layer: the part in the machine is the part after that cut.
"""

from solid2 import cube

from simulation import scad
from simulation.layout import BEAM_SCREW_FACE, VERTEX_BEAM_ANGLE
from simulation.part import PrintedPart

PAD = 0.5


def trimmed(part, height):
    """`part` with everything beyond its two beam faces in the bottom
    `PAD` removed: the adhesion pads, and nothing else lives there."""
    for side in (1, -1):
        knife = (cube([40, 200, PAD + 1], center=True)
                 .translate([-side * (BEAM_SCREW_FACE + 20), 0,
                             -height / 2 + (PAD + 1) / 2 - 1])
                 .rotate([0, 0, side * VERTEX_BEAM_ANGLE]))
        part = part - knife
    return part


class MotorVertex(PrintedPart):
    """frame_motor.scad: three extrusions tall, cradling the NEMA 17."""

    HEIGHT = 45.0

    def render(self):
        return trimmed(scad.frame_motor.frame_motor(), self.HEIGHT)


class TopVertex(PrintedPart):
    """frame_top.scad: one extrusion tall, with the idler cones and the
    belt tensioner."""

    HEIGHT = 15.0

    def render(self):
        return trimmed(scad.frame_top.frame_top(), self.HEIGHT)
