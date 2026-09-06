"""Contracts the effector keeps with what hangs from it."""

import numpy
import trimesh
from solid_node.test import TestCase

from simulation import hardware, layout
from simulation.effector import EffectorAssembly


class EffectorAssemblyTest(TestCase):

    node = EffectorAssembly

    def assertGap(self, node, other, low, high, points=None):
        if points is None:
            points = node.mesh.vertices
        distance = trimesh.proximity.closest_point(other.mesh, points)[1].min()
        self.assertGreaterEqual(distance, low,
                                f'{node.name} comes within {distance:.3f} of {other.name}')
        self.assertLessEqual(distance, high,
                             f'{node.name} stands {distance:.3f} off {other.name}')

    def test_the_collar_seats_in_the_pocket(self):
        holder, effector = self.node.holder, self.node.effector
        self.assertNotIntersecting(holder, effector)
        # the pocket is a 36-gon a fiftieth inside its circle
        self.assertGap(holder, effector, 0.015, 0.1)
        # up is blocked by the pocket floor at once; down by the clamp plate
        self.assertBlockedBeyond(holder, 0.1, effector, along=(0, 0, 1), directions='forward')
        self.assertFreeWithin(holder, 0.02, self.node.shroud, along=(0, 0, -1), directions='forward')
        self.assertBlockedBeyond(holder, 0.2, self.node.shroud, along=(0, 0, -1), directions='forward')

    def test_the_plate_is_in_the_groove(self):
        shroud, holder = self.node.shroud, self.node.holder
        self.assertNotIntersecting(shroud, holder)
        self.assertFreeWithin(shroud, 0.02, holder, along=(0, 0, 1))
        self.assertBlockedBeyond(shroud, 0.1, holder, along=(0, 0, 1))

    def test_z_is_the_nozzle(self):
        tip = self.node.nozzle.mesh.bounds[0][2]
        self.assertAlmostEqual(tip, -layout.NOZZLE_DROP, delta=0.01)
        self.assertAlmostEqual(tip, -(4.76 + 4.7 + 30.0 + 8.26 + 3.05 + 0.1), delta=0.01)

    def assertInHole(self, screw, part, clearance):
        """`part` has a hole the shank of `screw` runs through: vertices of
        `part` lie all round the shank, within `clearance` of it, and none
        of the part is inside the screw."""
        self.assertNotIntersecting(screw, part)
        mesh = screw.mesh
        centre = mesh.vertices.mean(axis=0)
        axis = numpy.linalg.svd(mesh.vertices - centre)[2][0]
        offsets = part.mesh.vertices - centre
        along = offsets @ axis
        radial = numpy.linalg.norm(offsets - numpy.outer(along, axis), axis=1)
        reach = numpy.abs((mesh.vertices - centre) @ axis).max()
        ring = part.mesh.vertices[(radial < hardware.M3_SHANK / 2 + clearance + 0.05)
                                  & (numpy.abs(along) < reach)]
        self.assertGreater(len(ring), 6, f'{part.name} has no hole round {screw.name}')
        distance = trimesh.proximity.closest_point(mesh, ring)[1]
        self.assertLess(distance.max(), clearance + 0.02,
                        f'{part.name} stands {distance.max():.3f} off {screw.name}')

    def test_the_clamp_screws_reach_the_shroud(self):
        self.assertEqual(len(list(self.node.clamp_screws)), 5)
        for screw in self.node.clamp_screws:
            self.assertInHole(screw, self.node.effector, 0.3)
            self.assertInHole(screw, self.node.shroud, 0.1)

    def test_the_pushfit_sits_in_the_thread(self):
        self.assertNotIntersecting(self.node.pushfit, self.node.effector)
        self.assertGap(self.node.pushfit, self.node.effector, 0.0, 0.3)

    def test_the_balls_are_captured_on_their_screws(self):
        for ball, screw, nut in zip(self.node.balls, self.node.joint_screws, self.node.joint_nuts):
            self.assertNotIntersecting(ball, screw)
            self.assertGap(ball, screw, 0.04, 0.15)
            self.assertNotIntersecting(ball, self.node.effector)
            self.assertGap(ball, self.node.effector, 0.03, 0.08)
            self.assertNotIntersecting(nut, self.node.effector)
            self.assertNotIntersecting(nut, screw)
            self.assertGap(nut, screw, 0.05, 0.15)
        # Pushed inward the sleeve meets the horn; outward, the screw head.
        # The perturbation goes in before the ball's first translation, so
        # its direction is read in the arm's frame, where the screw is X.
        for arm in range(3):
            for side in (-1, 1):
                index = 2 * arm + (side > 0)
                ball, screw = self.node.balls[index], self.node.joint_screws[index]
                self.assertBlockedBeyond(ball, 0.1, self.node.effector, along=(-side, 0, 0),
                                         directions='forward')
                self.assertBlockedBeyond(ball, 0.1, screw, along=(side, 0, 0),
                                         directions='forward')

    def test_solid_integrity(self):
        self.assertNoDisconnectedSolids(self.node)

    def test_assembly_integrity(self):
        self.assertNoSolidInterference(self.node)
