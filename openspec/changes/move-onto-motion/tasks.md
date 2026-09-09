# Tasks

Behaviour-preserving throughout: the acceptance is that every leaf's world
matrix is unchanged at every pose, so evidence is captured before the first
motion edit and compared after the last. Run everything from the project
root with `PYTHONPATH=.` and the workspace venv
(`/home/asa/devel/libresolid-studio/.venv/bin/python`, `.venv/bin/solid`).
Never run two suites at once. Never edit a test: if one blocks you, stop and
report the assertion and the reason.

## 0. Pre-existing state

- [x] 0.1 `git status --porcelain` is empty (checked 2026-09-09, `master` at
      `b7f4317`). Nothing to commit; skip stage 0 and say so in the stage A
      commit body.

## 1. Stage A — imports and the baseline

- [x] 1.1 Change three import lines and nothing else:
      `simulation/tower.py`, `simulation/belt.py` and `simulation/bowden.py`
      take `TranslationalPort` from `solid_node.motion.ports`
      (`tower.py` keeps `AssemblyNode`, `bowden.py` keeps `MolejoNode`,
      from `solid_node.node`). Confirmed with
      `PYTHONPATH=. python -c "import simulation.kossel"` (also
      `simulation.tower` and `simulation.effector`), all OK. Checked every
      other module and test file for a moved-name import from
      `solid_node.node`: none found (the remaining `AssemblyNode`,
      `Solid2Node` and `MolejoNode` imports elsewhere are not moved names).
