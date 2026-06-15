import numpy as np
from scipy.interpolate import CubicSpline
from PySide2.QtCore import QPoint

#https://stackoverflow.com/questions/77997127/add-padding-to-cubespline-interpolation-curve
#https://stackoverflow.com/questions/52014197/how-to-interpolate-a-2d-curve-in-python
#Интерполяция кубическим сплайном.

def cubic_spline_interpolation(points):
    points = np.array([[point.x(), point.y()] for point in points])

    distance = np.cumsum(np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1)))
    distance = np.insert(distance, 0, 0) / distance[-1]

    cs_x = CubicSpline(distance, points[:, 0])
    cs_y = CubicSpline(distance, points[:, 1])

    n = 40 + 6 * len(points) # xD много линий для очень плавной интерполяции, возможно плохо
    alpha = np.linspace(0, distance[-1], n)

    points_fitted = np.column_stack((cs_x(alpha), cs_y(alpha)))

    interopated_curve = [QPoint(int(x), int(y)) for x, y in points_fitted]
    return interopated_curve