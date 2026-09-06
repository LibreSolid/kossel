# delta-kinematics Specification

## Purpose

The nozzle position as the machine's drivers, the carriage heights that follow, the rods that join them, and the instructions that move the head.

## Requirements
### Requirement: The nozzle position drives the carriages
The root SHALL declare drivers `x` and `y` (mm from the glass centre,
range ±90) and `z` (mm of nozzle tip above the glass, range 0 to the
home height), and `diagonal_rod` (215.0 mm, ball centre to ball centre).
Tower `i` at angle `a_i` SHALL hold its carriage joint at height
`z_e + sqrt(L² - (x - R cos a_i)² - (y - R sin a_i)²)`, where `z_e` is
the effector joint plane (`glass_top + z + 50.87`, the J-Head stack of 4.76 + 4.7 + 30 + 8.26 + 3.05 with two 0.05 seating standoffs; `glass_top` is 52.45), `L` is
`diagonal_rod` and `R` is `tower_radius - 19.5 - 20`.

#### Scenario: The centre pose
- **WHEN** the drivers are bound to `x` 0, `y` 0, `z` 50
- **THEN** all three carriage joint axes stand at the same height, equal to the test's own evaluation of the formula within 0.01 mm, and the nozzle tip is 50 mm above the glass within 0.01 mm

#### Scenario: An off-centre pose
- **WHEN** the drivers are bound to `x` 60, `y` -30, `z` 20
- **THEN** each carriage joint height equals the test's own evaluation within 0.01 mm and the three differ from one another

### Requirement: Rods of the declared length reach both joints
Six rods SHALL be posed so that at every pose each rod's two ball-socket
centres coincide with a carriage ball centre and the matching effector
ball centre within 0.05 mm, and the distance between the two centres is
`diagonal_rod` within 0.01 mm. The two rods of a tower SHALL stay
parallel.

#### Scenario: Rods land on their joints across the bed
- **WHEN** the machine is posed at the centre, at each `TowerX/Y/Z` target and at `Home`
- **THEN** every rod's socket centres coincide with their balls within 0.05 mm

### Requirement: Instructions position the axes
The root SHALL declare `Home` (all carriages to the homing height, the
nozzle at the top centre), `Center` (`x` 0, `y` 0, `z` 50: the rest
pose), `Bed` (`z` 0 at the centre) and `TowerX`, `TowerY`, `TowerZ`
(90 mm toward each tower at `z` 20).

#### Scenario: No interference along the moves
- **WHEN** a simulation triggers `Home`, `Bed`, `TowerX`, `TowerY`, `TowerZ` and `Center` in turn, sampling every 0.25 s
- **THEN** no two rigid solids share volume at any sample
