from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))


import time
import math

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#


class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)


# This is the method that gets called by the GUI and actually executes
# the finding of the hull

    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        def get_merge_hull(left, right):
            points = left + right
            # contains the final hull points
            hull = []
            current = min(points, key=lambda point: (point[0], point[1]))

            while True:
                hull.append(current)
                next_point = points[0]
                for point in points:
                    orient = orientation(current, next_point, point)
                    if next_point == current or orient == 1 or (orient == 0 and distance(current, point) > distance(current, next_point)):
                        next_point = point
                current = next_point
                if current == hull[0]:
                    break
            if pause:
                polygon = convert_points_to_qlinef_list(hull)
                self.showHull(polygon, RED)
            return hull

        def get_convex_hull(points):
            if len(points) <= 3:
                return points

            # dividing the given points into 2 halfs
            mid = len(points)//2

            left = points[:mid]
            right = points[mid:]

            # divides the points recursively
            left_hull = get_convex_hull(left)
            right_hull = get_convex_hull(right)

            # merging the halfs into a convex hull
            final_hull = get_merge_hull(left_hull, right_hull)

            if pause:
                polygon = convert_points_to_qlinef_list(final_hull)
                self.eraseHull(polygon)

            return final_hull

        def convert_points_to_qlinef_list(nodes):
            if len(nodes) < 2:
                raise ValueError(
                    "At least two points are required to create QLineF instances.")

            # converting the list of tuples(x,y) back to QPointF instances
            points = [QPointF(x, y) for x, y in nodes]

            # list to store QLineF instances
            lines = []

            for i in range(len(points) - 1):
                line = QLineF(points[i], points[i + 1])
                lines.append(line)

            # adding first point at last to close the polygon
            lines.append(QLineF(points[-1], points[0]))

            return lines

        # check whether the points are collinear, clockwise or counterclockwise order
        def orientation(point1, point2, point3):
            orient = (point2[1] - point1[1]) * (point3[0] - point2[0]) - \
                (point2[0] - point1[0]) * (point3[1] - point2[1])
            if orient == 0:
                return 0  # Collinear
            elif orient > 0:
                return 1  # Clockwise
            else:
                return -1  # counterclockwise

        # compute the distance between points
        def distance(point1, point2):
            # extracting x and y from the tuple(x,y) for easy calculation
            x1 = point1[0]
            y1 = point1[1]
            x2 = point2[0]
            y2 = point2[1]
            return math.sqrt((y2-y1)**2 + (x2-x1)**2)

        t1 = time.time()
        # sorting the points by the increasing x-value
        sorted_points = sorted(points, key=lambda point: point.x())

        # extracting the tuple(x,y) from QPointF instances
        points = [(point.x(), point.y()) for point in sorted_points]

        # TODO: SORT THE POINTS BY INCREASING X-VALUE
        t2 = time.time()

        t3 = time.time()
        # this is a dummy polygon of the first 3 unsorted points
        final_hull = get_convex_hull(points)

        polygon = convert_points_to_qlinef_list(final_hull)

        # TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
