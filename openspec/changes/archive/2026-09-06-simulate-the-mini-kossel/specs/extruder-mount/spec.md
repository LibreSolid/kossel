## ADDED Requirements

### Requirement: The extruder hangs on the front top beam
The printed `frame_extruder` bracket SHALL sit on the top face of the
front top beam (between towers X and Y) at its midpoint with three M3 x
8 screws and slot nuts; a PG35L gearmotor (35 mm body, 22.5 x 3.35
gearhead boss, 5 mm shaft) SHALL lie in its cradle with its axis along
the beam 26 mm above the beam top; the printed `extruder` body SHALL be
bolted to the gearhead with the three M3 x 25 screws the drawing drills
for, standing beside the bracket along the beam with its filament path
horizontal -- entering from outside the frame and leaving through its
push-fit toward the centre, because a vertical path would put the
push-fit through the beam -- with an MK7 drive gear on the shaft and a
625 bearing on an M5 screw pinching a 1.75 mm filament path.

#### Scenario: The motor lies in the cradle
- **WHEN** the extruder assembly is built
- **THEN** the motor body displaced 0.2 mm downward interferes with the bracket and displaced 0.02 mm does not

#### Scenario: The drive pinches the filament
- **WHEN** the filament is built through the extruder
- **THEN** the filament's axis passes 6.5 mm from the drive gear's axis and the gear's hobbed radius plus half the filament equals that within 0.3 mm
