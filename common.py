from collections import defaultdict, namedtuple

Point = namedtuple("Point", ["x", "y"])

class Bounds:
    def __init__(self):
        self.top = 0
        self.right = 0
        self.bottom = 0
        self.left = 0

    def extend(self, p):
        self.top = max(self.top, p.y)
        self.right = max(self.right, p.x)
        self.bottom = min(self.bottom, p.y)
        self.left = min(self.left, p.x)

# Simple grid of cells, can be used as a "hull", "screen", etc.
class Grid:
    def __init__(self, defaultColor):
        self.cells = defaultdict(dict)
        self.bounds = Bounds()
        self.defaultColor = defaultColor

    # Note that the bound are effectively infinite since we extend them on any
    # call to set. This is a way to get the area that's actually been painted.
    def get_bounds(self):
        return self.bounds

    def get_cell(self, p):
        try:
            return self.cells[p.y][p.x]
        except:
            return self.defaultColor

    def set_cell(self, p, color):
        self.cells[p.y][p.x] = color
        self.bounds.extend(p)