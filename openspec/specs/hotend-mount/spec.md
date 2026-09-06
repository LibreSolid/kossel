# hotend-mount Specification

## Purpose

The J-Head in the effector's pocket and the groove clamp under it, and the nozzle tip as the machine's Z zero.

## Requirements
### Requirement: The J-Head seats in the effector
The effector SHALL be mounted pocket-down and thread-up (180 degrees
about X). A J-Head with a 16 x 4.76 collar, 12 x 4.7 groove (the standard's 4.64
opened so the 4.6 plate clears both ways), 16 x 30 body and 11.3 mm of
brass below it SHALL have its collar seated on the pocket floor; the
printed `hotend_fan` clamp SHALL be flipped under it with its 4.6 mm
plate in the groove and its five M3 x 16 screws (the clamp's slot takes
the sixth position) at the 12.5 mm mount radius through the effector;
the nozzle tip SHALL be 50.87 mm below the effector's joint plane.

#### Scenario: The collar cannot leave the pocket downward
- **WHEN** the J-Head is displaced 0.2 mm downward
- **THEN** its collar interferes with the clamp plate, and displaced 0.02 mm it does not

#### Scenario: The plate is in the groove
- **WHEN** the clamp plate is displaced 0.1 mm up or down
- **THEN** it interferes with the collar going up and with the body going down, and clears both at 0.02 mm

#### Scenario: Z is the nozzle
- **WHEN** the drivers are bound to `z` 0 at the centre
- **THEN** the nozzle tip's lowest vertex is at the glass top within 0.01 mm
