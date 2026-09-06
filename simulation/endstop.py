"""The endstop at the top of each tower, and the switch on it."""

from solid_node.node import AssemblyNode

from simulation import materials, scad
from simulation.fasteners import M3Screw
from simulation.layout import ENDSTOP_THICKNESS, EXTRUSION
from simulation.part import PrintedPart, ScadPart
from simulation.place import along_minus_y

#: The endstop's screw: the drawing seats the head 3.6 in from the switch
#: side, leaving 5.4 mm of bracket, so an M3 x 8 engages its slot nut by
#: only 1.05 mm.  Drawn as the design recommends and recorded.
ENDSTOP_SCREW = 8.0
SCREW_SEAT = 3.6 - ENDSTOP_THICKNESS / 2   # in the endstop's own frame
SCREW_Z = 3.0


class Endstop(PrintedPart):
    """endstop.scad, centred: +Y is the face against the tower, -Y the
    face the microswitch hangs on."""

    def render(self):
        return scad.endstop.endstop()


class Microswitch(ScadPart):
    """microswitch.scad: the bought switch, body on the XY plane."""

    color = materials.PLASTIC

    def render(self):
        return scad.microswitch.microswitch()


class EndstopAssembly(AssemblyNode):
    """The endstop with its switch and screw, in the tower's frame with
    the endstop's centre on the origin: +Y toward the printer's centre.

    The drawing's +Y face goes against the tower, so the part is turned
    half a turn about Z; the switch and the screw follow the drawing's
    own placements through that turn.
    """

    endstop = Endstop()
    switch = Microswitch()
    screw = M3Screw(length=ENDSTOP_SCREW)

    def render(self):
        self.endstop.rotate(180, [0, 0, 1])
        # endstop.scad: translate([0, -3-thickness/2, -2]) rotate([0, 180, 0])
        (self.switch
         .rotate(180, [0, 1, 0])
         .translate([0, -3 - ENDSTOP_THICKNESS / 2 - 0.05, -2])
         .rotate(180, [0, 0, 1]))
        along_minus_y(self.screw).translate([0, -SCREW_SEAT + 0.05, SCREW_Z])
