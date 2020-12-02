from collections import defaultdict, namedtuple

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def translate(self, tx, ty):
        return Point(self.x + tx, self.y + ty)

class Bounds(object):
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

    def save_state(self):
        return {
            "top": self.top,
            "right": self.right,
            "bottom": self.bottom,
            "left": self.left,
        }
    
    def restore_state(self, state):
        self.top = state["top"]
        self.right = state["right"]
        self.bottom = state["bottom"]
        self.left = state["left"]

# Simple grid of cells, can be used as a "hull", "screen", etc.
class Grid(object):
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