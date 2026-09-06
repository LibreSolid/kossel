"""The Bowden tube and the filament, as flexible leaves.

Both are shapes that follow the machine: the tube runs from the push-fit
on the extruder, which never moves, to the push-fit on the effector,
which does, so its curve is drawn afresh at every pose.  The filament
runs further at both ends -- in from outside the frame, through the
drive, along the same curve, and down the hot end to the melt zone.

molejo's parameters are plain references, so every moving coordinate is
a port, bound by the machine in the leaf's own frame: the origin is the
tube's start, and the ports carry the far end relative to it.

The tube is drawn as a solid 4 mm sweep: molejo sweeps closed profiles
and has no annulus, so the bore is not there and the filament runs
inside the solid.  Both are flexible leaves, never printed solids, and
the interference contracts leave them to each other; the containment
contract asks that the filament stays where the bore would be.  Its
drawn length varies with the pose, where a real tube's does not; the
difference a real tube takes up in its bow is not drawn.
"""

from molejo import Circle, Line, P, Shape, Spline
from solid_node.node import MolejoNode, TranslationalPort

from simulation import hardware, materials
from simulation.layout import EXTRUDER_ENTRY_Z
from simulation.scad import scad_sources

#: How far the strand runs in from where it enters the extruder body to
#: where the tube starts: the body's filament path (42 mm) less the
#: push-fit's stub, plus the floor the tube seats on inside it.
RUN_IN = EXTRUDER_ENTRY_Z - hardware.PUSHFIT_STUB + (hardware.PUSHFIT_STUB + 0.5)

#: Rings along each element of the path; a spline is one element per
#: point, so the whole free run gets this many.
PATH_SAMPLES = 96
PROFILE_SAMPLES = 12

#: The tube leaves the extruder's push-fit toward the centre and enters
#: the effector's from above.
LEAVING = [0.0, 1.0, 0.0]
ARRIVING = [0.0, 0.0, -1.0]


class BowdenTube(MolejoNode):

    color = materials.PTFE

    head_x = TranslationalPort(unit='mm')
    head_y = TranslationalPort(unit='mm')
    head_z = TranslationalPort(unit='mm')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = self.files | scad_sources()

    def render(self):
        return Shape(
            profile=Circle(radius=hardware.BOWDEN_DIAMETER / 2),
            path=[Spline(points=[[P.head_x, P.head_y, P.head_z]],
                         start_tangent=LEAVING, end_tangent=ARRIVING)],
            path_samples=PATH_SAMPLES,
            profile_samples=PROFILE_SAMPLES,
        )


class Filament(MolejoNode):
    """The strand: from where it enters the extruder body (the origin)
    straight along the body's filament path to the tube's start, along
    the tube's curve to the effector's push-fit, and straight down the
    hot end to the melt zone.  The ports are the far end and the melt
    zone's height, relative to the entry.
    """

    color = materials.FILAMENT

    head_x = TranslationalPort(unit='mm')
    head_y = TranslationalPort(unit='mm')
    head_z = TranslationalPort(unit='mm')
    melt_z = TranslationalPort(unit='mm')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = self.files | scad_sources()

    def render(self):
        return Shape(
            profile=Circle(radius=hardware.FILAMENT_DIAMETER / 2),
            path=[
                Line(to=[0.0, RUN_IN, 0.0]),
                Spline(points=[[P.head_x, P.head_y, P.head_z]],
                       start_tangent=LEAVING, end_tangent=ARRIVING),
                Line(to=[P.head_x, P.head_y, P.melt_z]),
            ],
            path_samples=PATH_SAMPLES,
            profile_samples=PROFILE_SAMPLES,
        )
