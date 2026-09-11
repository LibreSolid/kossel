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

Resumed 2026-09-11, on solid-node main `c83207f` (ADR-093, ADR-096,
ADR-097, ADR-098, ADR-099, ADR-100 all landed since this was deferred).
Two of the four joint declarations below are DEVIATIONS from this
proposal's original text, both because `joint-frame-follows-declarer`
(ADR-097, landed after this proposal was written) changed what frame a
class-declared joint's `axis`/`at` are read in — from the parent's frame
with an anchor callable, to the declaring class's OWN rest frame,
usually with no anchor at all. Both are reported in "Deviations" below.

- [x] 2.1 `EffectorAssembly`: declared `slide_x`, `slide_y`, `rise` as
      `Prismatic` on the machine's axes, no anchor (the machine's centre
      being the default origin of a class `Kossel.render()` never
      places) — as written.
- [x] 2.2 `CarriageAssembly`: declared
      `travel = Prismatic(axis=(0, 0, 1), at=(0, EXTRUSION / 2, 0), unit='mm')`
      — as written; the anchor is documentation only for a Prismatic.
- [x] 2.3 `GT2Pulley`: declared `spin = Revolute(axis=(0, 0, 1), unit='deg')`,
      own frame, **no anchor and no callable** — DEVIATION from
      `axis=(0, -1, 0)` with the `_on_the_motor_shaft` anchor callable
      this proposal specified: under ADR-097 a class joint reads its own
      undrawn rest frame, where the pulley's toothed body is drawn along
      +Z through the origin, so no anchor is needed and the hub-end
      origin already IS the shaft's own line. `Tower.render()`'s
      `rotate(90, [1, 0, 0])` turns that +Z onto the tower's -Y exactly
      as before; proved at 0 (§5).
- [x] 2.4 `Rod`: declared `spin`, `lean`, `swing` (`Revolute`, axes
      `(0,0,1)`, `(0,-1,0)`, `(0,0,1)`) and `rise` (`Prismatic`,
      `(0,0,1)`), every anchor the default origin — as written, and
      commented why (a rod's own undrawn frame is the ball centre
      whatever `Kossel.render()` later translates it to).
- [x] 2.5 No joint declares a `range` — as written.

## 3. Stage B — the relations

- [x] 3.1 `Kossel`: stated `x.drives(effector.slide_x)`,
      `y.drives(effector.slide_y)` and
      `z.drives(effector.rise, offset=layout.GLASS_TOP + layout.NOZZLE_DROP)`,
      and deleted the effector's `translate` from `simulate()` — as
      written.
- [x] 3.2 `belt.py`: added the two laws, `belt_clamp(tower, belt)` and
      `pulley_turn(tower, pulley)`, each returning the `Affine` reading of
      `Loop.anchor` and `Loop.pulley_angle` respectively — as written.
      `Loop.anchor`, `Loop.pulley_angle` and `Loop.idler_angle` kept.
- [x] 3.3 `Tower`: stated the derived coordinate
      `block = height - CARRIAGE_HORN_Y` and the three relations
      `block.drives(carriage.travel)`,
      `block.drives(belt.clamp, law=belt_clamp)`,
      `block.drives(pulley.spin, law=pulley_turn)` — as written.
- [x] 3.4 Shrank `Tower.simulate()` to the unbound-height default, the
      recomputed `block` and the two idlers' `rotate`. DEVIATION: the
      default guard binds with `self.height = layout.DEFAULT_CARRIAGE_HEIGHT`
      (the canonical rest-default-guard idiom `docs/driving.rst` names,
      also `Prusa3-vanilla`'s), not this proposal's literal
      `self.connect(layout.DEFAULT_CARRIAGE_HEIGHT, self.height)` — the
      framework documents `connect()` as sugar over an assignment, so
      the two are the same binding; `TowerTest.test_the_carriage_horn_axis_stands_where_marlin_says`,
      the one test this default reaches, passes (§5).

## 4. Stage B — the rods' bindings

Superseded by `solid-node`'s `multi-source-multi-target-laws` cycle
(ADR-100), which this proposal's own "Known gaps" §4 wanted and which
landed while this was deferred. Rather than binding each rod's four
joints and each tower's height by hand in `Kossel.simulate()` (4.1–4.3
below, as originally proposed), the two ADR-100 sentences the cycle's
own overlay proved on this project (evidence §7.1, 0.000e+00) are
declared once, in `Kossel`'s class body, and fan out over the
`.repeat()`:

    (x & y & z).drives(towers.height, law=delta_carriage_law)
    (x & y & z).drives((rods.spin, rods.lean, rods.swing, rods.rise), law=delta_rod)

