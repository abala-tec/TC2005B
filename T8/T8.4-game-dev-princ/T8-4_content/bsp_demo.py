SIDES = {
    "L1": ((0.0, -3.0), (0.0, 3.0)),
    "L2": ((-3.0, 0.0), (0.0, 0.0)),
    "L3": ((0.0, 0.0), (3.0, 0.0)),
}

TREE = ("L1", ("L2", "A", "B"), ("L3", "C", "D"))


def side(line, point):
    (x0, y0), (x1, y1) = line
    x, y = point
    return (x1 - x0) * (y - y0) - (y1 - y0) * (x - x0)


def visit(node, point, result):
    if isinstance(node, str):
        result.append(node)
        return

    name, front, back = node
    if side(SIDES[name], point) >= 0:
        visit(front, point, result)
        result.append(name)
        visit(back, point, result)
    else:
        visit(back, point, result)
        result.append(name)
        visit(front, point, result)


def main():
    cameras = {
        "B": (-1.5, -1.5),
        "A": (-1.5, 1.5),
        "C": (1.5, 1.5),
        "D": (1.5, -1.5),
    }

    for zone, point in cameras.items():
        result = []
        visit(TREE, point, result)
        print(f"cámara en {zone}: " + " -> ".join(result))


if __name__ == "__main__":
    main()
