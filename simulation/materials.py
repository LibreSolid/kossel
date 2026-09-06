"""Part colours, one per material the machine is made of.

A node's colour is a property of the node, not of the geometry it renders,
so every leaf carries the colour of the stuff it is made from and nothing
else: two parts of one material look alike, and a part looks the same
whichever tower it is on.
"""

# the printed parts: Johann's kits went out in whatever PLA the printer
# had, and this machine's is a warm orange
PLA = '#f2843b'

# aluminium: the OpenBeam extrusions, the linear rails, the pulleys
ALUMINIUM = '#c8c8c8'

# steel: screws, nuts, bearings, the rail blocks, the balls of the joints
STEEL = '#8c8c8c'

# the black things: GT2 belts, carbon-fibre tubes, the rod ends' nylon
RUBBER = '#1a1a1a'
CARBON = '#2b2b2b'
NYLON = '#333333'

# the motors' painted bodies
MOTOR = '#3a3a3a'

# the hot end: PEEK holder, brass nozzle, PTFE liner and tube
PEEK = '#d9c39a'
BRASS = '#c9a23c'
PTFE = '#f5f5f5'

# the print surface
GLASS = '#9bbfd9'

# the filament the machine is loaded with
FILAMENT = '#2f8fd6'

# the power supply brick and the microswitches
PLASTIC = '#454545'
