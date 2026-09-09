"""One tower of the Kossel: everything that stands on one vertical
extrusion, in the frame `vertex.scad` is drawn in -- the extrusion's
axis on the origin, +Y toward the printer's centre, +X tangential, Z up.

Three of these stand around the machine, identical, so the tower is one
declaration repeated and the machine tells each where its carriage is
through the `height` port.  What moves on a tower is the carriage on its
block, and with it the belt's teeth and the pulley and idlers they run
over; everything else is frame.
"""

from solid_node.node import AssemblyNode
from solid_node.motion.ports import TranslationalPort
from solid_node.parameters import Length

from simulation import hardware, layout
from simulation.belt import Belt
from simulation.carriage import CarriageAssembly
from simulation.endstop import EndstopAssembly
from simulation.extrusion import Extrusion
from simulation.fasteners import Bearing, M3Nut, M3Screw
from simulation.layout import (
    BEAM_SCREW_FACE,
    BEAM_SCREW_STATIONS,
    CARRIAGE_HORN_Y,
    ENDSTOP_HEIGHT,
    ENDSTOP_THICKNESS,
    EXTRUSION,
    IDLER_STATION,
    MOTOR_OFFSET,
    MOTOR_VERTEX_HEIGHT,
    SCREW_HEAD_SEAT,
    TOP_VERTEX_HEIGHT,
    VERTEX_BEAM_ANGLE,
    VERTEX_SCREW_PITCH,
    VERTICAL_SCREW_SEAT,
)
from simulation.motor import GT2Pulley, Nema17
from simulation.place import along_minus_x, along_minus_y, along_x, along_y
from simulation.rail import RAIL_COUNTERBORE, Rail, rail_holes
from simulation.vertices import MotorVertex, TopVertex

#: The frame's screws: M3 x 8 into the slots, as the design recommends.
FRAME_SCREW = 8.0

#: The motor's four screws, through the vertex's 4 mm wall into the
#: motor's tapped holes.
MOTOR_SCREW = 8.0
MOTOR_SCREW_SEAT = 40.0          # the wall's tower-side face
MOTOR_SCREW_SPACING = 15.5       # nema17.scad

#: The idler bolt: frame_top.scad drills from y = 65 down to y = 10 and
#: the cone it enters begins at 59, so an M3 x 50 seated there reaches 9.
IDLER_BOLT = 50.0
IDLER_BOLT_SEAT = 59.0

#: How far a slot nut, and the motor's face, are drawn off the faces
#: they are pulled against, so the pairs can be asked whether they touch.
STANDOFF = 0.05

#: Rail screw stations declared, more than a 400 mm rail has; the extra
#: ones are omitted.
RAIL_SCREW_SLOTS = 24


