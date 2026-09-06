"""A tower's GT2 belt: the loop from the motor pulley up to the idler
and back, clamped to the carriage, as a flexible leaf.

The loop stands still -- the pulley and the idler are where the vertices
put them -- and the rubber inside it travels with the carriage, so the
belt is drawn afresh from wherever the carriage holds it rather than
placed like a part.  The wrap lives in the tower's belt plane, X across
the tower and Y up it, and the tower turns that plane onto the radial
station the idler sets.

molejo runs a wrap clockwise seen from its +Z; with the pulley first
and the idler above it, the first tangent span rises on the loop's -X
side, and that is the span the carriage's clamp is anchored on.
"""

import math

from molejo import P, Shape, Wrap
from solid_node.node import TranslationalPort
from solid_node.parameters import Length

from simulation import gt2, hardware
from simulation.layout import MOTOR_VERTEX_HEIGHT, TOP_VERTEX_HEIGHT

#: The span the carriage clamps: the rising one, from the pulley.
CLAMP_SPAN = 0

#: A picometre, past which the pulley radius iteration is called closed.
CLOSED = 1e-12

#: Rings of mesh per element of the loop.  Four elements, two of them
#: 560 mm runs of about 280 teeth: ten rings a tooth on those, which is
#: what keeps a chord across a tooth's root corner out of the tenth of a
#: millimetre the pulley is cut inside the belt.
PATH_SAMPLES = 2880


def pulley_centre():
    return [0.0, MOTOR_VERTEX_HEIGHT / 2]


def idler_centre(vertical):
    return [0.0, vertical - TOP_VERTEX_HEIGHT / 2]


def meshed_radius(vertical):
    """Where the pulley's flanks stand for teeth spaced exactly as this
    loop's are; see Metamaquina 2's `x_belt._meshed_radius`."""
    radius = gt2.pulley_radius(hardware.PULLEY_TEETH)
    while True:
        circles = [gt2.on_pulley(pulley_centre(), radius),
                   gt2.on_idler(idler_centre(vertical), hardware.BEARING_623[1] / 2)]
        closer = gt2.pulley_radius(hardware.PULLEY_TEETH, gt2.pitch(circles))
        if abs(closer - radius) < CLOSED:
            return closer
        radius = closer


class Loop:
    """The loop's arithmetic for one tower height, shared by the belt
    that draws it and the tower that turns the pulley under it."""

    def __init__(self, vertical):
        self.pulley_radius = meshed_radius(vertical)
        self.circles = [
            gt2.on_pulley(pulley_centre(), self.pulley_radius),
            gt2.on_idler(idler_centre(vertical), hardware.BEARING_623[1] / 2),
        ]
        self.period = gt2.pitch(self.circles)
        origin = gt2.span_origin(self.circles, CLAMP_SPAN)
        self.clamp_origin = origin[1]
        self.clamp_scale = gt2.span_scale(self.circles, CLAMP_SPAN)
        centre = pulley_centre()
        self.pulley_phase = math.atan2(origin[1] - centre[1], origin[0] - centre[0])

    def anchor(self, height):
        """Millimetres of belt from the start of the clamped span to a
        clamp at `height` up the tower."""
        return (height - self.clamp_origin) * self.clamp_scale

    def pulley_angle(self, height):
        """Degrees the pulley faces with the clamp at `height`: the
        tangent point's angle less the belt paid out, at the pitch
        radius, the loop running clockwise."""
        turn = self.pulley_phase - self.anchor(height) / (self.pulley_radius + gt2.PITCH_LINE)
        return turn * 180 / math.pi

    def idler_angle(self, height):
        """Degrees a plain idler bearing has turned, riding the tooth
        tips; the other way round from the pulley, being on the other
        side of the loop."""
        riding = hardware.BEARING_623[1] / 2
        return self.anchor(height) / riding * 180 / math.pi


class Belt(gt2.Belt):
    """The GT2 loop of one tower, 6 mm wide, teeth inward."""

    vertical_extrusion = Length(min=0)

    clamp = TranslationalPort(unit='mm')

    @property
    def loop(self):
        return Loop(self.vertical_extrusion)

    def render(self):
        loop = self.loop
        return Shape(
            profile=gt2.section(hardware.BELT_WIDTH),
            path=[Wrap(around=loop.circles,
                       teeth=gt2.teeth(loop.circles),
                       anchor={'span': CLAMP_SPAN, 'at': P.clamp})],
            path_samples=PATH_SAMPLES,
            profile_samples=4,
            loop=True,
        )
