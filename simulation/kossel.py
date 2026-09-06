"""The Mini Kossel, as an assembly.

Johann's repository draws the printed parts, flat, one per file; this
package reads them into the machine.  The frame is three towers and nine
beams; each tower carries its carriage, belt, motor and idler; the
effector hangs from the carriages on six rods; the extruder sits on the
top frame and feeds the hot end through a Bowden tube.

The drivers are the printer's own coordinates -- `x` and `y` over the
glass, `z` the nozzle above it -- and everything else follows: three
carriage heights from the delta kinematics, six rod angles, three belts
redrawn from where their carriages hold them, three pulleys turned.
"""

import math

from solid_node.math import asin, cos, sin
from solid_node.node import AssemblyNode
from solid_node.parameters import Length
from solid_node.simulation import Driver, Instruction

from simulation import hardware, kinematics, layout
from simulation.bed import Bed
from simulation.bowden import BowdenTube, Filament
from simulation.effector import EffectorAssembly
from simulation.extruder import Extruder
from simulation.extrusion import Extrusion
from simulation.power_supply import PowerSupply
from simulation.layout import (
    BEAM_END_WINDOW,
    BEAM_STANDOFF,
    BOTTOM_ROWS,
    EXTRUSION,
    PRINTABLE_RADIUS,
    VERTEX_BEAM_OFFSET,
    TOP_VERTEX_HEIGHT,
    TOWER_ANGLES,
    TOWER_NAMES,
    VERTEX_BEAM_ANGLE,
    beam_end_inset,
    beam_point,
    radial,
    tangential,
    tower_frame,
)
from simulation.carriage import BALL_STATION
from simulation.place import along_y
from simulation.rod import Rod
from simulation.tower import Tower, home_height

#: The top of the travel at the default parameters: the nozzle height
#: with every carriage at home.  A driver range must be a number.
Z_MAX = (home_height(layout.DEFAULT_VERTICAL)
         - (layout.DEFAULT_CARRIAGE_HEIGHT - layout.joint_plane(layout.DEFAULT_Z))
         - layout.NOZZLE_DROP - layout.GLASS_TOP)

#: Where the instructions send the head under each tower: the print
#: radius out, low over the glass.
TOWER_TARGET_Z = 20.0


def _toward(angle, radius, z):
    return {'x': radius * math.cos(math.radians(angle)),
            'y': radius * math.sin(math.radians(angle)),
            'z': z}