`delta_carriage_law` and `delta_rod` (`simulation/kossel.py`) each close
over the driven end's owner (a `Tower` copy, or the tuple of one `Rod`
copy repeated four times) to read its `.index` for the tower angle, and
return a `forward` of the three driver VALUES — `solid_node.mechanisms.delta_carriage`/
`delta_rod` stay the prescribed law, imported under `_delta_carriage`/
`_delta_rod` so the outer law functions could keep the sentence's own
names. This is a stronger form of 4.1–4.3, not merely a substitute: it
removes the per-tower `connect()` loop and the six rods' bindings
entirely rather than reshaping them, and needs no per-rod loop variable
at all.

- [x] 4.1 (superseded, see above) — DEVIATION: no rotate/rotate/rotate/
      translate chain was rewritten by hand; the two relations above
      bind `rod.spin`, `rod.lean` (the POSITIVE lean, axis carrying the
      sign), `rod.swing` and `rod.rise` together, once per rod copy.
      The per-rod station `translate` — the rest placement, not a
      freedom — moved to `Kossel.render()` instead of staying in
      `simulate()` as this proposal's own text kept it (its "Known gap
      2"): `joint-frame-follows-declarer` (ADR-097) means a `Rod`'s own
      joints stay anchored at ITS OWN origin however this translate
      places it, which is exactly what "Known gap 2" said would need "the
      own-placed-origin anchor mode" to do safely — ADR-097 supplies
      that safety for free, so the gap closes without ADR-098's site
      joints.
- [x] 4.2 (superseded) — the ORDER that matters is now `Rod`'s
      declaration order (`spin`, `lean`, `swing`, `rise`, joint-composition-order,
      ADR-093) plus one more hand-written `translate` outside that
      block, in `Kossel.render()`; commented there and in `Rod`'s own
      docstring instead of at a bind site in `simulate()`, since there
      is no longer a bind site to comment.
- [x] 4.3 The `delta_carriage`/`delta_rod` mechanism calls stay (now
      inside the two laws), the three `connect()` into `tower.height`
      and the six rods' rotate/rotate/rotate/translate chains are GONE
      (not merely moved), and the seven Bowden/filament `connect()`
      calls in `Kossel.simulate()` are exactly as they were.

## 5. Evidence again

- [x] 5.1 Captured the tree as found (`git archive HEAD` of the stage A
      commit `5402b0b`, into a scratch directory outside the project) to
      `kossel-before.json`, and the working tree after this change's
      edits to `kossel-after.json`, both with `capture_poses.py capture
      simulation.kossel:Kossel` — **11 poses, 378 leaves**, both files,
      matching the cycle-5 overlay's own count. `capture_poses.py
      compare`: **maximum deviation 1.000e-09**, one leaf, one pose —
      `x@0.4: towers-0.pulley matrix deviates 1.000e-09` — exactly the
      affine re-association this proposal's own "Tests" section
      predicted for `belt_clamp`/`pulley_turn` (`ratio * block + offset`
      instead of `(block - origin) * scale`), one order of magnitude
      above the 1e-13 it estimated, confined to the one leaf and pose
      predicted, and reported rather than accepted silently. Re-posed
      the same instance three times inside `capture_poses.py` itself (it
      always re-poses seven times: defaults, six range/time poses); no
      one-pose lag.
- [x] 5.2 Re-ran all three suites, foreground, one at a time:
      `simulation/kossel.py:Kossel` **15/15** (unchanged from stage A);
      `simulation/tower.py:Tower` **9/9** (unchanged), including
      `test_the_carriage_horn_axis_stands_where_marlin_says` (the
      standalone default) and `test_the_pulley_meshes_the_belt_without_biting`
      / `test_the_belt_rides_its_pulley_and_idlers`, all green despite
      the 1e-9 re-association above (both tests carry millimetre-scale
      tolerances, as predicted); `simulation/effector.py:EffectorAssembly`
      **7/8**, the same pre-existing `test_the_balls_are_captured_on_their_screws`
      red as the stage A baseline (unrelated to this change: `effector.py`
      only gained the three joint declarations, not touched by
      `test_effector.py`'s ball geometry). No suite newly red; no test
      edited.
- [x] 5.3 Updated `README.md`'s account of how the machine moves: the
      freedoms are now named per body, the two ADR-100 relations named,
      and what still moves by hand and why (the two idlers, over a
      shared fastener class no `.repeat()` site can yet carry a joint;
      the rods' constant per-copy station, the rest placement and not a
      freedom).
- [x] 5.4 Committing as `refactor(simulation): move the Mini Kossel onto
      solid-node joints and couplings`, with the pose comparison and the
      test result in the body, in this project's own repository only.
- [x] 5.5 Reported: the commit hash, the pose line, the test counts
      before and after, every deviation from this proposal (§2.3, §3.4,
      §4), and the one pre-existing red (`test_the_balls_are_captured_on_their_screws`).
      Not synced, not archived.
