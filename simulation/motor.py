"""The tower motor and the pulley on its shaft."""

import math

from solid2 import polygon
from solid_node.parameters import Count, Length

from simulation import gt2, hardware, materials, scad
from simulation.part import ScadPart, curve


class Nema17(ScadPart):
    """nema17.scad: body below the XY plane, face on it, shaft up +Z."""

    color = materials.MOTOR

    def render(self):
        return scad.nema17.nema17()


class GT2Pulley(ScadPart):
    """The toothed pulley a GT2 belt is driven from.

    The toothed body is Metamaquina 2's: not a cylinder with notches and
    not the tooth's own shape, but `gt2.groove`, the deepest a tooth
    reaches anywhere on its way in and out of the pulley, cut `CLEARANCE`
    inside the belt all round -- see that project's `gt2.py` for what
    found each of those.  Drawn with a groove centred on +X, which is the
    phase an assembly turns it from.

    Here it also has what the bought part has: a hub toward the motor
    and a flange either side of the teeth.  Drawn along +Z from the hub
    end, so that turned onto a shaft pointing at the tower the hub is
    against the motor and the teeth are out at the belt.
    """

    color = materials.ALUMINIUM

    CLEARANCE = 0.1
    SAMPLES = 16

    period = Length(gt2.PITCH, min=0)
    teeth = Count(hardware.PULLEY_TEETH, min=1)
    bore = Length(hardware.MOTOR_SHAFT, min=0)

    @property
    def radius(self):
        """The flank circle the grooves are measured inward from."""
        return gt2.pulley_radius(self.teeth, self.period)

    @property
    def length(self):
        return (hardware.PULLEY_HUB + 2 * hardware.PULLEY_FLANGE
                + hardware.PULLEY_WIDTH)

    @property
    def teeth_start(self):
        """Where along +Z the toothed body begins."""
        return hardware.PULLEY_HUB + hardware.PULLEY_FLANGE

    def outline(self):
        depths = gt2.groove(self.teeth, self.period, 4 * self.SAMPLES)
        points = []
        for tooth in range(self.teeth):
            for step, depth in enumerate(depths):
                angle = 2 * math.pi * (tooth + step / len(depths)) / self.teeth
                radius = self.radius - depth - self.CLEARANCE
                points.append([radius * math.cos(angle), radius * math.sin(angle)])
        return points

    def render(self):
        hub = curve('cylinder', r=hardware.PULLEY_HUB_RADIUS, h=hardware.PULLEY_HUB)
        flange = curve('cylinder', r=hardware.PULLEY_FLANGE_RADIUS,
                       h=hardware.PULLEY_FLANGE)
        body = (hub
                + flange.translate([0, 0, hardware.PULLEY_HUB])
                + polygon(self.outline()).linear_extrude(hardware.PULLEY_WIDTH)
                .translate([0, 0, self.teeth_start])
                + flange.translate([0, 0, self.teeth_start + hardware.PULLEY_WIDTH]))
        return body - curve('cylinder', r=self.bore / 2 + self.CLEARANCE,
                            h=3 * self.length, center=True)
