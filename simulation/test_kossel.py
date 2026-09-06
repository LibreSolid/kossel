"""Contracts the machine has to keep."""

import math

import numpy
import trimesh
from solid_node.simulation import ScenarioTest
from solid_node.test import TestCase

from simulation import layout
from simulation.kossel import Z_MAX, Kossel
from simulation.layout import (
    BOTTOM_ROWS,
    EXTRUSION,
    TOP_VERTEX_HEIGHT,
    TOWER_ANGLES,
    BEAM_STANDOFF,
    VERTEX_BEAM_ANGLE,
    VERTEX_BEAM_OFFSET,
)

#: The poses the kinematic contracts are asked at: the rest pose, the
#: bed, home, and the print radius under each tower.
POSES = [(0.0, 0.0, 50.0), (0.0, 0.0, 0.0), (0.0, 0.0, Z_MAX)] + [
    (90.0 * math.cos(math.radians(a)), 90.0 * math.sin(math.radians(a)), 20.0)
    for a in TOWER_ANGLES]


def rotate2(point, degrees):
    a = math.radians(degrees)
    x, y = point
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))


class KosselTest(TestCase):

    node = Kossel

    # -- the frame ---------------------------------------------------------

    def axis_radius(self):
        return self.node.tower_radius + EXTRUSION / 2

    def tower_position(self, angle):
        radius = self.axis_radius()
        return numpy.array([radius * math.cos(math.radians(angle)),
                            radius * math.sin(math.radians(angle)), 0.0])

    def beam_reference(self, angle, side, z):
        """Where a beam's end should be in the machine: the vertex beam
        line at the inset that closes a frame of this radius, worked out
        here from the knobs rather than read off the model."""
        radius = self.axis_radius()
        inset = (math.sqrt(3) * radius - self.node.horizontal_extrusion) / 2
        local = rotate2((-(VERTEX_BEAM_OFFSET + BEAM_STANDOFF) * side, inset),
                        VERTEX_BEAM_ANGLE * side)
        x, y = rotate2(local, angle + 90)
        return self.tower_position(angle) + numpy.array([x, y, z])

    def assertGap(self, node, other, low, high):
        """The closest `node` comes to `other`, from `node`'s vertices to
        `other`'s surface, lies between `low` and `high` millimetres."""
        distance = trimesh.proximity.closest_point(other.mesh, node.mesh.vertices)[1].min()
        self.assertGreaterEqual(distance, low,
                                f'{node.name} comes within {distance:.3f} of {other.name}')
        self.assertLessEqual(distance, high,
                             f'{node.name} stands {distance:.3f} off {other.name}')

    def end_faces(self, mesh, direction):
        """Centres of the two end faces of a prism along `direction`."""
        vertices = mesh.vertices
        along = vertices @ direction
        near = vertices[along < along.min() + 0.01].mean(axis=0)
        far = vertices[along > along.max() - 0.01].mean(axis=0)
        return near, far

    def test_the_horizontal_beams_close_the_frame(self):
        rows = BOTTOM_ROWS + (self.node.vertical_extrusion - TOP_VERTEX_HEIGHT,)
        radius = self.axis_radius()
        for index, beam in enumerate(self.node.beams):
            angle = TOWER_ANGLES[index // 3]
            z = rows[index % 3] + EXTRUSION / 2
            start = self.beam_reference(angle, 1, z)
            end = self.beam_reference(angle - 120, -1, z)
            direction = (end - start) / numpy.linalg.norm(end - start)
            near, far = self.end_faces(beam.mesh, direction)
            self.assertLess(numpy.linalg.norm(near - start), 0.05,
                            f'{beam.name} starts {near} rather than {start}')
            self.assertLess(numpy.linalg.norm(far - end), 0.05,
                            f'{beam.name} ends {far} rather than {end}')
            midpoint = (near + far) / 2
            self.assertAlmostEqual(math.hypot(midpoint[0], midpoint[1]),
                                   radius / 2 + VERTEX_BEAM_OFFSET + BEAM_STANDOFF, delta=0.05)

    def test_a_tower_radius_the_beams_cannot_reach_is_refused(self):
        with self.assertRaises(ValueError):
            Kossel(tower_radius=160.0)
        with self.assertRaises(ValueError):
            Kossel(tower_radius=130.0)

    def test_frame_screws_reach_their_nuts_and_miss_the_metal(self):
        for tower in self.node.towers:
            screws = list(tower.vertical_screws) + list(tower.beam_screws)
            nuts = list(tower.vertical_nuts) + list(tower.beam_nuts)
            for screw, nut in zip(screws, nuts):
                self.assertNotIntersecting(screw, nut)
                self.assertGap(nut, screw, 0.05, 0.15)
                self.assertNotIntersecting(screw, tower.extrusion)
            for nut in tower.vertical_nuts:
                self.assertNotIntersecting(nut, tower.extrusion)
                self.assertGap(nut, tower.extrusion, 0.0, 0.1)
        for beam in self.node.beams:
            for tower in self.node.towers:
                for screw, nut in zip(tower.beam_screws, tower.beam_nuts):
                    self.assertNotIntersecting(screw, beam)
                    self.assertNotIntersecting(nut, beam)

    # -- delta-kinematics -----------------------------------------------------

    def expected_heights(self, x, y, z):
        """The three carriage joint heights, from the knobs and the
        parts' own numbers, by the test's own arithmetic."""
        plane = 52.45 + z + (4.76 + 4.7 + 30.0 + 8.26 + 3.05 + 0.1)
        radius = self.node.tower_radius - 19.5 - 20.0
        rod = self.node.diagonal_rod
        heights = []
        for angle in TOWER_ANGLES:
            dx = x - radius * math.cos(math.radians(angle))
            dy = y - radius * math.sin(math.radians(angle))
            heights.append(plane + math.sqrt(rod ** 2 - dx ** 2 - dy ** 2))
        return heights

    def joint_height(self, tower):
        """Where a tower's ball-joint axis stands: the balls' centres."""
        return numpy.mean([ball.mesh.centroid[2] for ball in tower.carriage.balls])

    def test_the_nozzle_position_drives_the_carriages(self):
        for x, y, z in POSES:
            self.node.set_state(x=x, y=y, z=z)
            expected = self.expected_heights(x, y, z)
            for tower, height in zip(self.node.towers, expected):
                self.assertAlmostEqual(self.joint_height(tower), height, delta=0.01,
                                       msg=f'{tower.name} at {(x, y, z)}')
            tip = self.node.effector.nozzle.mesh.bounds[0][2]
            self.assertAlmostEqual(tip, 52.45 + z, delta=0.01)
        x, y, z = POSES[3]
        heights = self.expected_heights(x, y, z)
        self.assertGreater(max(heights) - min(heights), 10.0)

    def test_rods_of_the_declared_length_reach_both_joints(self):
        for x, y, z in POSES:
            self.node.set_state(x=x, y=y, z=z)
            for index, tower in enumerate(self.node.towers):
                for side in (0, 1):
                    rod = self.node.rods[2 * index + side]
                    upper, lower = rod.ends
                    carriage_ball = tower.carriage.balls[side]
                    effector_ball = self.node.effector.balls[2 * index + side]
                    self.assertGap(upper, carriage_ball, 0.03, 0.08)
                    self.assertGap(lower, effector_ball, 0.03, 0.08)
                    self.assertNotIntersecting(upper, tower.carriage.joint_screws[side])
                    self.assertNotIntersecting(lower, self.node.effector.joint_screws[2 * index + side])
                    self.assertNotIntersecting(upper, tower.carriage.carriage)
                    self.assertNotIntersecting(lower, self.node.effector.effector)
                    span = numpy.linalg.norm(
                        carriage_ball.mesh.bounds.mean(axis=0)
                        - effector_ball.mesh.bounds.mean(axis=0))
                    self.assertAlmostEqual(span, self.node.diagonal_rod, delta=0.05)

    def test_home_stops_short_of_the_switch(self):
        self.node.set_state(x=0.0, y=0.0, z=Z_MAX)
        for tower in self.node.towers:
            carriage, switch = tower.carriage.carriage, tower.endstop.switch
            self.assertNotIntersecting(carriage, switch)
            self.assertNotIntersecting(tower.carriage.block, switch)
            # Up the tower is the carriage's own +Y: it is drawn flat with
            # its horns along +Y, and its quarter turn carries that up.
            self.assertFreeWithin(carriage, 0.3, switch, along=(0, 1, 0), directions='forward')
            self.assertBlockedBeyond(carriage, 1.2, switch, along=(0, 1, 0), directions='forward')

    # -- bed-mount --------------------------------------------------------------

    def test_the_glass_rests_on_three_pads(self):
        bed = self.node.bed
        top = bed.glass.mesh.bounds[1][2]
        self.assertAlmostEqual(top, 52.45, delta=0.01)
        centre = bed.glass.mesh.bounds.mean(axis=0)
        self.assertLess(math.hypot(centre[0], centre[1]), 0.05)
        for pad in bed.pads:
            self.assertNotIntersecting(bed.glass, pad)
            self.assertBlockedBeyond(bed.glass, 0.1, pad, along=(0, 0, -1), directions='forward')
        for tab, screw, nut in zip(bed.tabs, bed.screws, bed.nuts):
            self.assertNotIntersecting(tab, screw)
            self.assertNotIntersecting(screw, nut)
            self.assertGap(nut, screw, 0.05, 0.15)
            for beam in self.node.beams:
                self.assertNotIntersecting(screw, beam)
                self.assertNotIntersecting(nut, beam)

    # -- extruder-mount -----------------------------------------------------------

    def test_the_motor_lies_in_its_cradle(self):
        extruder = self.node.extruder
        self.assertNotIntersecting(extruder.motor, extruder.bracket)
        # Into the cradle is the motor's own +X: its quarter turn about Y
        # carries that to the extruder's -Z.
        self.assertFreeWithin(extruder.motor, 0.02, extruder.bracket, along=(1, 0, 0),
                              directions='forward')
        self.assertBlockedBeyond(extruder.motor, 0.3, extruder.bracket, along=(1, 0, 0),
                                 directions='forward')
        self.assertNotIntersecting(extruder.body, extruder.motor)
        self.assertGap(extruder.body, extruder.motor, 0.03, 0.2)
        self.assertNotIntersecting(extruder.gear, extruder.body)
        for screw in extruder.motor_screws:
            self.assertNotIntersecting(screw, extruder.body)
            self.assertNotIntersecting(screw, extruder.motor)
            self.assertGap(screw, extruder.motor, 0.05, 0.15)

    def test_the_drive_pinches_the_filament(self):
        extruder = self.node.extruder
        gear_axis = extruder.gear.mesh.bounds.mean(axis=0)
        entry = numpy.array(self.node.filament_entry)
        start = numpy.array(self.node.tube_start)
        # the strand runs along Y from the entry to the tube's start
        self.assertAlmostEqual(entry[0], start[0], delta=0.01)
        self.assertAlmostEqual(entry[2], start[2], delta=0.01)
        self.assertAlmostEqual(abs(gear_axis[2] - entry[2]), 6.5, delta=0.05)
        self.assertAlmostEqual(abs(gear_axis[2] - entry[2]),
                               10.6 / 2 + 1.75 / 2 + 0.3, delta=0.35)

    # -- bowden-path --------------------------------------------------------------

    def test_the_tube_reaches_the_head_everywhere(self):
        start = numpy.array(self.node.tube_start)
        for x, y, z in POSES:
            self.node.set_state(x=x, y=y, z=z)
            plane = 52.45 + z + (4.76 + 4.7 + 30.0 + 8.26 + 3.05 + 0.1)
            seat = numpy.array([x, y, plane + 4.5 + 0.05])
            tube = self.node.bowden.mesh
            at_start, at_seat = trimesh.proximity.closest_point(tube, [start, seat])[1]
            self.assertLess(at_start, 0.1, f'{(x, y, z)}: the tube starts {at_start} off its seat')
            self.assertLess(at_seat, 0.1, f'{(x, y, z)}: the tube ends {at_seat} off the head')
            # and it leaves toward the centre and arrives from above
            self.assertGreater(tube.vertices[:, 1].min(), start[1] - 2.1)
            self.assertGreater(tube.vertices[:, 2].min(), seat[2] - 2.1)
            for part in list(self.node.beams) + [t.top_vertex for t in self.node.towers]:
                self.assertNotIntersecting(self.node.bowden, part)

    def test_the_filament_stays_inside_the_tube(self):
        for x, y, z in (POSES[0], POSES[5]):
            self.node.set_state(x=x, y=y, z=z)
            tube = self.node.bowden.mesh
            strand = self.node.filament.mesh.vertices
            low, high = tube.bounds[0][2] + 3.0, tube.bounds[1][2] - 3.0
            inside = strand[(strand[:, 2] > low) & (strand[:, 2] < high)
                            & (strand[:, 1] > self.node.tube_start[1] + 3.0)]
            self.assertGreater(len(inside), 50)
            self.assertTrue(tube.contains(inside).all(), f'{(x, y, z)}: filament leaves the tube')

    # -- power-supply-mount -------------------------------------------------------

    def test_the_brick_is_held(self):
        psu = self.node.power_supply
        for bracket in psu.brackets:
            self.assertNotIntersecting(psu.brick, bracket)
        for along in ((0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0)):
            blocked = any(self.node.power_supply.brackets)
            self.assertFreeWithin(psu.brick, 0.05, psu.brackets[0], along=along, directions='forward')
        self.assertBlockedBeyond(psu.brick, 0.3, psu.brackets[0], along=(1, 0, 0))
        self.assertBlockedBeyond(psu.brick, 0.3, psu.brackets[0], along=(0, -1, 0), directions='forward')
        self.assertBlockedBeyond(psu.brick, 0.3, psu.brackets[1], along=(0, 1, 0), directions='forward')

    # -- the whole machine ---------------------------------------------------

    def test_solid_integrity(self):
        self.assertNoDisconnectedSolids(self.node)

    def test_assembly_integrity(self):
        self.assertNoSolidInterference(self.node)


class KosselScenarioTest(ScenarioTest):
    """The machine driven through every instruction, with the rigid parts
    asked to stay out of each other along the way."""

    node = Kossel
    dt = 0.25
    meshes = True

    def test_the_instructions_move_the_head_without_collision(self):
        sim = self.simulation()
        at = 0.0
        for name, hold in (('Home', 3.5), ('Bed', 2.5), ('TowerX', 2.5),
                           ('TowerY', 2.5), ('TowerZ', 2.5), ('Center', 2.5)):
            sim.at(at).trigger(name)
            at += hold
        sim.every(0.75, self.assertNoSolidInterference, self.node)
        sim.run(at)
        # and the head really went where it was sent: Center is the rest pose
        self.assertAlmostEqual(sim.state['x'], 0.0, delta=0.01)
        self.assertAlmostEqual(sim.state['z'], 50.0, delta=0.01)
