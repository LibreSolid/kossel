"""Delta kinematics, over `solid_node.math` so one formula serves the
viewer's symbols and the tests' numbers.  Trigonometry is in degrees.

A point of the nozzle becomes three carriage heights: for the tower at
`angle`, the carriage's ball-joint axis stands `sqrt(L^2 - d^2)` above
the effector's joint plane, where `d` is the horizontal distance from
the effector's joint to the carriage's and `L` is the rod.  Each rod is
then posed by two rotations with constant axes, because a rotation axis
cannot carry a driver symbol: tilted by `asin(d / L)` about Y and swung
to its azimuth about Z.
"""

from solid_node.math import asin, atan2, cos, sin, sqrt


def horizontal_offset(x, y, radius, angle):
    """The horizontal vector from the carriage joint of the tower at
    `angle` to the effector joint, for a nozzle at (`x`, `y`)."""
    return x - radius * cos(angle), y - radius * sin(angle)


def carriage_height(x, y, plane, rod, radius, angle):
    """Height of the carriage joint axis for the tower at `angle`."""
    dx, dy = horizontal_offset(x, y, radius, angle)
    return plane + sqrt(rod * rod - dx * dx - dy * dy)


def rod_tilt(x, y, rod, radius, angle):
    """Degrees the rod leans from vertical, for the tower at `angle`."""
    dx, dy = horizontal_offset(x, y, radius, angle)
    return asin(sqrt(dx * dx + dy * dy) / rod)


def rod_azimuth(x, y, radius, angle):
    """Degrees about Z the leaning rod points, from +X."""
    dx, dy = horizontal_offset(x, y, radius, angle)
    return atan2(dy, dx)
