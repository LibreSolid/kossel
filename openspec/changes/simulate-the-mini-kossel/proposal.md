## Why

This repository is Johann Rocholl's Mini Kossel: the OpenSCAD sources of
its printed parts, one file per part, each drawn flat for the printer.
Nothing in it is the machine. There is no frame, no tower, no belt, no
rod between a carriage and the effector, and no statement of how the
three carriages have to stand for the nozzle to be at a point. A maker
who wants to see the printer move, or to check that a part they changed
still fits the parts around it, has only the plates and their own
imagination.

What physically goes wrong today is everything the drawings cannot say:
whether the horizontal beams the vertex is cut for really meet the next
vertex at the radius the firmware is configured to; whether a 215 mm
rod reaches from a carriage horn to an effector horn at every point of
the bed; whether the belt the carriage clamps runs where the idler and
the pulley are; whether the hot end the effector is pocketed for
hangs where the machine's Z zero says it does. None of these has been
drawn, so none of them can be wrong, and none of them can be right.

## What Changes

- A solid-node project in `simulation/` that reads the OpenSCAD design as
  it is and assembles it into the machine: every printed part is one
  `.scad` module called through solid2's `import_scad`, and only what the
  design does not draw is modelled here — the sourced parts (OpenBeam
  extrusions, linear rails and blocks, motors, pulleys, bearings,
  screws, nuts, balls and rod ends, carbon tubes, the J-Head, the
  glass, the push-fit connectors, the power supply) and the flexible
  parts (three GT2 belts, the Bowden tube, the filament).
- Delta kinematics as the machine's drivers: `x`, `y`, `z` are the
  nozzle's position over the glass, the three carriage heights follow
  from them, the six diagonal rods swing to join the horns, the belts
  are redrawn from where the carriages hold them and the pulleys turn.
- Instructions on the root for positioning the axes: `Home` (all three
  carriages up to the endstops), `Center`, `Bed`, one move to the print
  radius under each tower, and `Rest`.
- Every part carries the colour of the material it is made of.
- Contracts prove the interfaces the drawings leave open: frame closure
  at the configured radius, rods of the declared length landing on both
  joints at every pose, belts riding pulleys and idlers and following
  their carriages, the hot end's tip at the machine's Z zero, no two
  rigid parts sharing volume anywhere in the travel.

## Capabilities

### New Capabilities
- `tower-frame-joint`: vertical extrusion in its vertices, horizontal
  beams on the vertex sides, the frame's closure at the tower radius,
  the M3 screws and slot nuts that hold it.
- `rail-carriage-fit`: the linear rail on the tower face, its block, the
  printed carriage on the block, the endstop above the rail's end, and
  the homing height they define.
- `belt-drive`: the GT2 loop from the motor pulley to the idler, in the
  tower's belt plane, clamped to the carriage; teeth that travel with it;
  a pulley that turns with them.
- `delta-kinematics`: the drivers, the inverse kinematics, the rods'
  reach to both joints, the effector's pose and the root instructions.
- `ball-joint`: the balls on the M3 screws against the horn faces and
  the rod ends' sockets around them.
- `hotend-mount`: the J-Head in the effector's pocket and the groove
  clamp, and the nozzle tip as the machine's Z zero.
- `bed-mount`: the glass on the tabs, the tabs on the upper bottom beams,
  the print surface height.
- `extruder-mount`: the extruder bracket on the top beam, the gearmotor
  in its cradle, the body on the motor, drive gear and idler on the
  filament.
- `bowden-path`: the push-fits at both ends, the tube's shape following
  the effector, the filament through the drive, the tube and the hot end.
- `power-supply-mount`: the two brackets on the bottom beam rows and the
  brick between them.

### Modified Capabilities
- (none; this is the project's first design change)

## Impact

- New `pyproject.toml` naming `simulation.kossel:Kossel`, new package
  `simulation/` beside the `.scad` sources, `openspec/` as the design
  record, `README.md` gaining a section on the simulation.
- The `.scad` sources are not edited. Where the model has to disagree
  with a drawing it says so in the design and in a contract.
- Out of scope, recorded for a later change: the retractable Z probe
  and its spring (`retractable.scad`), the alternative glass frame for
  FSR levelling (`glass_frame.scad`), the recirculating-roller carriage,
  the PG35L extruder body variant, the line-drive spool, the power switch
  holder, the card and the logotype.
- Uses solid-node 0.6 with the declarative API and molejo 0.2 as
  published; no framework change is needed.
