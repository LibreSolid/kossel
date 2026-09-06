## 1. Layer and constants

- [x] 1.1 `pyproject.toml`, `simulation/` package, `scad.py` (import_scad handles, source set), `part.py` (ScadPart, PrintedPart, curve), `materials.py`
- [x] 1.2 `hardware.py` (OpenBeam profile, MGN12, NEMA 17, PG35L, GT2 pulley, 623/625, M3/M5 fasteners, ball, rod end, J-Head, glass, push-fit, PSU) and `layout.py` (tower angles, radii, rows, stations from the scad numbers)
- [x] 1.3 `kinematics.py` over `solid_node.math`: carriage height, rod tilt and azimuth, belt travel to pulley angle

## 2. Frame (tower-frame-joint)

- [x] 2.1 Write the frame contracts (beam closure, refused radius, screws in slots, interference, support) red against a frame whose beams are placed at the vertex origin
- [x] 2.2 Extrusion, vertices, beams, screws and nuts placed; contracts green; `--set tower_radius=150` builds

## 3. Towers (rail-carriage-fit, belt-drive)

- [x] 3.1 Rail, block, carriage, endstop, switch: contracts red (block off the rail axis), then green
- [x] 3.2 Motor, pulley, idler bearings and bolt, belt wrap with `clamp` port; riding and tooth-travel contracts red (pulley at the wrong station), then green
- [x] 3.3 Pulley and idler rotation from the carriage height; meshing perturbation contract red (no rotation), then green

## 4. Effector and hot end (hotend-mount, ball-joint)

- [x] 4.1 Effector flipped, J-Head parts, clamp, screws, push-fit; pocket, groove and nozzle-drop contracts red (effector unflipped), then green
- [x] 4.2 Horn screws, balls, nuts on carriages and effector; capture contracts red then green

## 5. Kinematics (delta-kinematics, ball-joint)

- [x] 5.1 Root drivers and tower ports; carriage heights contract red (rods drawn vertical), then green
- [x] 5.2 Rods (tube + two rod ends) posed by tilt and azimuth; socket-on-ball and length contracts at five poses red then green
- [x] 5.3 Instructions; scenario sweep through every instruction with interference sampled

## 6. Bed, extruder, Bowden, PSU (bed-mount, extruder-mount, bowden-path, power-supply-mount)

- [x] 6.1 Tabs, glass; contracts
- [x] 6.2 Bracket, gearmotor, body, drive gear, idler screw and bearing, push-fit; contracts
- [x] 6.3 Tube and filament splines with ports bound by the root; reach, clearance and containment contracts
- [x] 6.4 Brackets and brick; contract

## 7. Evidence and record

- [x] 7.1 Root integrity contracts swept over the instruction scenario; mutation check (drop the effector offset from R, flip the rod azimuth sign, misplace the pulley station) and note which contract catches each
- [x] 7.2 `solid build`; read `viewer.json` (drivers, instructions, flexible specs, pieces); snapshots at rest and at `Home`; exact run of every test file
- [x] 7.3 README section on the simulation (knobs, sourced parts, what is and is not drawn); archive the change, fill `Purpose` in every spec; commit
