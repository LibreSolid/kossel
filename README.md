Release status
==============

Most of these parts are now stable and won't change much more.

How to print Mini Kossel
========================

* 3x plate_3x.stl (about 3x80g = 240g of plastic)
* 1x plate_1x.stl (about 50g of plastic)

Links
=====

* Bill of Materials: http://reprap.org/wiki/Kossel
* Mailing list: http://groups.google.com/group/deltabot
* Project history: http://deltabot.tumblr.com

Pay it forward
==============

Johann is offering free printed parts for Mini Kossel:

* I'm going to make some Mini Kossel printed parts kits.
* I'm going to give them away for free (as in beer).
* Some kits may include some non-printed parts.
* Free international shipping is included.
* No delivery schedule, maybe only one kit per month.

But there's no such thing as a free lunch. If you want to receive a
free kit, you must swear by your geek honor:

* To complete your Mini Kossel and tune it well.
* To print two (2) Mini Kossel kits and also give them away for free.
* To make your recipients agree to the same rule.

After giving away the 2 free kits, you may sell printed parts for any
price you want.

If you're interested, please email johann@rocholl.net and let me know
your favorite PLA color and mailing address. If you want to get your
printed parts first, explain why you're more qualified than others to
start giving away high quality printed parts soon.

Simulation
==========

`simulation/` reads the OpenSCAD design above into the whole machine, as a
[solid-node](https://pypi.org/project/solid-node/) project: every printed
part is its `.scad` module called through solid2's `import_scad`, and
only what the design does not draw is modelled there -- the sourced parts
(OpenBeam, MGN12 rails and blocks, NEMA 17s, GT2 pulleys, bearings,
screws, slot nuts, hollow balls and rod ends, carbon tubes, the J-Head,
the glass, push-fits, the PG35L gearmotor, the power supply) and the
flexible parts (three GT2 belts, the Bowden tube, the filament).  The
`.scad` files are not edited.  The design record is `openspec/`.

    solid build                       # publish the model into _build/
    solid test --faceted simulation/kossel.py    # the machine's contracts, fast
    solid test simulation/kossel.py   # the same, decided exactly
    solid build --set tower_radius=150.0

The drivers are the printer's coordinates: `x` and `y` over the glass,
`z` the nozzle above it.  The three carriage heights follow from the
delta kinematics, the six rods swing to join the horns, the belts are
redrawn from where their carriages hold them and the pulleys turn.  The
instructions `Home`, `Center`, `Bed`, `TowerX`, `TowerY` and `TowerZ`
move the head.  Towers are named and placed as Marlin names and places
them: X at 210 degrees, Y at 330, Z at 90.

Knobs (`--set`): `tower_radius` (145, Marlin's DELTA_SMOOTH_ROD_OFFSET,
centre to the tower face), `vertical_extrusion` (600), `horizontal_extrusion`
(240), `diagonal_rod` (215, ball centre to ball centre), `rail_length`
(400).  The frame refuses a tower radius its 240 mm beams cannot close.

What the model found in the design, recorded in `openspec/`:

* The effector is mounted upside down relative to its drawing: the
  16 mm pocket takes the J-Head's collar from below and the M5 thread
  takes the Bowden push-fit from above, and the half turn that does it
  carries the arms to Marlin's tower angles.
* A groove-mount collar is 4.76 tall and the pocket is 4 deep, so the
  clamp plate stands 0.76 off the effector's face with the collar seated.
* The `hotend_fan` clamp has five screw holes, not six: its groove slot
  takes the sixth position.
* `extruder.scad` drills three of the gearmotor's four screw holes; the
  fourth position is the filament path.  Mounted on the top beam with
  the filament path vertical, the push-fit would pass through the beam,
  so the path is horizontal: in from outside the frame, out toward the
  centre.
* The vertices' bed-adhesion pads reach 6 mm past the beam faces and
  are cut off, as a builder cuts them.
* The ball joints are drawn from their own mechanics rather than a
  datasheet: 6 mm hollow balls on 3 mm sleeves, 7.4 mm rings flared at
  66 degrees, stems glued into the tubes, button-head screws into the
  nut traps the carriage and effector are drawn with -- because the rods
  swing 21 degrees out of their screws' planes at the print radius and
  the three arms' fasteners meet at the effector's corners.

Not drawn: the retractable Z probe and its spring, the FSR glass frame,
the recirculating-roller carriage, the PG35L extruder body variant, the
line-drive spool, the switch holder, the card and the logotype; the
electronics and wiring; the spool.  The Bowden tube is a solid sweep of
varying length (molejo has no annulus and no length-true spline), and
the filament runs inside it.
