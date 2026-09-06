## ADDED Requirements

### Requirement: The tube joins the two push-fits
A 4 mm PTFE tube SHALL run as a molejo spline from the push-fit under
the extruder body (tangent down) to the push-fit on top of the effector
(tangent down), through a middle point directly above the effector's
push-fit at the top frame's height plus 40 mm, with its moving
coordinates bound through ports from the drivers. Both push-fits SHALL
be drawn at their 4.0 mm tap-drill stub with a 10 mm body.

#### Scenario: The tube reaches the head everywhere
- **WHEN** the machine is posed at the centre, `Home`, `Bed` and each `TowerX/Y/Z` target
- **THEN** the tube's end ring is within 0.1 mm of the effector push-fit's mouth and its start ring within 0.1 mm of the extruder push-fit's mouth

#### Scenario: The tube clears the frame
- **WHEN** the machine is posed at `Home` and at each tower target
- **THEN** the tube shares no volume with any horizontal beam or vertex

### Requirement: The filament runs the whole path
A 1.75 mm filament SHALL run from 30 mm above the extruder's entry, down
the extruder's filament path, along the tube's own spline, through the
effector's push-fit and the J-Head's bore to 5 mm above the nozzle tip.

#### Scenario: The filament stays inside the tube
- **WHEN** the machine is posed at the centre and at `TowerZ`
- **THEN** every vertex of the filament's mesh between the two push-fits lies within 1.0 mm of the tube's axis (inside a 2 mm bore)
