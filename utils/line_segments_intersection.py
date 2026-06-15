# https://raw.org/book/computer-graphics/line-segment-intersection/
# https://persson.berkeley.edu/Programming_for_Mathematical_Applications/content/Computational_Geometry/Line_Segment_Interactions.html

def find_segment_intersection(p1, p2, q1, q2, sigma = 0):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = q1
    x4, y4 = q2

    v0 = (x1 - x3, y1 - y3)      # A1 - A2
    v1 = (x2 - x1, y2 - y1)      # B1 - A1
    v2 = (x4 - x3, y4 - y3)      # B2 - A2

    def cross(ax, ay, bx, by):
        return ax * by - ay * bx

    w = cross(v1[0], v1[1], v2[0], v2[1])

    if w != 0:
        t = cross(v0[0], v0[1], v2[0], v2[1]) / w
        s = cross(v0[0], v0[1], v1[0], v1[1]) / w

        if -sigma <= t <= 1 + sigma and -sigma <= s <= 1 + sigma:
            ix = x1 + t * v1[0]
            iy = y1 + t * v1[1]
            return (ix, iy)
    
    return None


def _qpoints_to_segments(qpoints):
    segments = []
    for i in range(len(qpoints) - 1):
        a, b = qpoints[i], qpoints[i + 1]
        segments.append(((a.x(), a.y()), (b.x(), b.y())))
    return segments


def find_growth_grid_intersections(growth_line, grid_lines): 
    growth_segments = _qpoints_to_segments(growth_line)

    result = []
    for line_idx, grid_line in enumerate(grid_lines):
        if not grid_line or len(grid_line) < 2:
            continue

        grid_segments = _qpoints_to_segments(grid_line)

        for grid_a, grid_b in grid_segments:
            for growth_a, growth_b in growth_segments:
                pt = find_segment_intersection(grid_a, grid_b, growth_a, growth_b)
                if pt is not None:
                    result.append((pt, line_idx))

    return result
