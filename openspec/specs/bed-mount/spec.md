# bed-mount Specification

## Purpose

The glass on its three tabs on the upper bottom beams, and the print surface height it defines.

## Requirements
### Requirement: The glass rests on three tabs
Three printed `glass_tab`s SHALL be screwed to the top slot of each upper
bottom beam (row at 30 mm) at the beam's midpoint, round end outward,
with an M3 x 8 and slot nut; a 170 x 3 mm round glass SHALL rest on
their 0.7 mm adhesive pads, so the glass top is `45 + 3.6 + 0.7 + 3` plus
three 0.05 seating standoffs, `52.45` mm above the floor and the glass edge is 85 mm from the centre,
0.75 mm past the tab's intended edge line.

#### Scenario: The glass sits on all three pads
- **WHEN** the glass is displaced 0.05 mm downward
- **THEN** it interferes with each of the three pads

#### Scenario: The glass is centred
- **WHEN** the bed is built
- **THEN** the glass's top face is at 52.45 mm within 0.01 and its centre within 0.05 mm of the machine axis
