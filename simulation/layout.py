"""Where things are, read off the OpenSCAD design and Marlin.

Every number here is either written in a `.scad` file beside this
package (named with the file it comes from) or in Johann's Marlin
configuration for the Mini Kossel.  Nothing is derived from a
declared parameter: the root's knobs are combined with these in the
nodes, and the defaults the driver ranges are computed from are stated
once at the bottom.
"""

import math

# configuration.scad
EXTRUSION = 15.0          # OpenBeam 15 x 15
MOTOR_OFFSET = 44.0       # NEMA 17 face from the tower axis
MOTOR_LENGTH = 47.0
BRACKET_THICKNESS = 3.6   # under an M3 x 8 head
M3_MAJOR = 2.85           # what the design drills its M3 holes for

# Marlin, Configuration.h of the Mini Kossel.  Towers are named as the
# firmware names them and stand where it puts them.
TOWER_NAMES = ('X', 'Y', 'Z')
TOWER_ANGLES = (210.0, 330.0, 90.0)
PRINTABLE_RADIUS = 90.0   # DELTA_PRINTABLE_RADIUS

# vertex.scad: the horizontal beam line, 16 mm off the vertex's own Y axis
# and 30 degrees from it, and where along it the beam's end may fall --
# past the nut tunnel the vertex cuts at 11 (hex radius 4) and short of
# the screw sockets at 23.
VERTEX_BEAM_OFFSET = 16.0
VERTEX_BEAM_ANGLE = 30.0
BEAM_STANDOFF = 0.05                 # the beam drawn off the vertex face it lies on
BEAM_END_WINDOW = (7.5, 17.5)
BEAM_SCREW_STATIONS = (23.0, 67.0)   # along the beam line from the vertex Y axis
BEAM_SCREW_FACE = 8.5                # the beam face the screws enter, off the vertex Y axis
SCREW_HEAD_SEAT = 3.8                # plastic under a socket head, screw_socket()
VERTICAL_SCREW_SEAT = 7.5 + 0.1 + SCREW_HEAD_SEAT   # head seat off the tower axis, outer face
VERTEX_SCREW_PITCH = 30.0            # one vertical screw per 30 mm of vertex

# frame_motor.scad / frame_top.scad
MOTOR_VERTEX_HEIGHT = 3 * EXTRUSION
TOP_VERTEX_HEIGHT = EXTRUSION
IDLER_STATION = 26.0 + 3.0           # 26 + idler_offset, off the tower axis
IDLER_BOLT_FROM = 10.0               # the M3 runs from y = 65 down to 10
IDLER_BOLT_TO = 65.0
IDLER_SPACE = 12.5

# the three beam rows: bottom faces.  Two rows through the motor vertex,
# one through the top vertex.
BOTTOM_ROWS = (0.0, 2 * EXTRUSION)

# carriage.scad, in the carriage's own frame: X across, Y up the tower,
# Z off the block toward the printer's centre.
CARRIAGE_HORN_Y = 16.0
CARRIAGE_HORN_Z = 13.0 / 2
CARRIAGE_TOP = 24.0                  # the horns' upper edge, above the block's centre
CARRIAGE_SEPARATION = 40.0
CARRIAGE_SCREW_PATTERN = 20.0        # the block's 20 x 20 holes
CARRIAGE_BELT_X = 5.6
CARRIAGE_BELT_Z = 7.0
CARRIAGE_BELT_WIDTH_DRAWN = 5.0
CARRIAGE_SCREW_LENGTH = 60.0         # "Screws for ball joints", h=60

# effector.scad
EFFECTOR_OFFSET = 20.0               # DELTA_EFFECTOR_OFFSET
EFFECTOR_HEIGHT = 8.0
EFFECTOR_MOUNT_RADIUS = 12.5
EFFECTOR_HOTEND_RADIUS = 8.0
EFFECTOR_POCKET_DEPTH = EFFECTOR_HEIGHT - 4.0   # height - push_fit_height
EFFECTOR_SEPARATION = 40.0
EFFECTOR_ARM_ANGLES_DRAWN = (30.0, 150.0, 270.0)

# endstop.scad and microswitch.scad
ENDSTOP_THICKNESS = 9.0
ENDSTOP_WIDTH = 15.0
ENDSTOP_HEIGHT = 15.0
SWITCH_LEVER_DROP = 10.5             # lever tip below the endstop's centre
HOME_GAP = 0.5                       # block top under the lever at home

# glass_tab.scad
TAB_THICKNESS = BRACKET_THICKNESS
TAB_STICKY = 25.4
TAB_STICKY_OFFSET = 8.0              # screw centre to the glass edge
TAB_SCREW_OFFSET = TAB_STICKY / 2 - EXTRUSION / 2
TAB_PAD = 0.7

