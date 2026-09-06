# rail-carriage-fit Specification

## Purpose

The linear rail on the tower face, the block on it, the printed carriage on the block, and the endstop that caps the travel.

## Requirements
### Requirement: Rail, block and carriage stack on the tower face
Each tower SHALL carry a 12 x 8 mm linear rail of `rail_length` (400.0
mm, declared on the root) centred on its inner face, with its top end 15
mm below the top vertex; an MGN12H block (27 wide, 44.5 long, top face
13 mm off the tower face, a channel over the rail with 0.1 mm clearance
per side) on it; and the printed `carriage` on the block's top with its
horns upward, so the ball-joint screw axis is 19.5 mm off the tower
face and 16 mm above the block's centre. The carriage's four M3 screws
SHALL land in the block's 20 x 20 pattern: the lower two through 6 mm of
plate (M3 x 10), the upper two down through the horn and belt clamp the
drawing runs those holes through (M3 x 18).

#### Scenario: The carriage's screw holes meet the block's pattern
- **WHEN** a tower is built at rest
- **THEN** each of the carriage's four screw shanks passes through the block within 0.1 mm of a hole centre at (±10, ±10)

#### Scenario: The block slides on the rail without touching it
- **WHEN** the block is displaced 0.05 mm toward the rail along its channel normal and 0.15 mm
- **THEN** it clears the rail at the first and interferes at the second

### Requirement: The endstop caps the travel
Each tower SHALL carry the printed `endstop` on the tower face directly
under the top vertex, microswitch on its centre-facing side, and the
travel's top (home) SHALL be the carriage height at which the block's top
is 0.5 mm below the switch's lever tip (10.5 mm below the endstop's
centre).

#### Scenario: Home stops short of the switch
- **WHEN** the machine is posed at `Home`
- **THEN** every block clears its switch, and displacing any block 1.2 mm upward interferes with the switch
