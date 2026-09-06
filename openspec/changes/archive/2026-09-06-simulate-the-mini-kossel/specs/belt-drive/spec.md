## ADDED Requirements

### Requirement: The belt loop runs where the pulley and idler are
Each tower SHALL carry a NEMA 17 at `frame_motor`'s station (axis radial,
face 44 mm from the tower axis, shaft toward the tower), a 20 tooth GT2
pulley on its shaft at 29 mm from the tower axis, two 623 bearings on
the `frame_top` idler bolt at 25 to 33 mm, and a 6 mm GT2 belt as a
molejo wrap around the pulley's pitch circle and the idler's tooth-tip
circle in the vertical plane 26 to 32 mm from the tower axis. The wrap
SHALL be anchored on its rising span at the carriage's clamp height
through a `clamp` port the tower binds from the carriage height.

#### Scenario: The belt rides its pulley and idler
- **WHEN** a tower is built at the default carriage height
- **THEN** the belt's mesh shares less than 0.05 mm³ with the pulley and with each idler bearing, and its material band lies within 26 to 32 mm radially within 0.05 mm

#### Scenario: The teeth travel with the carriage
- **WHEN** the carriage is raised by exactly one tooth pitch (2.0 mm)
- **THEN** every ring of the belt's mesh has the same tooth depth as before within 0.001 mm, and raising it by half a pitch moves a crest to a root

### Requirement: The pulley turns with the belt
Each tower SHALL turn its pulley by the belt travel over the pulley's
pitch radius as the carriage moves, with a groove under every tooth, and
turn its idler bearings by the belt travel over their riding radius.

#### Scenario: The pulley meshes without biting
- **WHEN** the pulley is turned by 2 degrees either way from its posed angle
- **THEN** it interferes with the belt, and turned by 0.2 degrees it does not (the pulley is cut 0.1 mm inside the belt, a twentieth of a millimetre of play on a 56 degree flank)
