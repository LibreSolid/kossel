# ball-joint Specification

## Purpose

The hollow balls on the horns and the rod ends that socket them, at every pose the machine reaches.

## Requirements
### Requirement: Hollow balls on short screws into the horns' nut traps
Each horn of each carriage and each effector arm SHALL carry a 6.0 mm
hollow ball on a 4 mm sleeve -- 3.0 mm toward the horn and 3.1 mm toward
the screw head -- with the ball's centre 23.05 mm from the horn pair's
centre plane, held by an M3 button-head screw (M3 x 20 on the carriage,
M3 x 25 on the effector) running in through the sleeve and the horn to an
M3 nut in the trap the part is drawn with (the carriage's hex cones at
x = 4 to 12, the effector's channel at |x| < 8). The screw SHALL be drawn
at 2.85 mm and the ball bore at 3.05 mm.

#### Scenario: The ball is captured between horn and head
- **WHEN** a ball is displaced 0.1 mm along the screw either way
- **THEN** it interferes with the horn on one side and with the screw head on the other

### Requirement: Rod ends socket the balls
Each rod SHALL carry a rod end at each end: a 7.4 mm ring 3.4 wide whose
spherical socket (6.1 mm) is concentric with its ball within 0.05 mm at
every pose, flared at 66 degrees either side so the ball's sleeve passes
through it at the 21 degree swing the instructions reach, with a 3.9 mm
stem glued 8 mm into the 6.0 mm carbon tube. The tube's end face SHALL
be 17.5 mm from the ball's centre and its length `diagonal_rod - 2 x
17.5` (180 mm). The machine SHALL spin each rod about its own axis so the
rings lie as near their screws as the pose allows, and at every pose the
rod ends SHALL clear the horns, the screws and the effector.

#### Scenario: The socket sits on the ball
- **WHEN** the machine is posed at the centre, the bed, home and each tower target
- **THEN** every rod end comes no closer than 0.03 mm and no further than 0.08 mm from its ball, and shares no volume with the horn's screw or the printed part it hangs on
