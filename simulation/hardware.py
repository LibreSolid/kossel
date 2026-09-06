"""What the bought parts are.

Catalogue dimensions of everything the design does not draw, each with
where the number comes from.  Clearances are drawing decisions and say
so: two parts that touch exactly cannot be asked whether they interfere.
"""

from simulation.layout import EXTRUSION, M3_MAJOR

#: A screw or pin drawn a tenth under its hole, a bore a tenth over its
#: shaft, wherever nothing better is stated; and half that between two
#: faces that meet, so the pair can be asked whether they touch.
FIT = 0.1
STANDOFF = 0.05

# OpenBeam 1515.  The vertex's extrusion cutout carries 2.5 mm wide tabs
# 3.1 mm into each slot, so the opening is drawn for them; the cavity
# behind the lips takes an M3 nut, and stops where the corner blocks
# still join the core.  The vertical screws' cones clear the tabs at the
# screw stations, which is where the nuts sit.
SLOT_OPENING = 3.0
SLOT_LIP_DEPTH = 1.5
SLOT_CAVITY = 5.6                # an M3 nut's 5.5 across flats, a twentieth each side
SLOT_DEPTH = 4.4                 # what an M3 x 8 through a 3.6 bracket reaches, plus a twentieth

# MGN12 rail and MGN12H block (HIWIN catalogue)
RAIL_WIDTH = 12.0
RAIL_HEIGHT = 8.0
RAIL_HOLE_PITCH = 25.0
RAIL_HOLE_FIRST = 12.5           # from the rail end
BLOCK_WIDTH = 27.0
BLOCK_LENGTH = 44.5
BLOCK_HEIGHT = 13.0              # rail base to block top
BLOCK_UNDERSIDE = 3.0            # rail base to block underside
BLOCK_HOLE_PATTERN = 20.0

# where the carriage's horn axis lands off the tower face: the block's
# top plus the carriage drawing's horn axis
CARRIAGE_OFFSET = BLOCK_HEIGHT + 13.0 / 2      # 19.5, Marlin's DELTA_CARRIAGE_OFFSET

# GT2 pulley on the tower motors: the firmware's 80 steps/mm at 3200
# steps a turn is 40 mm a turn, twenty teeth.  Hub, flanges and bore as
# the common 20T/5mm part.
PULLEY_TEETH = 20
PULLEY_WIDTH = 7.5               # the toothed body, for a 6 mm belt
PULLEY_FLANGE_RADIUS = 8.0
PULLEY_FLANGE = 1.0
PULLEY_HUB_RADIUS = 8.0
PULLEY_HUB = 6.5
PULLEY_BORE = 5.0
BELT_WIDTH = 6.0

# bearings: 623ZZ on the idler bolt, 625ZZ in the extruder
BEARING_623 = (3.0, 10.0, 4.0)   # bore, outer diameter, width
BEARING_625 = (5.0, 16.0, 5.0)

# NEMA 17 shaft, from nema17.scad
MOTOR_SHAFT = 5.0

# metric fasteners.  Shanks at the design's own major (2.85) or the tap
# drill of what they self-tap into; heads are ISO 4762 socket caps.
M3_SHANK = M3_MAJOR
M3_HEAD_DIAMETER = 5.5
M3_HEAD = 3.0
M3_NUT_FLATS = 5.5
M3_NUT = 2.4
M5_SHANK = 4.9
M5_HEAD_DIAMETER = 8.5
M5_HEAD = 5.0
M5_NUT_FLATS = 8.0
M5_NUT = 4.0

