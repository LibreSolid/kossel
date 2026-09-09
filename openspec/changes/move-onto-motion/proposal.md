# Move the Mini Kossel onto the motion layer

## Why

solid-node's ports and the declared time base left `solid_node.node` for
`solid_node.motion.ports` with no re-export (ADR-087..089), so this project
does not import at all today:

    ImportError: module 'solid_node.node' has no attribute
    'TranslationalPort': ports and the declared time base moved to
    'solid_node.motion.ports'.

Fixing three import lines would make it run again. It would not make it say
what it is. The Mini Kossel is a machine of twelve moving bodies — one
effector, three carriages, three pulleys, six rods — and today not one of
them declares a freedom. Every motion is a `rotate()`/`translate()` call in
somebody's `simulate()`, and a reader has to work out from the call order
which body may move and about what. The same framework release that broke
the import added the vocabulary for saying it: a joint on the body that
moves, a relation for what drives what.

The machine wants to read:

- the effector translates in three coordinates, and those coordinates
  **are** the drivers `x`, `y`, `z`;
- each carriage slides up its tower, and the belt clamp, the pulley and the
  idlers of that tower are all functions of where it stands;
- each rod hangs from its carriage's ball and swings — a spin about its own
  axis, a lean from vertical, a swing about the machine's axis, and a rise
  with the carriage that carries it.

The delta inverse kinematics themselves (`delta_carriage`, `delta_rod` from
`solid_node.mechanisms`) stay where they are: they are a prescribed law of
three drivers over three towers, which is not a relation and is not meant
to be one.

## What changes

### Stage A, imports only

`simulation/tower.py`, `simulation/belt.py` and `simulation/bowden.py`
import `TranslationalPort` from `solid_node.node`; each becomes
`from solid_node.motion.ports import TranslationalPort` (bowden.py keeps
`MolejoNode` from `solid_node.node`, tower.py keeps `AssemblyNode`). No
test file imports a moved name. Nothing else changes; this is the baseline.

### The joints to declare

Nine declarations, thirty-three realized freedoms. No joint declares a
`range`: the machine's limits are on the drivers `x`, `y`, `z`, and a range
on a joint could only refuse a pose the drivers already allow.

**`EffectorAssembly` (simulation/effector.py) — three `Prismatic`.**

    slide_x = Prismatic(axis=(1, 0, 0), unit='mm')
    slide_y = Prismatic(axis=(0, 1, 0), unit='mm')
    rise    = Prismatic(axis=(0, 0, 1), unit='mm')

Axes in the parent's frame, which is the machine's: `Kossel.render()` never
places the effector, so its rest placement is the identity and the parent's
frame is its own. `at` is left at the origin, which is the machine's centre
on the glass — the point all three slides are measured from. Numbers: none;
the axes are the machine's own. These replace
`self.effector.translate([self.x, self.y, plane])` in `Kossel.simulate()`.
Three translations compose to the same matrix as one whatever order they
are bound in, so the composition-order gap recorded for OpenCycloid does
not touch this body.

**`CarriageAssembly` (simulation/carriage.py) — one `Prismatic`, realized
three times.**

    travel = Prismatic(axis=(0, 0, 1), at=(0, EXTRUSION / 2, 0), unit='mm')

Stated in the tower's frame, where `Tower.render()` places the carriage at
`translate([0, EXTRUSION / 2, 0])` — the rail's face. The anchor does not
affect a prismatic placement; it is the declared line of the slide, and
`EXTRUSION / 2 = 7.5` is where `tower.py` already puts the carriage. The
coordinate's value is the block centre's height, exactly the `block` the
tower computes today.

**`GT2Pulley` (simulation/motor.py) — one `Revolute`, realized three
times.**

    spin = Revolute(axis=(0, -1, 0), at=_on_the_motor_shaft, unit='deg')

    def _on_the_motor_shaft(pulley):
        return (0.0,
                IDLER_STATION + pulley.teeth_start + hardware.PULLEY_WIDTH / 2,
                MOTOR_VERTEX_HEIGHT / 2)

