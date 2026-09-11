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
from solid_node_mechanics import delta_carriage as _delta_carriage, delta_rod as _delta_rod
from solid_node.node import AssemblyNode
from solid_node.parameters import Length
from solid_node.simulation import Driver, Instruction

from simulation import hardware, layout
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


#: multi-source-multi-target-laws (ADR-100): the two laws behind
#: `(x & y & z).drives(towers.height, law=delta_carriage_law)` and
#: `(x & y & z).drives((rods.spin, rods.lean, rods.swing, rods.rise),
#: law=delta_rod)`.  Each is handed the sources' shared owner (`Kossel`
#: itself, `x`, `y` and `z` all being its own drivers) and the driven
#: end's owner -- a `Tower` copy for the first, the tuple of one `Rod`
#: copy repeated four times for the second, `.repeat()`'s own broadcast
#: calling each once per copy -- and returns a `forward` of exactly the
#: three source VALUES, in written order, giving back one value or the
#: four in written order.  `solid_node_mechanics.delta_carriage` and
#: `delta_rod` stay the prescribed law of three drivers over three
#: towers; only the class-level connect() loop that fed them by hand is
#: gone.
def delta_carriage_law(sources, tower):
    kossel = sources[0]
    angle = TOWER_ANGLES[tower.index]

    def forward(x, y, z):
        plane = layout.joint_plane(z)
        return _delta_carriage(x, y, kossel.diagonal_rod, kossel.delta_radius,
                               angle, plane=plane)
    return forward


def delta_rod(sources, rods):
    kossel = sources[0]
    angle = TOWER_ANGLES[rods[0].index // 2]

    def forward(x, y, z):
        plane = layout.joint_plane(z)
        tilt, azimuth = _delta_rod(x, y, kossel.diagonal_rod, kossel.delta_radius, angle)
        spin = asin(sin(azimuth - angle) * cos(tilt))
        height = _delta_carriage(x, y, kossel.diagonal_rod, kossel.delta_radius,
                                 angle, plane=plane)
        return spin, tilt, azimuth, height
    return forward


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

    #: The effector's three coordinates ARE the drivers.
    x.drives(effector.slide_x)
    y.drives(effector.slide_y)
    z.drives(effector.rise, offset=layout.GLASS_TOP + layout.NOZZLE_DROP)

    #: multi-source-multi-target-laws (ADR-100): the delta kinematics
    #: read all three drivers and drive three towers' heights and six
    #: rods' four freedoms each, the law called once per copy under the
    #: `.repeat()` broadcast (repeat-fan-out, ADR-096).  These replace
    #: the per-tower `connect(height, tower.height)` loop and the six
    #: rods' rotate/rotate/rotate/translate chains this project deferred
    #: at stage A; the per-rod station translate stays, in `render()`
    #: now (see below), because it is the rest placement and not a
    #: freedom.
    (x & y & z).drives(towers.height, law=delta_carriage_law)
    (x & y & z).drives((rods.spin, rods.lean, rods.swing, rods.rise), law=delta_rod)

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

        # each rod's ball hangs at a constant (x, y) per copy: the rest
        # placement its own class has none of (Rod has no rest
        # placement of its own; see its docstring), and no freedom --
        # joint-frame-follows-declarer (ADR-097) means a Rod's own
        # joints stay anchored at ITS OWN origin (the carriage-end
        # socket centre) however this translate places it, so this can
        # live here now instead of Kossel.simulate() (deferred stage A
        # "Known gap 2": moved once site/own-frame joints made it safe).
        for index, rod in enumerate(self.rods):
            angle = TOWER_ANGLES[index // 2]
            side = -1 if index % 2 == 0 else 1
            ux, uy = radial(angle)
            vx, vy = tangential(angle)
            rod.translate([self.joint_radius * ux + side * BALL_STATION * vx,
                           self.joint_radius * uy + side * BALL_STATION * vy, 0])

    def simulate(self):
        """Put the head where the drivers say and hang everything on it.

        The three relations declared above put the effector, the
        towers' heights and the six rods' four freedoms each from the
        drivers alone; this keeps only what they cannot reach -- the
        Bowden tube and the filament, which follow the head but are not
        driven coordinates of any declared joint.
        """
        plane = layout.joint_plane(self.z)

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
