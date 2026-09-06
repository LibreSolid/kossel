"""The print surface: a round glass on three printed tabs.

Each tab is screwed into the top slot of an upper bottom beam at its
midpoint, round end out over the beam's outer face and pad end in; the
glass rests on the three adhesive pads.  glass_tab.scad draws the pad
and the beam as background, so the pad is a part here and the beam is
the frame's.
"""

import math

from solid2 import cube
from solid_node.node import AssemblyNode
from solid_node.parameters import Length

from simulation import hardware, materials, scad
from simulation.fasteners import M3Nut, M3Screw
from simulation.layout import (
    BOTTOM_ROWS,
    EXTRUSION,
    TAB_PAD,
    TAB_STICKY,
    TAB_STICKY_OFFSET,
    TAB_THICKNESS,
    TOWER_ANGLES,
)
from simulation.part import PrintedPart, ScadPart, curve
from simulation.place import along_minus_z

#: The beams the tabs sit on: the upper of the two bottom rows.
TAB_ROW = BOTTOM_ROWS[1]

#: The tab's screw: M3 x 8 through 3.6 of tab into the slot, as the
#: design recommends for its 3.6 mm brackets.
TAB_SCREW = 8.0


class GlassTab(PrintedPart):
    """glass_tab.scad, centred on its thickness, screw hole on the origin,
    pad end along +Y."""

    def render(self):
        return scad.glass_tab.glass_tab()


class Pad(ScadPart):
    """The restickable adhesive pad, 25.4 square, on the XY plane."""

    color = materials.PTFE

    def render(self):
        return (cube([TAB_STICKY, TAB_STICKY, TAB_PAD])
                .translate([-TAB_STICKY / 2, 0, 0]))


class Glass(ScadPart):
    """The round glass, on the XY plane."""

    color = materials.GLASS

    def render(self):
        return curve('cylinder', r=hardware.GLASS_DIAMETER / 2, h=hardware.GLASS)


class Bed(AssemblyNode):
    """Tabs, pads, screws, nuts and glass in the machine's frame, for a
    frame whose beam axes stand `beam_distance` from the centre."""

    beam_distance = Length(min=0)

    tabs = GlassTab().repeat(3)
    pads = Pad().repeat(3)
    screws = M3Screw(length=TAB_SCREW).repeat(3)
    nuts = M3Nut().repeat(3)
    glass = Glass()

    def render(self):
        top = TAB_ROW + EXTRUSION
        tab_base = top + hardware.STANDOFF
        for tab, pad, screw, nut, angle in zip(
                self.tabs, self.pads, self.screws, self.nuts, TOWER_ANGLES):
            # the beam from this tower toward the one 120 degrees on has
            # its midpoint on the bisector, 60 degrees back
            mid = angle - 60.0
            ux, uy = math.cos(math.radians(mid)), math.sin(math.radians(mid))
            station = [self.beam_distance * ux, self.beam_distance * uy, 0]
            turn = mid + 90.0   # the tab's +Y toward the centre
            (tab.rotate(turn, [0, 0, 1])
             .translate([station[0], station[1], tab_base + TAB_THICKNESS / 2]))
            (pad.translate([0, TAB_STICKY_OFFSET, 0]).rotate(turn, [0, 0, 1])
             .translate([station[0], station[1],
                         tab_base + TAB_THICKNESS + hardware.STANDOFF]))
            along_minus_z(screw).translate(
                [station[0], station[1], tab_base + TAB_THICKNESS + hardware.STANDOFF])
            nut_top = top - hardware.SLOT_LIP_DEPTH - hardware.STANDOFF
            (along_minus_z(nut.rotate(30, [0, 0, 1])).rotate(turn, [0, 0, 1])
             .translate([station[0], station[1], nut_top]))
        self.glass.translate(
            [0, 0, tab_base + TAB_THICKNESS + hardware.STANDOFF + TAB_PAD + hardware.STANDOFF])

