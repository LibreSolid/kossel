"""The power supply brick in its two printed brackets, hung outside the
bottom beam rows.

power_supply.scad draws one bracket and ghosts the other turned about
and 30 mm up; between them the brick passes through both like a drawer,
its 50.5 face along the beam and its 30.5 face spanning the two rows.
The bracket frame: X along the beam, Y up with the lower beam's axis at
0, Z out from the beam's face.
"""

from solid2 import cube
from solid_node.node import AssemblyNode

from simulation import hardware, materials, scad
from simulation.fasteners import M3Nut, M3Screw
from simulation.layout import (
    PSU_BEAM_SCREW_X,
    PSU_BRACKET_DEPTH,
    PSU_CLAMP_SCREW_X,
    PSU_CLAMP_SCREW_Z,
    PSU_HEIGHT,
    PSU_SPACE,
    PSU_WIDTH,
)
from simulation.part import PrintedPart, ScadPart
from simulation.place import along_minus_y, along_minus_z

#: The second bracket's station up the frame: the upper row's axis.
UPPER = PSU_SPACE + 15.0

#: Screws radially into the beams' outer slots through 16 mm of bracket,
#: and the two that bolt the brackets to each other through both.
BEAM_SCREW = 20.0
CLAMP_SCREW = 40.0

#: The brick drawn a tenth inside the brackets' window.
BRICK_CLEARANCE = 0.1


class PsuBracket(PrintedPart):
    def render(self):
        return scad.power_supply.power_supply()


class Brick(ScadPart):
    """The power supply, X along the beam, Y up from its lower face, Z out
    from its inner end."""

    color = materials.PLASTIC

    def render(self):
        return (cube([PSU_WIDTH - 2 * BRICK_CLEARANCE, PSU_HEIGHT - 2 * BRICK_CLEARANCE,
                      hardware.PSU_LENGTH])
                .translate([-(PSU_WIDTH - 2 * BRICK_CLEARANCE) / 2, BRICK_CLEARANCE, 0]))


class PowerSupply(AssemblyNode):

    brackets = PsuBracket().repeat(2)
    brick = Brick()
    beam_screws = M3Screw(length=BEAM_SCREW).repeat(4)
    beam_nuts = M3Nut().repeat(4)
    clamp_screws = M3Screw(length=CLAMP_SCREW).repeat(2)
    clamp_nuts = M3Nut().repeat(2)

    def render(self):
        self.brackets[0].translate([0, 0, hardware.STANDOFF])
        (self.brackets[1].rotate(180, [0, 0, 1])
         .translate([0, UPPER, hardware.STANDOFF]))
        # the window is 30.5 tall from -0.25; the brick sits centred in it
        self.brick.translate([0, -0.25, 2 * hardware.STANDOFF])
        seats = [(x, y) for y in (0.0, UPPER) for x in (-PSU_BEAM_SCREW_X, PSU_BEAM_SCREW_X)]
        for screw, nut, (x, y) in zip(self.beam_screws, self.beam_nuts, seats):
            along_minus_z(screw).translate([x, y, PSU_BRACKET_DEPTH + 2 * hardware.STANDOFF])
            along_minus_z(nut.rotate(30, [0, 0, 1])).translate(
                [x, y, -hardware.SLOT_LIP_DEPTH - hardware.STANDOFF])
        for screw, nut, x in zip(self.clamp_screws, self.clamp_nuts, (-PSU_CLAMP_SCREW_X, PSU_CLAMP_SCREW_X)):
            top = UPPER + 4.0 + hardware.STANDOFF   # the upper bracket's top face
            along_minus_y(screw).translate([x, top, PSU_CLAMP_SCREW_Z])
            # the traps' hexagons stand with vertices along the beam
            along_minus_y(nut.rotate(30, [0, 0, 1])).translate(
                [x, -4.0 + hardware.M3_NUT + hardware.STANDOFF, PSU_CLAMP_SCREW_Z])
