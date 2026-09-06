## ADDED Requirements

### Requirement: Balls on the horn screws
Each carriage and each effector arm SHALL carry one M3 x 60 screw
through both horns with a 6.0 mm steel ball against each horn's outer
face (centre 23.0 mm from the horn pair's centre plane) and an M3 nut
outside each ball. The screw SHALL be drawn at 2.85 mm and the ball bore
at 3.05 mm.

#### Scenario: The ball is captured between horn and nut
- **WHEN** a ball is displaced 0.5 mm along the screw either way
- **THEN** it interferes with the horn on one side and with the nut on the other

### Requirement: Rod ends socket the balls
Each rod SHALL carry a rod end at each end whose spherical socket (6.1
mm) is concentric with its ball within 0.05 mm at every pose, whose
housing clears the horn face by 0.5 mm, and whose shank receives the 6.0
mm carbon tube 8 mm deep. The tube length SHALL be `diagonal_rod - 2 x
17.5` (180 mm).

#### Scenario: The socket holds the ball
- **WHEN** a rod end is displaced 0.15 mm in any of three axes at the centre pose
- **THEN** it interferes with its ball, and displaced 0.03 mm it does not