- [x] 1.2 Ran the declared model's suite: `solid test --faceted
      simulation/kossel.py:Kossel`. **15/15 passed** (faceted kernel,
      volume epsilon 0 mm3): `test_a_tower_radius_the_beams_cannot_reach_is_refused`,
      `test_assembly_integrity`,
      `test_frame_screws_reach_their_nuts_and_miss_the_metal`,
      `test_home_stops_short_of_the_switch`,
      `test_rods_of_the_declared_length_reach_both_joints`,
      `test_solid_integrity`, `test_the_brick_is_held`,
      `test_the_drive_pinches_the_filament`,
      `test_the_filament_stays_inside_the_tube`,
      `test_the_glass_rests_on_three_pads`,
      `test_the_horizontal_beams_close_the_frame`,
      `test_the_motor_lies_in_its_cradle`,
      `test_the_nozzle_position_drives_the_carriages`,
      `test_the_tube_reaches_the_head_everywhere` (`KosselTest`), and
      `test_the_instructions_move_the_head_without_collision`
      (`KosselScenarioTest`). No baseline red.
- [x] 1.3 Ran the two sub-assembly suites the same way:
      `simulation/tower.py:Tower` — **9/9 passed** (`test_assembly_integrity`,
      `test_solid_integrity`, `test_the_belt_rides_its_pulley_and_idlers`,
      `test_the_block_rides_the_rail_without_touching_it`,
      `test_the_carriage_horn_axis_stands_where_marlin_says`,
      `test_the_carriage_screws_meet_the_block_pattern`,
      `test_the_endstop_hangs_its_switch_over_the_rail`,
      `test_the_pulley_and_idlers_sit_on_their_shafts`,
      `test_the_pulley_meshes_the_belt_without_biting`).
      `simulation/effector.py:EffectorAssembly` — **7/8 passed, 1 failed**:
      `EffectorAssemblyTest.test_the_balls_are_captured_on_their_screws` is
      RED at baseline —
      `AssertionError: balls-0 should be blocked displaced 0.1mm along
      [1, 0, 0] against effector (no intersection)` in `assertBlockedBeyond`
      — pre-existing, unrelated to this change: `effector.py` and
      `test_effector.py` were not touched by the stage A import fix (which
      only edits `tower.py`, `belt.py`, `bowden.py`), so this is the
      standing baseline, not a regression. The other 7
      (`test_assembly_integrity`, `test_solid_integrity`,
      `test_the_clamp_screws_reach_the_shroud`,
      `test_the_collar_seats_in_the_pocket`,
      `test_the_plate_is_in_the_groove`,
      `test_the_pushfit_sits_in_the_thread`, `test_z_is_the_nozzle`) passed.
      Confirmed there are no plain `pytest` tests (only the three
      `test_*.py` files driven through `solid test --faceted`).
- [x] 1.4 Captured poses on the model as it stands:
      `PYTHONPATH=. python <shop>/docs/motion-general-refactor/capture_poses.py
      capture simulation.kossel:Kossel /tmp/kossel-before.json
      /tmp/kossel-extra-before.json`, the extra file holding the six
      instructions' targets (`Home`, `Center`, `Bed`, `TowerX`, `TowerY`,
      `TowerZ`) read off `Kossel.instructions[...].targets` directly so the
      numbers are the project's own. Result: **17 poses, 378 leaves ->
      /tmp/kossel-before.json**.
- [x] 1.5 Commit as `refactor(simulation): import ports from
      solid_node.motion`, with the baseline in the message body, together
      with this change's `proposal.md` and `tasks.md`.

## 2. Stage B — the joints

- [ ] 2.1 `EffectorAssembly`: declare `slide_x`, `slide_y`, `rise` as
      `Prismatic` on the machine's axes, anchored at the machine's centre.
- [ ] 2.2 `CarriageAssembly`: declare
      `travel = Prismatic(axis=(0, 0, 1), at=(0, EXTRUSION / 2, 0), unit='mm')`
      in the tower's frame.
- [ ] 2.3 `GT2Pulley`: declare `spin = Revolute(axis=(0, -1, 0), at=...)`
      with the anchor a callable of the realized pulley returning
      `(0, IDLER_STATION + pulley.teeth_start + PULLEY_WIDTH / 2,
      MOTOR_VERTEX_HEIGHT / 2)` — the tower's frame, the pulley's own placed
      origin, single-sourced off `teeth_start` as `Tower.render()` reads it.
- [ ] 2.4 `Rod`: declare `spin`, `lean`, `swing` (`Revolute`, axes
      `(0,0,1)`, `(0,-1,0)`, `(0,0,1)`) and `rise` (`Prismatic`,
      `(0,0,1)`), every anchor left at the default origin — correct only
      because a rod has no rest placement. Comment that.
- [ ] 2.5 No joint declares a `range`: the machine's limits live on the
      drivers.

## 3. Stage B — the relations

- [ ] 3.1 `Kossel`: state `x.drives(effector.slide_x)`,
      `y.drives(effector.slide_y)` and
      `z.drives(effector.rise, offset=layout.GLASS_TOP + layout.NOZZLE_DROP)`,
      and delete the effector's `translate` from `simulate()`.
- [ ] 3.2 `belt.py`: add the two laws, `belt_clamp(tower, belt)` and
      `pulley_turn(tower, pulley)`, each returning the `Affine` reading of
      `Loop.anchor` and `Loop.pulley_angle` respectively — the same
      coefficients, not a second derivation. Keep `Loop.anchor`,
      `Loop.pulley_angle` and `Loop.idler_angle`.
- [ ] 3.3 `Tower`: state the derived coordinate
      `block = height - CARRIAGE_HORN_Y` and the three relations
      `block.drives(carriage.travel)`,
      `block.drives(belt.clamp, law=belt_clamp)`,
      `block.drives(pulley.spin, law=pulley_turn)`.
- [ ] 3.4 Shrink `Tower.simulate()` to the unbound-height default, the
      recomputed `block` and the two idlers' `rotate` — the derived
      coordinate is unbound inside its own `simulate()`, so `block` is
      recomputed from `self.height.value` there.

## 4. Stage B — the rods' bindings

- [ ] 4.1 In `Kossel.simulate()`, replace each rod's rotate/rotate/rotate/
      translate chain with `rod.spin`, `rod.lean = tilt` (positive, the
      axis carries the sign), `rod.swing`, `rod.rise = height`, then the
      station `translate([..., ..., 0])`.
- [ ] 4.2 Comment that the five statements' ORDER is the composition:
      motion is inserted at the end of the motion block in call order,
      innermost first, so this reproduces
      `T(station) · Rz(azimuth) · Ry(-tilt) · Rz(spin)`.
- [ ] 4.3 Leave the `delta_carriage`/`delta_rod` calls, the `spin`
      arithmetic, the three `connect()` into `tower.height` and the seven
      Bowden/filament `connect()` calls exactly as they are.

## 5. Evidence again

- [ ] 5.1 Re-capture to `/tmp/kossel-after.json` (both files) and
      `capture_poses.py compare`. Expect maximum deviation 0 on every leaf
      of the effector, the carriages and the rods. A deviation of order
      1e-13 confined to the pulleys and the belts is the affine
      re-association of `Loop.anchor`/`Loop.pulley_angle` and is to be
      reported, with its magnitude, not silently accepted.
- [ ] 5.2 Re-run all three suites: the same tests green as the baseline,
      none newly red. Watch
      `TowerTest.test_the_carriage_horn_axis_stands_where_marlin_says`
      (the standalone default), `test_the_pulley_meshes_the_belt_without_biting`
      and `test_the_belt_rides_its_pulley_and_idlers`.
- [ ] 5.3 Update `README.md`'s account of how the machine moves: the
      freedoms are now declared on the bodies that have them, and what
      still moves by hand and why (the two idlers, the rod station, the
      delta law's three-source bindings).
- [ ] 5.4 Commit as `refactor(simulation): move the Mini Kossel onto
      solid-node joints and couplings`, with the pose comparison and the
      test result in the body.
- [ ] 5.5 Report the two commit hashes, the pose line, the test counts
      before and after, every deviation from this proposal, and any test
      you believe needs a change. Do not sync or archive; the orchestrator
      reviews first.
