"""The base every leaf drawn from the OpenSCAD design shares."""

from solid2.core.object_base import OpenSCADObject
from solid_node.node import Solid2Node

from simulation import materials
from simulation.scad import scad_sources

# OpenSCAD's defaults draw a 6 mm bore as a 7-gon; the design sets `$fn`
# per file, so parts drawn here in Python state their own resolution.
FACET_ANGLE = 2
FACET_SIZE = 0.3


def curve(primitive, **parameters):
    """A curved primitive drawn here, at a resolution fit for a fit."""
    return OpenSCADObject(
        primitive, dict(parameters, **{'$fa': FACET_ANGLE, '$fs': FACET_SIZE}))


class ScadPart(Solid2Node):
    """A part whose geometry comes from the .scad sources.

    The framework invalidates a node from the Python files it imports, and
    no Python import names a .scad file, so each part adds the whole
    design to its own source set.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = self.files | scad_sources()


class PrintedPart(ScadPart):
    """One of Johann's printed parts: one module, one colour."""

    color = materials.PLA
