## ADDED Requirements

### Requirement: The frame closes at the tower radius
The root SHALL declare `tower_radius` (145.0 mm, the distance from the
printer's centre to each tower's inner face), `vertical_extrusion` (600.0
mm) and `horizontal_extrusion` (240.0 mm). Three 15 x 15 vertical
extrusions SHALL stand at `tower_radius + 7.5` from the centre at 210,
330 and 90 degrees, from the floor to `vertical_extrusion`. Nine
horizontal extrusions of `horizontal_extrusion` SHALL run between the
vertices in three rows — bottom faces at 0, 30 and `vertical_extrusion -
15` — each on the vertex's beam line (16 mm off the vertex Y axis, 30
degrees from it, drawn 0.05 further out so the beam can be asked whether
it touches the vertex), so that adjacent vertices' beam lines coincide. The
beam end SHALL lie between 7.5 and 17.5 mm along the beam line from the
vertex Y axis, and the frame's `check()` SHALL refuse a `tower_radius`
that puts it outside that window.

#### Scenario: The horizontal beams meet the next vertex
- **WHEN** the frame is built at the default parameters
- **THEN** each horizontal beam's two end faces are each within 0.05 mm of the beam line reference of its two vertices, and the perpendicular distance from the centre to every beam axis equals `tower_radius / 2 + 3.75 + 16.05` within 0.05 mm

#### Scenario: A tower radius that leaves the beams short is refused
- **WHEN** the root is constructed with `tower_radius` 160.0
- **THEN** construction raises naming the beam end window

### Requirement: Vertices hold the extrusions
Each tower SHALL carry `frame_motor` at the bottom (base on the floor)
and `frame_top` at the top (top face at `vertical_extrusion`), both with
the vertical extrusion through their cutout and the horizontal beams
against their beam faces. The frame SHALL carry M3 x 8 screws at every
screw socket the vertices cut — one per 30 mm of vertex height into the
vertical extrusion, two per beam end — each with an M3 nut in the
extrusion's slot. The OpenBeam slot SHALL be drawn 3.0 mm wide at the
face for the vertex's tabs, over a 5.6 mm cavity 4.4 mm deep for the
nuts.

#### Scenario: No two frame parts share volume
- **WHEN** the frame is built
- **THEN** no two of its rigid solids interfere, and every screw shank lies within its extrusion's slot cavity

#### Scenario: The frame stands
- **WHEN** the frame is built
- **THEN** every vertex and vertical extrusion stands on the floor, and every beam, rail and tab is held by screws whose shanks reach their slot nuts (a support proof is not asked; see the design)
