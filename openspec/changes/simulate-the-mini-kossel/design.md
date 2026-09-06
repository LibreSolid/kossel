## Context

The Mini Kossel is a delta printer: three vertical towers, a carriage on
each, six parallel rods from the carriages down to a triangular effector
carrying the hot end. Moving the nozzle to a point means raising and
lowering the three carriages together; no axis of the machine is an axis
of the print. Johann's repository draws the printed parts and nothing
else, and this change reads those drawings into a machine.

The model is a solid-node project on the declarative node API. Every
printed part is a `Solid2Node` whose `render()` calls the part's own
OpenSCAD module through solid2's `import_scad` (absolute `use`, so the
design's relative `include`, `use` and `import` keep resolving from the
source directory); each such node adds the whole `.scad` set to its
source set so an edit there rebuilds it. Sourced parts are drawn in
Python from catalogue dimensions. Flexible parts are molejo shapes.

## Coordinates

The origin is the printer's centre on the floor the bottom vertices stand
on; Z is up. Towers are named as Marlin names them and stand where Marlin
puts them: X at 210 degrees, Y at 330, Z at 90. Each tower's own frame is
the frame `vertex.scad` is drawn in — the extrusion's axis on the origin,
+Y toward the printer's centre, +X tangential — and the machine turns it
into place by `tower_angle + 90` degrees about Z.

The drivers are the printer's coordinates: `x` and `y` in millimetres
from the centre of the glass, `z` the nozzle tip's height above it. The
glass top is derived, not declared: it is where the tabs on the upper
bottom beams put it.

## Goals / Non-Goals

**Goals:**
- The `.scad` files are the printed parts. The layer is as thin as it can
  be: one node per module, dimensions read from the sources, nothing
  redrawn that the design already draws.
- The machine moves the way the printer does: a point on the bed becomes
  three carriage heights, six rod angles, three belts redrawn and three
  pulleys turned, and every rigid part stays out of every other at every
  pose the instructions reach.
- Everything a builder handles is a node, coloured by its material, and
  the flexible parts are flexible: belts as toothed wraps, tube and
  filament as sweeps whose shape follows the effector.

**Non-Goals:**
- Editing the OpenSCAD design. Disagreements are recorded, not fixed.
- Thread geometry. Screws are drawn at minor diameter with clearance,
  push-fits at the tap drill they self-tap into; threads are declared
  press supports where a support proof needs them.
- Electronics, wiring, the spool and where the maker hangs it: the
  filament enters from a short way above the extruder.
- Constant-length Bowden: the tube is a spline pinned at both ends with a
  bulge that keeps it clear of the frame; its drawn length varies with
  the pose, and the design says so.
- The parts listed out of scope in the proposal.

## Decisions

**The tower radius is Marlin's, and it is the one frame knob.** The
vertex is cut for a horizontal beam whose axis runs 30 degrees off the
vertex's own Y at a 16 mm offset, so the beams of three vertices close
an equilateral triangle for any tower radius, and the radius is fixed by
the beam length alone once the beam's end position in the vertex is
known — which the drawing does not state. Marlin's
`DELTA_SMOOTH_ROD_OFFSET` of 145 mm is taken as the distance from the
centre to the tower's inner face (the face the rail mounts on), because
Marlin's `DELTA_CARRIAGE_OFFSET` of 19.5 mm then falls out of the parts
exactly: MGN12H block height 13 plus the carriage's horn axis at 6.5.
With 240 mm beams the beam end lands 12.1 mm from the vertex's Y axis
along the beam, between the nut tunnel the vertex cuts for the slot nut
and the vertical extrusion; a `check()` on the frame refuses a radius
that puts it elsewhere. Alternatives measured: deriving the radius from
the glass tabs gives 154 (the glass edge 8 mm inside the beam axis meets
an 85 mm glass), from the FSR glass frame 152; both are within the slop
of a printed frame and neither is what the firmware is calibrated to.

**Effector offset and carriage offset are the drawings', not knobs.** 20
mm is written in `effector.scad` "same as DELTA_EFFECTOR_OFFSET in
Marlin"; 19.5 is derived above. Changing either means changing a printed
part, which this layer does not do. The delta radius is therefore
`145 - 19.5 - 20 = 105.5` and the rod length `diagonal_rod` (215, Marlin,
ball centre to ball centre) is a knob because the rods are cut to it.

**Inverse kinematics live in one module over `solid_node.math`.** For
tower `i` at angle `a_i` and joint radius difference `R`, the carriage
joint height is `z_e + sqrt(L^2 - (x - R cos a_i)^2 - (y - R sin a_i)^2)`
where `z_e` is the effector joint plane. Each rod is drawn from its
carriage ball straight down and posed by two rotations with constant
axes — `asin(d / L)` about Y and `atan2(dy, dx)` about Z — because the
viewer's expressions carry driver symbols through these functions and
not through a rotation axis. The two rods of a tower share the pose and
differ by a constant tangential offset, which is the horn half
separation plus the ball radius, the same at both ends, so the pair
stays parallel by construction.