Both stated in the tower's frame. `Tower.render()` places the pulley
`rotate(90, [1, 0, 0])` then `translate([0, IDLER_STATION + teeth_centre,
motor_centre])`, so the pulley's own +Z — the axis it is drawn about, and
the axis it turns about today — is the tower's -Y; the anchor is the
pulley's own placed origin, hence the callable, which reads
`teeth_start` off the realized pulley exactly as `Tower.render()` does.
Numbers: `IDLER_STATION = 29.0` and `MOTOR_VERTEX_HEIGHT / 2 = 22.5` from
`layout.py`, `PULLEY_WIDTH` from `hardware.py`. The framework carries this
back to one `rotate(value, [0, 0, 1])` in the pulley's own frame with no
centring translations, which is byte-for-byte what
`self.pulley.rotate(loop.pulley_angle(block), [0, 0, 1])` produces today.
GT2Pulley has exactly one user (the tower), so the joint goes on the class
rather than on a subclass that would exist only to carry it; see "Known
gaps".

**`Rod` (simulation/rod.py) — four joints, realized six times.**

    spin  = Revolute(axis=(0, 0, 1), unit='deg')    # about its own axis
    lean  = Revolute(axis=(0, -1, 0), unit='deg')   # from vertical
    swing = Revolute(axis=(0, 0, 1), unit='deg')    # toward the effector
    rise  = Prismatic(axis=(0, 0, 1), unit='mm')    # with its carriage

Every anchor is the default origin, and that is correct only because a rod
has no rest placement: `Rod.render()` places its tube and its two rod ends
and never itself, so the rod's own frame is the machine's frame and the
origin is the carriage-end socket centre — the ball the rod hangs from.
`lean` is declared about `(0, -1, 0)` so it can be bound with the positive
lean `delta_rod` returns instead of today's `-tilt`; the matrix is the same.
Numbers: none — a rod's freedoms are the frame's axes.

### The relations to state

Six declarations, twelve realized. Both ends named in each sentence.

**In `Kossel` (simulation/kossel.py), three:**

    x.drives(effector.slide_x)
    y.drives(effector.slide_y)
    z.drives(effector.rise, offset=layout.GLASS_TOP + layout.NOZZLE_DROP)

Driver `x` → the effector's `slide_x` coordinate, ratio 1; likewise `y`.
Driver `z` → the effector's `rise`, ratio 1 with an offset, because the
joint plane the effector hangs on is `joint_plane(z) = GLASS_TOP + z +
NOZZLE_DROP`; both constants are `layout.py`'s, read off the bed stack and
the J-Head stack, and this is the one place the offset is written.

**In `Tower` (simulation/tower.py), one derived coordinate and three:**

    block = height - CARRIAGE_HORN_Y

    block.drives(carriage.travel)
    block.drives(belt.clamp, law=belt_clamp)
    block.drives(pulley.spin, law=pulley_turn)

