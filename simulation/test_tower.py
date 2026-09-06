"""Contracts one tower keeps on its own, at the machine's default pose."""

import numpy
import trimesh
from solid_node.test import TestCase

from simulation import hardware, layout
from simulation.layout import IDLER_STATION
from simulation.tower import Tower


class TowerTest(TestCase):

    node = Tower

    def assertGap(self, node, other, low, high, points=None):
        """The closest `node` comes to `other`, from `node`'s vertices (or
        the given `points` of it) to `other`'s surface, lies between `low`
        and `high` millimetres."""
        if points is None:
            points = node.mesh.vertices
        distance = trimesh.proximity.closest_point(other.mesh, points)[1].min()
        self.assertGreaterEqual(distance, low,
                                f'{node.name} comes within {distance:.3f} of {other.name}')
        self.assertLessEqual(distance, high,
                             f'{node.name} stands {distance:.3f} off {other.name}')

    # -- rail-carriage-fit --------------------------------------------------

    def test_the_carriage_screws_meet_the_block_pattern(self):
        carriage = self.node.carriage
        for screw in carriage.plate_screws:
            self.assertNotIntersecting(screw, carriage.block)
            self.assertGap(screw, carriage.block, 0.05, hardware.FIT + 0.05)
            self.assertNotIntersecting(screw, carriage.carriage)

    def test_the_block_rides_the_rail_without_touching_it(self):
        block, rail = self.node.carriage.block, self.node.rail
        self.assertNotIntersecting(block, rail)
        self.assertFreeWithin(block, 0.05, rail, along=(0, -1, 0), directions='forward')
        self.assertBlockedBeyond(block, 0.15, rail, along=(0, -1, 0), directions='forward')
        self.assertFreeWithin(block, 0.05, rail, along=(1, 0, 0))
        self.assertBlockedBeyond(block, 0.15, rail, along=(1, 0, 0))

    def test_the_carriage_horn_axis_stands_where_marlin_says(self):
        """The ball-joint screw is 19.5 mm off the tower face: the block's
        13 plus the drawing's 6.5, which is DELTA_CARRIAGE_OFFSET."""
        centres = numpy.array([ball.mesh.centroid for ball in self.node.carriage.balls])
        axis_y, axis_z = centres[:, 1].mean(), centres[:, 2].mean()
        self.assertAlmostEqual(axis_y, layout.EXTRUSION / 2 + 13.0 + 6.5, delta=0.02)
        self.assertAlmostEqual(axis_z, layout.DEFAULT_CARRIAGE_HEIGHT, delta=0.02)

    def test_the_endstop_hangs_its_switch_over_the_rail(self):
        endstop = self.node.endstop
        self.assertNotIntersecting(endstop.endstop, self.node.extrusion)
        self.assertGap(endstop.endstop, self.node.extrusion, 0.0, 0.05)
        self.assertNotIntersecting(endstop.switch, endstop.endstop)
        top = self.node.rail.mesh.bounds[1][2]
        self.assertLess(top, endstop.endstop.mesh.bounds[0][2])
        switch_low = endstop.switch.mesh.bounds[0][2]
        endstop_centre = (self.node.vertical_extrusion - layout.TOP_VERTEX_HEIGHT
                          - layout.ENDSTOP_HEIGHT / 2)
        self.assertAlmostEqual(switch_low, endstop_centre - layout.SWITCH_LEVER_DROP, delta=0.05)

    # -- belt-drive ---------------------------------------------------------

    def test_the_belt_rides_its_pulley_and_idlers(self):
        belt = self.node.belt
        vertices = belt.mesh.vertices
        low = vertices[vertices[:, 2] < layout.MOTOR_VERTEX_HEIGHT]
        high = vertices[vertices[:, 2] > self.node.vertical_extrusion - layout.TOP_VERTEX_HEIGHT]
        self.assertIntersectVolumeBelow(belt, self.node.pulley, 0.05)
        self.assertGap(belt, self.node.pulley, 0.05, 0.15, points=low)
        for bearing in self.node.idlers:
            self.assertIntersectVolumeBelow(belt, bearing, 0.05)
            self.assertGap(belt, bearing, 0.0, 0.05, points=high)
        band = belt.mesh.vertices[:, 1]
        self.assertAlmostEqual(band.min(), IDLER_STATION - hardware.BELT_WIDTH / 2, delta=0.05)
        self.assertAlmostEqual(band.max(), IDLER_STATION + hardware.BELT_WIDTH / 2, delta=0.05)

    def test_the_pulley_meshes_the_belt_without_biting(self):
        # The pulley is cut a tenth inside the belt, which on a 56 degree
        # flank is a twentieth of a millimetre of play: about a fifth of a
        # degree at this pitch radius.
        # The perturbation is inserted before the pulley's placement
        # translation and after its turn onto the shaft, so its axis is
        # the shaft's direction in the tower's frame: the radial Y.
        self.assertFreeWithin(self.node.pulley, 0.2, self.node.belt, axis=(0, 1, 0))
        self.assertBlockedBeyond(self.node.pulley, 2.0, self.node.belt, axis=(0, 1, 0))

    def test_the_pulley_and_idlers_sit_on_their_shafts(self):
        self.assertNotIntersecting(self.node.pulley, self.node.motor)
        self.assertGap(self.node.pulley, self.node.motor, 0.05, 0.15)
        for bearing in self.node.idlers:
            self.assertNotIntersecting(bearing, self.node.idler_bolt)
            self.assertGap(bearing, self.node.idler_bolt, 0.05, 0.15)

    # -- the tower as a whole -------------------------------------------------

    def test_solid_integrity(self):
        self.assertNoDisconnectedSolids(self.node)

    def test_assembly_integrity(self):
        self.assertNoSolidInterference(self.node)
