"""The Mini Kossel, as an assembly.  Under construction."""

from solid_node.node import AssemblyNode

from simulation import scad
from simulation.part import PrintedPart


class MotorVertex(PrintedPart):
    """frame_motor.scad: the bottom vertex holding a NEMA 17."""

    def render(self):
        return scad.frame_motor.frame_motor()


class Kossel(AssemblyNode):

    vertex = MotorVertex()
