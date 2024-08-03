import numpy as np
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
from PySide6.QtCore import QPoint

def line_intersection(line1_coords, line2_coords):
    line1 = LineString(line1_coords)
    line2 = LineString(line2_coords)
    intersection = line1.intersection(line2)
    return QPoint(intersection.x, intersection.y) if not intersection.is_empty else None

def find_nearest_point_to_line(line, points):
    line = LineString(line)
    nearest_point = None
    min_distance = float('inf')
    
    for point in points:
        point = Point(point)
        point_on_line = nearest_points(line, point)[0]
        distance = point.distance(point_on_line)
        
        if distance < min_distance:
            min_distance = distance
            nearest_point = point
    
    return (nearest_point.x, nearest_point.y) if nearest_point else None

def check_intersections(lines, points):
    if isinstance(lines, np.ndarray):
        lines = lines.tolist()

    nearest_points_to_lines = []

    for idx_line, line in enumerate(lines):
        nearest_pt = find_nearest_point_to_line(line, points)
        if nearest_pt:
            nearest_points_to_lines.append((nearest_pt, idx_line))

    return nearest_points_to_lines

def generate_points(interpolated_line, lines):
    intersections = []
    for line_idx, line in enumerate(lines): # проходим по каждой линии сетки
        p1, p2 = line[0], line[1]
        for j in range(len(interpolated_line) - 1):  # проходим по каждой линии роста
            q1, q2 = interpolated_line[j], interpolated_line[j + 1]
            det = (p2[0] - p1[0]) * (q2[1] - q1[1]) - (p2[1] - p1[1]) * (q2[0] - q1[0]) # определитель a1b2-a2b1
            if abs(det) > 0:  # 0 если линии параллельны, чтобы не было деления на 0
                t = ((q1[0] - p1[0]) * (q2[1] - q1[1]) - (q1[1] - p1[1]) * (q2[0] - q1[0])) / det #c1b2-c2b1/det
                u = ((p1[0] - q1[0]) * (p2[1] - p1[1]) - (p1[1] - q1[1]) * (p2[0] - p1[0])) / det #a1c2-a2c1/det
                if 0 <= t <= 1 and 0 <= u <= 1.5:
                    intersection_x = p1[0] + t * (p2[0] - p1[0])
                    intersection_y = p1[1] + t * (p2[1] - p1[1])
                    intersections.append(((intersection_x, intersection_y), line_idx))
    return intersections


















