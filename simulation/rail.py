"""The MGN12 linear rail and its MGN12H block."""

from solid2 import cube
from solid_node.parameters import Length

from simulation import hardware, materials
from simulation.part import ScadPart, curve

#: The rail's counterbores are drawn 3.5 deep rather than the
#: catalogue's 4.5, so that an M3 x 8 through 4.5 mm of rail reaches its
#: slot nut without meeting the slot's back.
RAIL_COUNTERBORE = 3.5
RAIL_COUNTERBORE_DIAMETER = 6.0
RAIL_HOLE = 3.5


def rail_holes(length):
    """Where the rail's mounting holes fall along it."""
    holes = []
    station = hardware.RAIL_HOLE_FIRST
    while station <= length - hardware.RAIL_HOLE_FIRST + 0.01:
        holes.append(station)
        station += hardware.RAIL_HOLE_PITCH
    return holes


class Rail(ScadPart):
    """12 x 8 rail along +Z from 0 to `length`, base on the XY plane,
    counterbored from its top for M3 screws."""

    color = materials.ALUMINIUM

    length = Length(min=0)

    def render(self):
        body = (cube([hardware.RAIL_WIDTH, hardware.RAIL_HEIGHT, self.length])
                .translate([-hardware.RAIL_WIDTH / 2, 0, 0]))
        for z in rail_holes(self.length):
            body -= (curve('cylinder', r=RAIL_HOLE / 2, h=hardware.RAIL_HEIGHT + 2)
                     .translate([0, 0, -1]).rotate([-90, 0, 0]).translate([0, 0, z]))
            body -= (curve('cylinder', r=RAIL_COUNTERBORE_DIAMETER / 2,
                           h=RAIL_COUNTERBORE + 1)
                     .rotate([-90, 0, 0])
                     .translate([0, hardware.RAIL_HEIGHT - RAIL_COUNTERBORE, z]))
        return body


class Block(ScadPart):
    """The MGN12H block astride its rail: rail base on the XY plane,
    length along Z centred on the origin, the carriage's four M3 holes
    tapped from its top."""

    color = materials.STEEL

    def render(self):
        body = (cube([hardware.BLOCK_WIDTH,
                      hardware.BLOCK_HEIGHT - hardware.BLOCK_UNDERSIDE,
                      hardware.BLOCK_LENGTH], center=True)
                .translate([0, (hardware.BLOCK_HEIGHT + hardware.BLOCK_UNDERSIDE) / 2, 0]))
        # the rail stands a standoff off the tower face; the channel's roof
        # keeps its clearance over that
        roof = hardware.RAIL_HEIGHT + hardware.STANDOFF + hardware.FIT
        channel = (cube([hardware.RAIL_WIDTH + 2 * hardware.FIT, roof + 1,
                         hardware.BLOCK_LENGTH + 2], center=True)
                   .translate([0, (roof - 1) / 2, 0]))
        body -= channel
        half = hardware.BLOCK_HOLE_PATTERN / 2
        for x in (-half, half):
            for z in (-half, half):
                body -= (curve('cylinder', r=hardware.M3_SHANK / 2 + hardware.FIT, h=6)
                         .rotate([-90, 0, 0])
                         .translate([x, hardware.BLOCK_HEIGHT - 5, z]))
        return body
