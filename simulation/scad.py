"""Access to Johann's OpenSCAD design, which lives one directory up.

This package does not replace the .scad files; it reads them.  Every
printed part is one OpenSCAD module reached through solid2's
``import_scad``, which emits ``use <absolute path>`` so the relative
``include <configuration.scad>``, ``use <vertex.scad>`` and
``import("logotype.stl")`` inside the design keep resolving from the
source directory.  ``OpenScadNode`` is deliberately not used: it inlines
the .scad text into the generated file under ``_build``, where none of
those relative references resolve.
"""

import os

from solid2 import import_scad

SOURCE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def _handle(filename):
    return import_scad(os.path.join(SOURCE_DIR, filename))


vertex = _handle('vertex.scad')
frame_top = _handle('frame_top.scad')
frame_motor = _handle('frame_motor.scad')
frame_extruder = _handle('frame_extruder.scad')
carriage = _handle('carriage.scad')
effector = _handle('effector.scad')
endstop = _handle('endstop.scad')
extruder = _handle('extruder.scad')
glass_tab = _handle('glass_tab.scad')
hotend_fan = _handle('hotend_fan.scad')
microswitch = _handle('microswitch.scad')
nema17 = _handle('nema17.scad')
power_supply = _handle('power_supply.scad')


def scad_sources():
    """Every OpenSCAD source and mesh the design is built from.

    The whole directory rather than a per-node closure: OpenSCAD's own
    ``include``/``use``/``import`` graph is not visible to the framework's
    Python import walk, and an unnecessary rebuild is cheaper than stale
    geometry.
    """
    return {
        os.path.join(SOURCE_DIR, entry)
        for entry in os.listdir(SOURCE_DIR)
        if entry.endswith(('.scad', '.stl'))
    }