`height` stays the tower's declared `TranslationalPort`: the ball-joint axis
height the machine's inverse kinematics hand it. `block` is the one derived
coordinate of this change — the carriage block's centre, `CARRIAGE_HORN_Y =
16.0` (carriage.scad) below the joint axis — and it is exactly the local
`block` variable `Tower.simulate()` computes today, promoted to a coordinate
so the three consumers read it by name.

- `block` → `carriage.travel`, ratio 1, no offset: the block centre's height
  IS the carriage's slide.
- `block` → `belt.clamp` (the molejo anchor, in millimetres of belt along
  the clamped span), `law=belt_clamp`, a new function in `belt.py`:

      def belt_clamp(tower, belt):
          loop = belt.loop
          return Affine(ratio=loop.clamp_scale,
                        offset=-loop.clamp_origin * loop.clamp_scale)

  which is `Loop.anchor()` — `(block - clamp_origin) * clamp_scale` — read
  as an affine. Its numbers come from `Loop`: `clamp_scale` and
  `clamp_origin` are `gt2.span_scale`/`gt2.span_origin` of the meshed
  pulley/idler circles, so the law must be handed the realized nodes, which
  is why it is a `law=` and not a `ratio=`.
- `block` → `pulley.spin`, `law=pulley_turn`, also in `belt.py`:

      def pulley_turn(tower, pulley):
          loop = Loop(tower.vertical_extrusion)
          reach = loop.pulley_radius + gt2.PITCH_LINE
          degrees = 180 / math.pi
          return Affine(
              ratio=-degrees * loop.clamp_scale / reach,
              offset=degrees * (loop.pulley_phase
                                + loop.clamp_origin * loop.clamp_scale / reach))

  which is `Loop.pulley_angle()` — `(pulley_phase - anchor(block) / reach)`
  in degrees — read as an affine. `Loop.anchor()`, `Loop.pulley_angle()` and
  `Loop.idler_angle()` all stay: `idler_angle` is still called by hand (see
  "Known gaps"), and the two laws should be written as the affine reading of
  the same coefficients, not as a second derivation of them.

### The `simulate()` that shrinks

`Kossel.simulate()` loses the effector's `translate` (now three relations)
and the rods' four-call `rotate/rotate/rotate/translate` chain (now four
joint bindings and one station translate). It keeps, unchanged: the seven
`connect()` calls that feed the Bowden tube and the filament, the three
`delta_carriage` bindings of `tower.height`, and the `delta_rod`/`spin`
arithmetic per tower. The rod block becomes

    for side, rod in zip((-1, 1), self.rods[2 * index:2 * index + 2]):
        rod.spin = spin
        rod.lean = tilt
        rod.swing = azimuth
        rod.rise = height
        rod.translate([self.joint_radius * ux + side * BALL_STATION * vx,
                       self.joint_radius * uy + side * BALL_STATION * vy,
                       0])

and the binding order is load-bearing: joint motion and hand motion are
inserted at the end of the node's motion block in call order, innermost
first, so `spin, lean, swing, rise, station` reproduce today's
`T(station) · Rz(azimuth) · Ry(-tilt) · Rz(spin)` exactly. The order must
be commented where it is written, because nothing in the class says it.

`Tower.simulate()` loses the carriage's `translate`, the `connect()` into
`belt.clamp` and the pulley's `rotate`. It keeps the unbound-height default
(the one place an unbound port is not a fault — a tower is a declared model
of its own and `test_tower.py` asks for the machine's default pose) and the
two idlers' `rotate`:

    def simulate(self):
        if self.height.value is None:
            self.connect(layout.DEFAULT_CARRIAGE_HEIGHT, self.height)
        block = self.height.value - CARRIAGE_HORN_Y
        loop = self.belt.loop
        for bearing in self.idlers:
            bearing.rotate(loop.idler_angle(block), [0, 0, 1])

The default must be bound before the relations solve, which is what the
end-of-simulate solve gives; `block` is recomputed here from `height`
rather than read off the derived coordinate, because a class's own derived
coordinate is unbound inside its own `simulate()`.

### Hand-written frame inversions that leave

None: there are none to remove. Every rotation this project writes today is
already stated in the moving node's own frame, so the arithmetic the joints
spec exists to delete was never written here. The gain of this change is
that the freedoms become declarations on the bodies that have them, and
that three transmissions become sentences; it is not a reduction in frame
arithmetic. Saying so plainly is part of the proposal.

## What does not change

- The drivers `x`, `y`, `z`, their units, defaults and ranges, and `Z_MAX`.
- The six instructions (`Home`, `Center`, `Bed`, `TowerX/Y/Z`).
- Every `render()`: no part is re-placed, re-drawn or re-parameterized, and
  no build identity changes (a joint argument never enters one).
- The delta kinematics: `delta_carriage` and `delta_rod` from
  `solid_node.mechanisms`, the `asin(sin(azimuth - angle) * cos(tilt))`
  spin, and `layout.joint_plane`.
- Every port that exists today stays, because not one of them forwards:
  `Tower.height` is the tower's input from the machine's kinematics and now
  has three named consumers; `Belt.clamp` and the seven `BowdenTube`/
  `Filament` ports feed molejo geometry and are the flexible-part chain
  `driver → port → geometry`.
- Every test file, contract and assertion (see "Tests").
- The pose of every leaf at every driver value.

## Known gaps

Four things stay hand-written, each against a limit already recorded in
`solid-node/workflow/warts.md`. None of them is the machine's principal
motion, and each is a place a later primitive would ADD a declaration
rather than redo this refactor.

1. **The two idler bearings cannot carry a joint** (own-placed-origin
   anchor; fan-out over `.repeat()`). Both bearings turn about the same
   line — the idler bolt, `(0, IDLER_STATION, top_centre)` along the
   tower's Y — so one declared anchor would serve both copies, but
   `top_centre = vertical_extrusion - TOP_VERTEX_HEIGHT / 2` is the
   TOWER's knowledge and `Bearing` is a shared fastener class the extruder
   also uses. There is no way to hand a repeated child a joint at the
   declaration site, and a relation cannot fan out over `.repeat()`.
   Wanted:

       idlers = Bearing(...).repeat(2, spin=Revolute(axis=(0, 1, 0), at=OWN_PLACED_ORIGIN))
       block.drives(idlers.spin, law=idler_turn)

   Today: two `rotate()` calls in `Tower.simulate()`, in the bearings' own
   frame, and `Loop.idler_angle` stays.

2. **The rod station stays a hand-written translate.** A rod's ball hangs
   at a constant `(x, y)` per copy, which belongs in `Kossel.render()` as a
   rest placement — but then each of the rod's four joints would need
   `at` at that copy's own placed origin, which is per-copy metadata a
   `.repeat(6)` cannot carry. Leaving the rods unplaced keeps every anchor
   at the default origin and puts the station in `simulate()` instead, as
   today. Wanted: the own-placed-origin anchor mode, plus per-copy joint
   arguments.

3. **The rods' four joints compose in binding order.** Correct here, and
   deliberately so — they are bound as four adjacent lines in one loop, so
   the order is visible to a reader — but nothing in `Rod` states that
   `spin` is innermost and `rise` outermost, and a future relation binding
   any of them would silently reorder the composition. Fifth sighting of
   the OpenCycloid/hexapod/dog finding. Wanted: joints of one class
   compose in DECLARATION order, innermost first, whatever order they are
   bound in. This is why the binding order gets a comment.

4. **A relation reads one coordinate; the delta reads three.** A carriage's
   height is `plane + sqrt(rod² - dx² - dy²)` over `x`, `y` and `z`, and a
   rod's lean, swing and spin are the same three sources per copy — over
   `.repeat()` children with a per-copy tower angle and side. Second
   sighting of the Pascaline finding, doubled by the fan-out finding.
   Wanted:

       (x, y, z).drives(towers.height, law=delta_carriage_law)   # law reads the copy's tower angle

   Today: three `connect()` calls and six four-line bindings in
   `Kossel.simulate()`, which is what the framework's own
   `solid_node.mechanisms.delta_carriage`/`delta_rod` are for.

New limit found by this project, worth recording alongside them: a joint's
anchor is frequently the node's own placed origin computed from a value
only the PARENT has (the idlers' `top_centre`), and where the parent's
value can be reached the anchor still has to be re-derived by a callable
(`GT2Pulley._on_the_motor_shaft` recomputes `IDLER_STATION +
teeth_start + PULLEY_WIDTH / 2`, which `Tower.render()` has just
computed). This is the sixth sighting of the declaration-site finding and
the second of the "the number is the parent's knowledge" variant.

**Recommendation: proceed, do not defer.** The machine's principal motion —
the effector's three coordinates, the three carriage slides, the three
pulleys and all six rods, thirty-three freedoms — is fully statable with
the API as it stands. The four gaps above cost two `rotate()` calls, one
`translate()` and the bindings of a prescribed kinematic law, all of which
a later primitive extends rather than rewrites.

## Pre-existing state

The repository is clean: `git status --porcelain` prints nothing, on branch
`master` at `b7f4317`. Stage 0 therefore has nothing to commit and is a
no-op; the proposal is committed with the stage A import fix.

## Tests

Three test files, none of which imports a moved name, all of which drive
the model through `set_state` and measure geometry. The declared model is
`simulation.kossel:Kossel` (`pyproject.toml`); `test_tower.py` and
`test_effector.py` are companions of sub-assemblies built on their own.

`simulation/test_kossel.py` (`KosselTest`, `KosselScenarioTest`) — the
frame closes and its screws reach their nuts (static); the nozzle position
drives the carriages (`joint_height` off the balls' centroids against the
test's own delta arithmetic, six poses); rods of the declared length reach
both joints (the ball-to-ball span is the diagonal rod, six poses, twelve
rods); home stops short of the switch; the glass rests on three pads; the
extruder is held and pinches the filament; the tube reaches the head
everywhere and the filament stays inside it; the brick is held; whole-model
disconnection and interference; and a scenario running all six
instructions with interference every 0.75 s.

`simulation/test_tower.py` (`TowerTest`) — the carriage screws meet the
block pattern; the block rides the rail; **the carriage horn axis stands
where Marlin says**, asserting the ball centres' mean Z equals
`layout.DEFAULT_CARRIAGE_HEIGHT` on a tower built alone; the endstop hangs
its switch over the rail; the belt rides its pulley and idlers; the pulley
meshes the belt without biting; the pulley and idlers sit on their shafts;
disconnection and interference.

`simulation/test_effector.py` (`EffectorAssemblyTest`) — the collar seats,
the plate is in the groove, `z` is the nozzle, the clamp screws reach the
shroud, the push-fit sits in the thread, the balls are captured, plus
disconnection and interference. Nothing here moves; the effector is built
at rest.

I expect **no test to need a change**. Three to watch, flagged for the
orchestrator, not decided here:

- `TowerTest.test_the_carriage_horn_axis_stands_where_marlin_says` — the
  only test that depends on the standalone unbound-height default, which
  now has to be bound before the tower's relations solve rather than read
  as a local variable. If the default binding is written wrongly this test
  is the one that goes red, and it should stay green as written.
- `TowerTest.test_the_pulley_meshes_the_belt_without_biting` and
  `test_the_belt_rides_its_pulley_and_idlers` — the pulley angle and the
  belt clamp are now the same arithmetic re-associated as
  `ratio * block + offset` instead of `(block - origin) * scale`. The pose
  is the same to the last representable digit but perhaps not to the last
  bit; a pose deviation of order 1e-13 mm or degrees on the pulley and the
  belt, and nowhere else, would be that re-association and not a change of
  pose. Both tests carry millimetre-scale tolerances and should not notice.
- `test_effector.py`'s and `test_tower.py`'s perturbation assertions
  (`assertFreeWithin`/`assertBlockedBeyond`) read their directions in the
  perturbed node's own frame. The perturbed nodes (balls, pulley, block,
  carriage) keep the frames they have; only their PARENTS' motion changes
  form. The pulley is the one perturbed node that gains a joint, and its
  joint resolves to the same single local-Z rotation it applies today, so
  the comment in that test stays true.

## Deferred (2026-09-09)

The orchestrator deferred stage B of this change: the six rods each need
four joints on one body (`spin`, `lean`, `swing`, `rise`), and the
framework does not yet state the composition order of several joints
declared on one body. This is the fifth sighting of that gap, recorded in
`solid-node/workflow/warts.md` as "joints of one class compose in
DECLARATION order, innermost first, whatever order they are bound in."
Stage B waits for that primitive. Stage A — the import fix, the baseline,
and the captured poses — is committed so the project runs meanwhile.