# the ball joints: Traxxas 5347 rod ends on 6 mm hollow balls, each on a
# short M3 button-head screw through its horn into a nut trapped inside
# the horn -- the traps the carriage and the effector are drawn with.
# The kinematics reads only the ball centre.
#
# A hollow ball is a ball on a sleeve.  The sleeve stands the ball off the
# horn and off the screw head, and it has to: a rod swings up to 21
# degrees out of the plane of its screw at the instructions' targets and
# the housing around the ball swings with it, reaching 2.85 mm either way
# from the ball's centre.  So the sleeves are 3.0 and 3.1, the housing 7.4
# across and 3.4 wide, and its socket is flared at 66 degrees so the
# sleeve passes through it at that swing; the lip that keeps the ball is
# what is left inside 1.24 mm of the ring's middle plane.  Button heads because the
# three arms' fasteners meet at the effector's corners 14.6 mm past the
# horns, where a socket head would touch its neighbour.  All drawn from
# the joint's own mechanics rather than a datasheet, and stated so.
BALL_DIAMETER = 6.0
BALL_BORE = M3_MAJOR + 2 * FIT
BALL_SLEEVE_DIAMETER = 4.0
BALL_SLEEVE_IN = 3.0             # ball centre to the horn face
BALL_SLEEVE_OUT = 3.1            # ball centre to the screw head
ROD_END_HOUSING_DIAMETER = 7.4   # a wider ring stands its rim off the horn's cone at full swing
ROD_END_HOUSING_WIDTH = 3.4
ROD_END_SOCKET = BALL_DIAMETER + FIT
ROD_END_FLARE = 66.0             # half-angle of the socket's opening cone: the sleeve, swung 21 degrees, crosses the socket sphere at 62
ROD_END_STEM_DIAMETER = 3.9      # glued into the tube's 4 mm bore
ROD_END_REACH = 17.5             # ball centre to the tube's end face
ROD_END_TUBE_DEPTH = 8.0         # how far the stem runs into the tube
M3_BUTTON_HEAD_DIAMETER = 5.7    # ISO 7380
M3_BUTTON_HEAD = 1.65
TUBE_DIAMETER = 6.0
TUBE_BORE = 4.0

# the J-Head Mk V-B, groove-mount standard, and the brass below it as
# the drawing Metamaquina 2 reads the same part from
# The collar and the groove are drawn a twentieth under the standard's 16
# and 12, because the effector's pocket and the clamp's slot are cut at
# exactly those and two coincident cylinders cannot be asked whether
# they touch.
JHEAD_COLLAR_DIAMETER = 15.9
JHEAD_COLLAR = 4.76
JHEAD_GROOVE_DIAMETER = 11.7
JHEAD_GROOVE = 4.7               # the standard's 4.64, opened for the 4.6 plate to clear both ways
JHEAD_BODY_DIAMETER = 16.0
JHEAD_BODY = 30.0
JHEAD_FIN_ROOT = 10.4
JHEAD_FINS = 5
JHEAD_FIN_GROOVE = 2.0
JHEAD_FIN_PITCH = 3.175
JHEAD_BORE = 3.2
BLOCK_SIDE = 12.7                # heater block, 0.5"
BLOCK_TALL = 8.26                # 0.325"
NOZZLE_REACH = 3.05              # 0.12" of brass below the block
NOZZLE_DROP = JHEAD_COLLAR + JHEAD_GROOVE + JHEAD_BODY + BLOCK_TALL + NOZZLE_REACH
FILAMENT_DIAMETER = 1.75

# the Bowden push-fit, PC4-M5: a stub at the tap drill it self-taps into,
# a round body and a collet.  The tube seats at the stub's top.
PUSHFIT_STUB_DIAMETER = 3.8
PUSHFIT_STUB = 4.0
PUSHFIT_BODY_DIAMETER = 10.0
PUSHFIT_BODY = 6.0
PUSHFIT_COLLET_DIAMETER = 8.0
PUSHFIT_COLLET = 4.0
PUSHFIT_BORE = 4.2
BOWDEN_DIAMETER = 4.0
BOWDEN_BORE = 2.0

# the print surface
GLASS_DIAMETER = 170.0
GLASS = 3.0

# the PG35L gearmotor in the extruder cradle (drawn 0.2 under the 35 mm
# cradle so the two can be asked whether they touch), and the MK7 drive
# gear on its shaft
PG35L_DIAMETER = 34.8
PG35L_LENGTH = 40.0
PG35L_BOSS_DIAMETER = 22.3      # the body's recess is 22.5
PG35L_BOSS = 1.9                 # the body's recess is 2.35 deep, and the idler nut's trap opens into it
PG35L_SHAFT = 5.0
PG35L_SHAFT_LENGTH = 18.0
MK7_DIAMETER = 12.0
MK7_HOB_DIAMETER = 10.6
MK7_HOB_WIDTH = 2.5
MK7_HUB_DIAMETER = 13.6
MK7_HUB = 5.0
MK7_TOOTHED = 8.9

# the power supply brick
PSU_LENGTH = 108.0
