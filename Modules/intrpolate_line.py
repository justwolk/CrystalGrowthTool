import PySide6
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline, UnivariateSpline

from scipy.interpolate import CubicSpline
import numpy as np
from PySide6.QtCore import QPoint

#https://stackoverflow.com/questions/77997127/add-padding-to-cubespline-interpolation-curve
#https://stackoverflow.com/questions/52014197/how-to-interpolate-a-2d-curve-in-python

def cubic_spline_interpolation(points):
    points = np.array([[point.x(), point.y()] for point in points])

    distance = np.cumsum(np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1)))
    distance = np.insert(distance, 0, 0) / distance[-1]

    cs_x = CubicSpline(distance, points[:, 0])
    cs_y = CubicSpline(distance, points[:, 1])

    n = 50 + 7 * len(points)
    alpha = np.linspace(0, distance[-1], n)

    points_fitted = np.column_stack((cs_x(alpha), cs_y(alpha)))

    reconstructed_growth_lines = [QPoint(int(x), int(y)) for x, y in points_fitted]
    return reconstructed_growth_lines

def sort_points_by_distance(array):
    sorted_array = [array[0]]
    remaining_points = list(array[1:])

    while remaining_points:
        last_point = sorted_array[-1]
        distances = [euclidean_distance(last_point, point) for point in remaining_points]
        nearest_index = np.argmin(distances)
        sorted_array.append(remaining_points.pop(nearest_index))
    return np.array(sorted_array)

def euclidean_distance(point1, point2):
    return np.sqrt(np.sum((np.array(point1) - np.array(point2)) ** 2))
