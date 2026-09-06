## ADDED Requirements

### Requirement: The tube joins the two push-fits
A 4 mm PTFE tube SHALL run as a molejo spline from the push-fit on the
extruder body (leaving toward the centre) to the push-fit on top of the
effector (arriving from above), its far end bound through ports from
the drivers; drawn as a solid sweep, since molejo has no annulus. Both
push-fits SHALL be drawn with a 3.8 mm stub at the tap drill they
self-tap into, a 10 mm body and a bore whose floor seats the tube 4.5 mm
above the stub's foot.

#### Scenario: The tube reaches the head everywhere
- **WHEN** the machine is posed at the centre, `Home`, `Bed` and each `TowerX/Y/Z` target
- **THEN** the tube's surface passes within 0.1 mm of the effector push-fit's seat and of the extruder push-fit's seat, leaving the one toward the centre and arriving at the other from above

#### Scenario: The tube clears the frame
- **WHEN** the machine is posed at `Home` and at each tower target
- **THEN** the tube shares no volume with any horizontal beam or top vertex

### Requirement: The filament runs the whole path
A 1.75 mm filament SHALL run from 30 mm above the extruder's entry, down
the extruder's filament path, along the tube's own spline, through the
effector's push-fit and the J-Head's bore to 5 mm above the nozzle tip.

#### Scenario: The filament stays inside the tube
- **WHEN** the machine is posed at the centre and at `TowerZ`
- **THEN** every vertex of the filament's mesh between the two push-fits lies inside the tube's solid
