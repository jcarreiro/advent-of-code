from collections import defaultdict

class Body:
    def __init__(self):
        self.label = None
        self.parent = None
        self.children = set()

    def __repr__(self):
        return f"Body({self.label}, {self.parent.label if self.parent else None}, {[c.label for c in self.children]})"

    def set_parent(self, parent):
        assert(self.parent is None or self.parent == parent)
        self.parent = parent

    def add_child(self, child):
        self.children.add(child)
        child.set_parent(self)

def build_orbit_graph(filename):
    g = defaultdict(lambda: Body())
    with open(filename) as f:
        for orbit in f:
            orbit = orbit.rstrip()
            parent_label, child_label = orbit.split(")")

            print(f"{parent_label} <- {child_label}")

            child = g[child_label]
            child.label = child_label

            parent = g[parent_label]
            parent.label = parent_label
            parent.add_child(child)
    return g

def find_shortest_path(g, src_label, dst_label):
    if not src_label in g or not dst_label in g:
        raise ValueError("Source or destination not in graph!")

    q = [(src_label, 0, [src_label])]
    visited = set()
    while q:
        label, l, path = q.pop()
        visited.add(label)

        print(f"Considering {label} at depth {l}.")

        if label == dst_label:
            print(f"Min path from {src_label} to {dst_label} has length {l}, path is {path}.")
            break

        # We're not done yet.
        def append_if_not_visted(n, l):
            if not n.label in visited:
                q.append((n.label, l, path + [n.label]))

        b = g[label]
        if b.parent:
            append_if_not_visted(b.parent, l + 1)
        for c in b.children:
            append_if_not_visted(c, l + 1)

if __name__ == '__main__':
    # Build the tree of orbits.
    g = build_orbit_graph("input")

    # Part 1
    #
    # We need to get the total number of direct and indirect orbits in the map.
    # To do this, just count all orbits recursively from COM using a BFS.
    q = [('COM', 0)]
    orbits = 0
    while q:
        body, d = q.pop()
        print(f"{body} {d}")
        orbits += d
        for x in g[body].children:
            q.append((x.label, d+1))

    print(f"Got {orbits} total orbits.")

    # Part 2
    #
    # Now we need to figure out the minimum length path between the body we are
    # currently orbiting (we are represented by the node YOU) and the body Santa
    # is currently orbiting (SAN). We can just do a BFS from YOU to SAN; since
    # we're doing a BFS, the first solution we find will have the minimum
    # length.
    #
    # For fun let's carry around the path we took so we can print the path found
    # at the end.
    q = [('YOU', 0, ['YOU'])]
    visited = set()
    while q:
        label, l, path = q.pop()
        visited.add(label)

        print(f"Considering {label} at depth {l}.")

        if label == 'SAN':
            # We're done! Note the -1 here is because we don't need to go into
            # orbit around SAN, just around the body he's orbiting.
            print(f"Min path from YOU to SAN has length {l-1}, path is {path}.")
            break

        # We're not done yet.
        def append_if_not_visted(n, l):
            if not n.label in visited:
                q.append((n.label, l, path + [n.label]))

        b = g[label]
        if b.parent:
            append_if_not_visted(b.parent, l + 1)
        for c in b.children:
            append_if_not_visted(c, l + 1)