**The effector is mounted upside down relative to its drawing, and that
is the design.** The module has a 16 mm pocket 4 deep in its upper half
and an M5 internal thread in its lower half; a J-Head's collar goes in
the pocket and a Bowden push-fit in the thread, so the pocket faces down
and the thread up. One rotation of 180 degrees about X does both and
carries the arms from 30/150/270 degrees to 330/210/90 — Marlin's
towers. Nothing else about the effector had to be chosen.

**The J-Head is the groove-mount standard.** Collar 16 x 4.76, groove 12
x 4.64, body 16 x 30 (the shroud's `barrel_height`), brass block and
nozzle 11.3 below it (the dimensions of the drawing Metamaquina 2 reads
the same part from). The shroud's plate is 4.6 for the 4.64 groove and
the pocket is 4 for the 4.76 collar, so the plate stands 0.76 off the
effector's face with the collar seated; the model draws that gap rather
than a plate flush against a collar that would not fit. The nozzle tip is
then 50.7 mm below the joint plane, and that number is what makes `z` a
height above the glass.

**Belts are molejo wraps in the tower's belt plane.** The pulley is a 20
tooth GT2 — the firmware's 80 steps/mm at 3200 steps a turn is 40 mm a
turn — on the motor shaft, slid along it to the idler's radial station
of 29 mm (`frame_top`'s `26 + idler_offset`), so the loop is a vertical
plane 29 mm in from the tower axis. The idler is two 623 bearings on the
vertex's M3 bolt, 8 mm wide, and the 6 mm belt is centred on them
(26 to 32 mm radially), which is 1 mm inside where the carriage drawing
puts its 5 mm belt; the carriage's clamps still cover it. The wrap runs
`[pulley, idler]` clockwise in its own plane, the carriage anchors the
belt's arc-length origin on the rising span, and the pulley's angle is
read from the same carriage height, exactly as Metamaquina 2 does it;
the GT2 arithmetic (pitch line, tooth form, groove that lets a tooth in
and out, span origin and scale) is carried over from there with its
authorship noted. The pulley is cut a tenth inside the belt all round.

**The Bowden tube is a spline through three points.** Start at the
extruder's push-fit on the top frame, tangent down; end at the
effector's push-fit, tangent down; a middle point directly above the
effector at the height of the top frame plus a fixed clearance, so the
tube comes across level and turns down onto the head wherever the head
is, and never has to pass through the top triangle's beams. Its three
moving coordinates are three ports; the middle point is made of the
end's X and Y with a constant Z, so no port is spent on it. The filament
is a second sweep on the same points, continued down through the hot end
to the melt zone and up from the extruder's entry to a stub above it.

**Rails are 400 mm MGN12H, mounted with their top under the endstop.** The
endstop (15 tall, 9 deep — the drawing's "1 mm thicker than the rail")
sits on the tower face directly under the top vertex with its switch
hanging below it on the centre side; the block coming up meets the
switch body, so home is the block top one millimetre under the switch.
That fixes the top of the travel; the bottom is the bed, which the rail
reaches with room.

**Extrusion slots are drawn for the vertex's tabs.** The vertex's
extrusion cutout carries 6 x 2.5 tabs into each slot, so the OpenBeam
profile is drawn with a 6.2 mm opening 1.6 deep and a 6.6 mm cavity
behind it for the M3 slot nuts; frame screws are M3 x 8 as the design
recommends, drawn at minor diameter.

**Support is proven on the frame only.** Vertices and vertical
extrusions stand on the floor; the upper beams, the rails, the tabs and
the glass are held by screws declared as press supports. The moving
assembly hangs on belts, which are not printed solids, and on ball
sockets; the framework's frictionless push-only contact proof is not the
tool for a kinematic chain and is not asked.

**Rest pose.** The drivers default to the centre of the glass at 50 mm;
`Home` is the top, `Bed` is `z = 0`, `TowerX/Y/Z` move to the print
radius (90 mm, Marlin's `DELTA_PRINTABLE_RADIUS`) under each tower.
Driver ranges are computed from the default parameter values, because a
range must be a constant.

## Risks / Trade-offs

- [The beam-end position is inferred, not drawn] → recorded as a
  `check()` window (between the nut tunnel and the vertical extrusion)
  and a contract on the frame closing; a maker with a measured frame sets
  `tower_radius`.
- [Rod ends and balls are drawn from a 5347's rough dimensions] → the
  joint's kinematic point is the ball centre, the only number the
  kinematics reads; the housing is cosmetic and clears by 0.5 mm.
- [The belt's 1 mm radial disagreement with the carriage drawing] →
  stated; the belt is placed by the idler and pulley it runs on, which is
  what places a belt.
- [Tube length varies with pose] → stated; a length-true tube would need
  a vocabulary molejo does not have.
- [Perturbation contracts against a flexible part] → if the framework
  cannot perturb a rigid pulley against a flexible belt, the meshing is
  proven by a mesh boolean in the test, as Metamaquina 2 does, and the
  gap is reported.