def screw_stations(vertical):
    """Heights of the vertex screw rows: two through the motor vertex, one
    through the top vertex -- `for (z = [0:30:height])` in vertex.scad."""
    stations = [EXTRUSION / 2 + step * VERTEX_SCREW_PITCH
                for step in range(int(MOTOR_VERTEX_HEIGHT // VERTEX_SCREW_PITCH) + 1)]
    stations.append(vertical - TOP_VERTEX_HEIGHT / 2)
    return stations


def rail_top(vertical):
    """The rail ends under the endstop, which sits under the top vertex."""
    return vertical - TOP_VERTEX_HEIGHT - ENDSTOP_HEIGHT - 2 * STANDOFF


def home_height(vertical):
    """The carriage joint height at home: the carriage's horns, which
    stand above its block, `HOME_GAP` under the switch lever hanging
    below the endstop's centre."""
    endstop_centre = vertical - TOP_VERTEX_HEIGHT - ENDSTOP_HEIGHT / 2
    carriage_top = endstop_centre - layout.SWITCH_LEVER_DROP - layout.HOME_GAP
    return carriage_top - layout.CARRIAGE_TOP + CARRIAGE_HORN_Y


class Tower(AssemblyNode):

    #: The design's own values, so a tower builds and tests on its own;
    #: the machine passes its knobs down over them.
    vertical_extrusion = Length(layout.DEFAULT_VERTICAL, min=0)
    rail_length = Length(layout.DEFAULT_RAIL, min=0)

    extrusion = Extrusion(length=vertical_extrusion)
    motor_vertex = MotorVertex()
    top_vertex = TopVertex()
    vertical_screws = M3Screw(length=FRAME_SCREW).repeat(3)
    vertical_nuts = M3Nut().repeat(3)
    beam_screws = M3Screw(length=FRAME_SCREW).repeat(12)
    beam_nuts = M3Nut().repeat(12)

    rail = Rail(length=rail_length)
    rail_screws = M3Screw(length=FRAME_SCREW).repeat(RAIL_SCREW_SLOTS)
    rail_nuts = M3Nut().repeat(RAIL_SCREW_SLOTS)
    carriage = CarriageAssembly()
    endstop = EndstopAssembly()
    endstop_nut = M3Nut()

    motor = Nema17()
    motor_screws = M3Screw(length=MOTOR_SCREW).repeat(4)
    pulley = GT2Pulley()
    idler_bolt = M3Screw(length=IDLER_BOLT)
    idlers = Bearing(bore=hardware.BEARING_623[0], outer=hardware.BEARING_623[1],
                     width=hardware.BEARING_623[2]).repeat(2)
    belt = Belt(vertical_extrusion=vertical_extrusion)

    #: Where the machine holds this tower's carriage: the height of the
    #: ball-joint axis on the carriage horns.
    height = TranslationalPort(unit='mm')

    def render(self):
        vertical = self.vertical_extrusion
        top_centre = vertical - TOP_VERTEX_HEIGHT / 2
        face = EXTRUSION / 2
        nut_seat = face - hardware.SLOT_LIP_DEPTH - STANDOFF

        # the vertices and their screws
        self.motor_vertex.translate([0, 0, MOTOR_VERTEX_HEIGHT / 2])
        self.top_vertex.translate([0, 0, top_centre])
        stations = screw_stations(vertical)
        for screw, nut, z in zip(self.vertical_screws, self.vertical_nuts, stations):
            along_y(screw).translate([0, -VERTICAL_SCREW_SEAT - STANDOFF, z])
            along_y(nut).translate([0, -nut_seat, z])
        seats = [(side, station, z)
                 for side in (1, -1)
                 for station in BEAM_SCREW_STATIONS
                 for z in stations]
        for (side, station, z), screw, nut in zip(seats, self.beam_screws, self.beam_nuts):
            aim = along_minus_x if side > 0 else along_x
            (aim(screw)
             .translate([-side * (BEAM_SCREW_FACE - SCREW_HEAD_SEAT - STANDOFF), station, z])
             .rotate(side * VERTEX_BEAM_ANGLE, [0, 0, 1]))
            (aim(nut)
             .translate([-side * (BEAM_SCREW_FACE + layout.BEAM_STANDOFF
                                  + hardware.SLOT_LIP_DEPTH + STANDOFF), station, z])
             .rotate(side * VERTEX_BEAM_ANGLE, [0, 0, 1]))

        # the rail on the inner face, screwed into its slot
        bottom = rail_top(vertical) - self.rail_length
        self.rail.translate([0, face + STANDOFF, bottom])
        holes = rail_holes(self.rail_length)
        seat = face + hardware.RAIL_HEIGHT - RAIL_COUNTERBORE + 2 * STANDOFF
        for index, (screw, nut) in enumerate(zip(self.rail_screws, self.rail_nuts)):
            if index >= len(holes):
                screw.omit()
                nut.omit()
                continue
            z = bottom + holes[index]
            along_minus_y(screw).translate([0, seat, z])
            along_minus_y(nut).translate([0, nut_seat, z])

        # the carriage rides the rail: its Y is fixed, its Z is the machine's
        self.carriage.translate([0, face, 0])

        # the endstop under the top vertex, its switch toward the centre
        endstop_centre = vertical - TOP_VERTEX_HEIGHT - ENDSTOP_HEIGHT / 2
        self.endstop.translate([0, face + ENDSTOP_THICKNESS / 2 + STANDOFF,
                                endstop_centre - STANDOFF])
        along_minus_y(self.endstop_nut).translate([0, nut_seat, endstop_centre + 3.0])

        # the motor in the bottom vertex, shaft toward the tower
        motor_centre = MOTOR_VERTEX_HEIGHT / 2
        (self.motor.rotate(90, [1, 0, 0])
         .translate([0, MOTOR_OFFSET + STANDOFF, motor_centre]))
        for screw, (x, z) in zip(self.motor_screws, [(-1, -1), (1, -1), (-1, 1), (1, 1)]):
            along_y(screw).translate([x * MOTOR_SCREW_SPACING, MOTOR_SCREW_SEAT - STANDOFF,
                                      motor_centre + z * MOTOR_SCREW_SPACING])

        # the pulley on the shaft, teeth at the idler's station
        teeth_centre = self.pulley.teeth_start + hardware.PULLEY_WIDTH / 2
        (self.pulley.rotate(90, [1, 0, 0])
         .translate([0, IDLER_STATION + teeth_centre, motor_centre]))

        # the idler bolt through the top vertex's cones, two bearings on it
        along_minus_y(self.idler_bolt).translate([0, IDLER_BOLT_SEAT + 2 * STANDOFF, top_centre])
        width = hardware.BEARING_623[2]
        for bearing, y in zip(self.idlers, (IDLER_STATION, IDLER_STATION + width)):
            along_minus_y(bearing).translate([0, y, top_centre])

        # the belt plane, its width running out from the idler's far edge
        (self.belt.rotate(90, [1, 0, 0])
         .translate([0, IDLER_STATION + hardware.BELT_WIDTH / 2, 0]))

    def simulate(self):
        """Put the carriage where the machine says, and let the belt, the
        pulley and the idlers follow it.

        Built on its own, with nothing bound, the tower stands its
        carriage at the machine's default pose so it can be tested alone;
        that is the one place an unbound port is not a fault, and it is
        stated here so it is not mistaken for a wiring default.
        """
        height = self.height.value
        if height is None:
            height = layout.DEFAULT_CARRIAGE_HEIGHT
        block = height - CARRIAGE_HORN_Y
        self.carriage.translate([0, 0, block])

        loop = self.belt.loop
        self.connect(loop.anchor(block), self.belt.clamp)
        self.pulley.rotate(loop.pulley_angle(block), [0, 0, 1])
        for bearing in self.idlers:
            bearing.rotate(loop.idler_angle(block), [0, 0, 1])