class Kossel(AssemblyNode):

    #: Marlin's DELTA_SMOOTH_ROD_OFFSET: centre to the tower's inner face.
    tower_radius = Length(layout.DEFAULT_TOWER_RADIUS, min=0)
    #: The OpenBeam cut lengths.
    vertical_extrusion = Length(layout.DEFAULT_VERTICAL, min=0)
    horizontal_extrusion = Length(layout.DEFAULT_HORIZONTAL, min=0)
    #: Marlin's DELTA_DIAGONAL_ROD: ball centre to ball centre.
    diagonal_rod = Length(layout.DEFAULT_ROD, min=0)
    #: The MGN12 rails.
    rail_length = Length(layout.DEFAULT_RAIL, min=0)

    #: Where the extrusions' axes stand, where the carriage joints stand,
    #: and how far the effector's joints stand inside them: the delta radius.
    axis_radius = tower_radius + Length(EXTRUSION / 2)
    joint_radius = tower_radius - Length(layout.CARRIAGE_OFFSET)
    delta_radius = tower_radius - Length(layout.CARRIAGE_OFFSET + layout.EFFECTOR_OFFSET)
    #: How far from the centre the horizontal beams' axes run.
    beam_distance = axis_radius / 2 + Length(VERTEX_BEAM_OFFSET + BEAM_STANDOFF)

    x = Driver(default=0.0, unit='mm', range=(-PRINTABLE_RADIUS, PRINTABLE_RADIUS))
    y = Driver(default=0.0, unit='mm', range=(-PRINTABLE_RADIUS, PRINTABLE_RADIUS))
    z = Driver(default=layout.DEFAULT_Z, unit='mm', range=(0.0, Z_MAX))

    instructions = {
        'Home': Instruction({'x': 0.0, 'y': 0.0, 'z': Z_MAX}, duration=3.0),
        'Center': Instruction({'x': 0.0, 'y': 0.0, 'z': layout.DEFAULT_Z}, duration=2.0),
        'Bed': Instruction({'x': 0.0, 'y': 0.0, 'z': 0.0}, duration=2.0),
        **{f'Tower{name}': Instruction(_toward(angle, PRINTABLE_RADIUS, TOWER_TARGET_Z),
                                       duration=2.0)
           for name, angle in zip(TOWER_NAMES, TOWER_ANGLES)},
    }

    towers = Tower(vertical_extrusion=vertical_extrusion,
                   rail_length=rail_length).repeat(3)
    beams = Extrusion(length=horizontal_extrusion).repeat(9)
    effector = EffectorAssembly()
    rods = Rod(diagonal_rod=diagonal_rod).repeat(6)
    bed = Bed(beam_distance=beam_distance)
    extruder = Extruder()
    power_supply = PowerSupply()
    bowden = BowdenTube()
    filament = Filament()

    #: The extruder hangs on the front top beam, between towers X and Y;
    #: the power supply on the rear-left bottom beams, between Z and X.
    EXTRUDER_BEAM = 270.0
    POWER_SUPPLY_BEAM = 150.0

    def check(self):
        inset = beam_end_inset(self.axis_radius, self.horizontal_extrusion)
        low, high = BEAM_END_WINDOW
        if not low <= inset <= high:
            raise ValueError(
                f'a tower radius of {self.tower_radius} puts the end of a '
                f'{self.horizontal_extrusion} mm beam {inset:.1f} mm along the '
                f'vertex beam line; the vertex holds a beam ending between '
                f'{low} and {high}')

    def tower_position(self, angle):
        ux, uy = radial(angle)
        return [self.axis_radius * ux, self.axis_radius * uy, 0]

    @property
    def extruder_position(self):
        """The extruder assembly's origin: the front top beam's axis
        midpoint on its top face."""
        return [0.0, -self.beam_distance, self.vertical_extrusion]

    @property
    def tube_start(self):
        seat = self.extruder.tube_seat
        origin = self.extruder_position
        return [origin[axis] + seat[axis] for axis in range(3)]

    @property
    def filament_entry(self):
        entry = self.extruder.filament_entry
        origin = self.extruder_position
        return [origin[axis] + entry[axis] for axis in range(3)]

    def render(self):
        for tower, angle in zip(self.towers, TOWER_ANGLES):
            tower.rotate(tower_frame(angle), [0, 0, 1]).translate(self.tower_position(angle))

        inset = beam_end_inset(self.axis_radius, self.horizontal_extrusion)
        rows = BOTTOM_ROWS + (self.vertical_extrusion - TOP_VERTEX_HEIGHT,)
        px, py = beam_point(inset)
        for index, beam in enumerate(self.beams):
            angle = TOWER_ANGLES[index // 3]
            row = rows[index % 3]
            (along_y(beam)
             .rotate(VERTEX_BEAM_ANGLE, [0, 0, 1])
             .translate([px, py, row + EXTRUSION / 2])
             .rotate(tower_frame(angle), [0, 0, 1])
             .translate(self.tower_position(angle)))

        self.extruder.translate(self.extruder_position)

        # the power supply's bracket frame: X along its beam, Y up from the
        # lower row's axis, Z out from the beams' outer face
        ux, uy = radial(self.POWER_SUPPLY_BEAM)
        outer = self.beam_distance + EXTRUSION / 2
        (self.power_supply.rotate(90, [1, 0, 0])
         .rotate(self.POWER_SUPPLY_BEAM - 270.0, [0, 0, 1])
         .translate([outer * ux, outer * uy, BOTTOM_ROWS[0] + EXTRUSION / 2]))

        self.bowden.translate(self.tube_start)
        self.filament.translate(self.filament_entry)

    def simulate(self):
        """Put the head where the drivers say and hang everything on it.

        Each tower is told its carriage height; each rod is spun about its
        own axis so its housings lie along their screws as far as the
        pose allows, tilted from vertical and swung to the effector, and
        stood on its carriage ball.
        """
        plane = layout.joint_plane(self.z)
        self.effector.translate([self.x, self.y, plane])

        # the tube's far end: the effector push-fit's seat, read in the
        # tube's own frame; the filament's, in the strand's
        seat = plane + self.effector.tube_seat + hardware.STANDOFF
        melt = plane - layout.NOZZLE_DROP + 5.0
        start, entry = self.tube_start, self.filament_entry
        self.connect(self.x - start[0], self.bowden.head_x)
        self.connect(self.y - start[1], self.bowden.head_y)
        self.connect(seat - start[2], self.bowden.head_z)
        self.connect(self.x - entry[0], self.filament.head_x)
        self.connect(self.y - entry[1], self.filament.head_y)
        self.connect(seat - entry[2], self.filament.head_z)
        self.connect(melt - entry[2], self.filament.melt_z)

        for index, (tower, angle) in enumerate(zip(self.towers, TOWER_ANGLES)):
            height = kinematics.carriage_height(
                self.x, self.y, plane, self.diagonal_rod, self.delta_radius, angle)
            self.connect(height, tower.height)

            tilt = kinematics.rod_tilt(self.x, self.y, self.diagonal_rod,
                                       self.delta_radius, angle)
            azimuth = kinematics.rod_azimuth(self.x, self.y, self.delta_radius, angle)
            spin = asin(sin(azimuth - angle) * cos(tilt))
            ux, uy = radial(angle)
            vx, vy = tangential(angle)
            for side, rod in zip((-1, 1), self.rods[2 * index:2 * index + 2]):
                (rod.rotate(spin, [0, 0, 1])
                 .rotate(-tilt, [0, 1, 0])
                 .rotate(azimuth, [0, 0, 1])
                 .translate([self.joint_radius * ux + side * BALL_STATION * vx,
                             self.joint_radius * uy + side * BALL_STATION * vy,
                             height]))
