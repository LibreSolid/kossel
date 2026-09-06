"""Turning a part drawn along +Z to point somewhere else.

Each returns the node so the call chains into a `translate`.  The axis
names are the part's +Z after the turn.
"""


def along_x(node):
    return node.rotate(90, [0, 1, 0])


def along_minus_x(node):
    return node.rotate(-90, [0, 1, 0])


def along_y(node):
    return node.rotate(-90, [1, 0, 0])


def along_minus_y(node):
    return node.rotate(90, [1, 0, 0])


def along_minus_z(node):
    return node.rotate(180, [1, 0, 0])