# hotend_fan.scad
SHROUD_PLATE = 4.6                   # groove_height
SHROUD_BARREL_HEIGHT = 30.0
SHROUD_FAN_OFFSET = 15.0

# extruder.scad, in the module's frame before its print rotation: the
# motor axis along Y at (16, *, 21), the body from y 0 to 20, the
# filament along Z at (22.5, 6.5), the idler bearing at (31, 4.25..9.5, 21).
EXTRUDER_MOTOR_AXIS = (16.0, 21.0)
EXTRUDER_BODY_DEPTH = 20.0
EXTRUDER_FILAMENT = (22.5, 6.5)
EXTRUDER_ENTRY_Z = 42.0
EXTRUDER_IDLER_X = 31.0
EXTRUDER_IDLER_Y = (4.25, 9.5)
EXTRUDER_GEARHEAD_RECESS = 3.35
EXTRUDER_MOTOR_SCREW_RADIUS = 14.0
EXTRUDER_MOTOR_SCREW_ANGLE = 45.0
EXTRUDER_NUT_Y = (14.0, 22.0)

# frame_extruder.scad
EXTRUDER_BRACKET_LENGTH = 29.0
EXTRUDER_CRADLE_HEIGHT = 26.0        # motor axis above the beam top
EXTRUDER_BRACKET_SCREWS = (-11.0, 0.0, 11.0)

# power_supply.scad
PSU_SPACE = 15.0
PSU_WIDTH = 50.5
PSU_HEIGHT = 30.5
PSU_BRACKET_DEPTH = 16.0
PSU_BEAM_SCREW_X = PSU_WIDTH / 2 + 10
PSU_CLAMP_SCREW_X = PSU_WIDTH / 2 + 5
PSU_CLAMP_SCREW_Z = 9.0


def tower_frame(angle):
    """The rotation about Z that turns a tower's own frame (+Y toward
    the centre) into the machine, for a tower at `angle` degrees."""
    return angle + 90.0


def radial(angle):
    """Unit vector from the centre toward a tower at `angle` degrees."""
    return (math.cos(math.radians(angle)), math.sin(math.radians(angle)))


def tangential(angle):
    """Unit vector along a tower's own +X, in the machine."""
    return (-math.sin(math.radians(angle)), math.cos(math.radians(angle)))


def beam_line_distance(axis_radius):
    """Perpendicular distance from the centre to a horizontal beam's
    axis, for towers whose extrusion axes stand at `axis_radius`."""
    return axis_radius / 2 + VERTEX_BEAM_OFFSET


def beam_end_inset(axis_radius, beam_length):
    """Where a beam's end falls along the vertex's beam line, measured
    from the vertex Y axis, for the frame to close."""
    return (math.sqrt(3) * axis_radius - beam_length) / 2


def beam_point(inset):
    """A point on the a=+1 beam line at `inset` along it, in the tower's
    own frame: `rotate(30) translate([-16, inset])` from vertex.scad."""
    angle = math.radians(VERTEX_BEAM_ANGLE)
    x, y = -(VERTEX_BEAM_OFFSET + BEAM_STANDOFF), inset
    return (x * math.cos(angle) - y * math.sin(angle),
            x * math.sin(angle) + y * math.cos(angle))


# the bed: glass on the tabs on the upper bottom beams
GLASS_TOP = (BOTTOM_ROWS[1] + EXTRUSION) + TAB_THICKNESS + TAB_PAD + 3.0 + 0.15  # plus three seating standoffs

# The defaults the root declares, restated here for what has to be a
# number before the root exists: driver ranges, and the pose a tower
# built on its own stands at.
DEFAULT_TOWER_RADIUS = 145.0
DEFAULT_VERTICAL = 600.0
DEFAULT_HORIZONTAL = 240.0
DEFAULT_ROD = 215.0
DEFAULT_RAIL = 400.0
DEFAULT_Z = 50.0

# the kinematic constants that follow from the parts: the carriage joint
# off the tower face (MGN12H block 13 + horn axis 6.5), and the nozzle
# tip below the effector's joint plane (the J-Head stack, in `hardware`)
CARRIAGE_OFFSET = 13.0 + CARRIAGE_HORN_Z
NOZZLE_DROP = 4.76 + 4.7 + 30.0 + 8.26 + 3.05 + 0.1   # plus the two seating standoffs


def delta_radius(tower_radius):
    return tower_radius - CARRIAGE_OFFSET - EFFECTOR_OFFSET


def joint_plane(z):
    """The effector's ball-joint plane for a nozzle `z` above the glass."""
    return GLASS_TOP + z + NOZZLE_DROP


DEFAULT_CARRIAGE_HEIGHT = (
    joint_plane(DEFAULT_Z)
    + math.sqrt(DEFAULT_ROD ** 2 - delta_radius(DEFAULT_TOWER_RADIUS) ** 2))
