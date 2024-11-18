import matplotlib.pyplot as plt

class VoronoiDiagram:
    """
    Creates an instance of the Voronoi diagram builder
    :param points: List of Point objects with coordinates p.x and p.y
    :param width: Width of the canvas
    :param height: Height of the canvas
    """
    def __init__(self, points, width, height):
        self.point_list = points
        self.reset()
        self.box_x = width
        self.box_y = height
        self.maxCircle = {
            'x': [],
            'y': [],
            'radius': 0
        }

    def reset(self):
        self.event_list = SortedQueue()
        self.beachline_root = None
        self.voronoi_vertex = []
        self.edges = []
        self.maxCircle = {
            'x': [],
            'y': [],
            'radius': 0
        }

    def update(self):
        """
        Builds the Voronoi diagram by computing the Voronoi vertices and edges
        """
        self.reset()
        points = []
        e = None
        for p in self.point_list:
            points.append(Event("point", p))
        self.event_list.points = points

        while len(self.event_list) > 0:
            e = self.event_list.extract_first()
            if e.type == "point":
                self.point_event(e.position)
            elif e.active:
                self.circle_event(e)
        self.complete_segments(e.position)

    def point_event(self, p):
        """
        Handles the Point Events
        :param p: Point object with coordinates p.x and p.y
        """
        q = self.beachline_root
        if q is None:
            self.beachline_root = Arc(None, None, p, None, None)
        else:
            while q.right is not None and self.parabola_intersection(p.y, q.focus, q.right.focus) <= p.x:
                q = q.right

            e_qp = Edge(q.focus, p, p.x)
            e_pq = Edge(p, q.focus, p.x)

            arc_p = Arc(q, None, p, e_qp, e_pq)
            arc_qr = Arc(arc_p, q.right, q.focus, e_pq, q.edge['right'])
            if q.right:
                q.right.left = arc_qr
            arc_p.right = arc_qr
            q.right = arc_p
            q.edge['right'] = e_qp

            if q.event:
                q.event.active = False

            self.add_circle_event(p, q)
            self.add_circle_event(p, arc_qr)

            self.edges.append(e_qp)
            self.edges.append(e_pq)

    def circle_event(self, e):
        """
        Handles the circle event
        :param e: Event object
        """
        arc = e.caller
        p = e.position
        edge_new = Edge(arc.left.focus, arc.right.focus)

        if arc.left.event:
            arc.left.event.active = False
        if arc.right.event:
            arc.right.event.active = False

        arc.left.edge['right'] = edge_new
        arc.right.edge['left'] = edge_new
        arc.left.right = arc.right
        arc.right.left = arc.left

        self.edges.append(edge_new)

        if not self.point_outside(e.vertex):
            self.voronoi_vertex.append(e.vertex)
        arc.edge['left'].end = arc.edge['right'].end = edge_new.start = e.vertex

        self.add_circle_event(p, arc.left)
        self.add_circle_event(p, arc.right)

        circle_radius = float('inf')

        if arc.left.left and arc.left.right:
            focus = arc.left.focus
            circle_radius_left = ((e.vertex.x - focus.x) ** 2 + (e.vertex.y - focus.y) ** 2) ** 0.5
            circle_radius = min(circle_radius, circle_radius_left)

        if arc.right.left and arc.right.right:
            focus = arc.right.focus
            circle_radius_right = ((e.vertex.x - focus.x) ** 2 + (e.vertex.y - focus.y) ** 2) ** 0.5
            circle_radius = min(circle_radius, circle_radius_right)

        if self.maxCircle['radius'] == circle_radius:
            self.maxCircle['x'].append(e.vertex.x)
            self.maxCircle['y'].append(e.vertex.y)
        elif self.maxCircle['radius'] < circle_radius:
            self.maxCircle['x'] = [e.vertex.x]
            self.maxCircle['y'] = [e.vertex.y]
            self.maxCircle['radius'] = circle_radius

    def add_circle_event(self, p, arc):
        """
        Tests if the arc event is valid and adds it into the queue
        :param p: Current position of the sweepline
        :param arc: The Arc tested
        """
        if arc.left and arc.right:
            a = arc.left.focus
            b = arc.focus
            c = arc.right.focus

            if (b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y) > 0:
                new_inters = self.edge_intersection(arc.edge['left'], arc.edge['right'])
                if new_inters:
                    circle_radius = ((new_inters.x - arc.focus.x) ** 2 + (new_inters.y - arc.focus.y) ** 2) ** 0.5
                    event_pos = circle_radius + new_inters.y
                    if event_pos > p.y and new_inters.y < self.box_y:
                        e = Event("circle", Point(new_inters.x, event_pos), arc, new_inters)
                        arc.event = e
                        self.event_list.insert(e)

    def parabola_intersection(self, y, f1, f2):
        """
        Computes the intersection of two parabolas given the directrix
        :param y: Position of the directrix (sweepline)
        :param f1: Focus of first parabola
        :param f2: Focus of second parabola
        :return: Intersection x-coordinate
        """
        fy_diff = f1.y - f2.y
        if fy_diff == 0:
            return (f1.x + f2.x) / 2
        fx_diff = f1.x - f2.x
        b1md = f1.y - y
        b2md = f2.y - y
        h1 = (-f1.x * b2md + f2.x * b1md) / fy_diff
        h2 = ((b1md * b2md * (fx_diff ** 2 + fy_diff ** 2)) ** 0.5) / fy_diff
        return h1 + h2

    def edge_intersection(self, e1, e2):
        """
        Computes the intersection point of two edges
        :param e1: First edge
        :param e2: Second edge
        :return: Intersection Point
        """
        if e1.m == float('inf'):
            return Point(e1.start.x, e2.getY(e1.start.x))
        elif e2.m == float('inf'):
            return Point(e2.start.x, e1.getY(e2.start.x))
        else:
            mdif = e1.m - e2.m
            if mdif == 0:
                return None
            x = (e2.q - e1.q) / mdif
            y = e1.getY(x)
            return Point(x, y)

    def complete_segments(self, last):
        """
        Completes the Voronoi edges considering the canvas boundaries
        :param last: Last point extracted from the queue
        """
        r = self.beachline_root
        e = None
        x = y = 0
        while r.right:
            e = r.edge['right']
            x = self.parabola_intersection(last.y * 1.1, e.arc['left'], e.arc['right'])
            y = e.getY(x)

            if (e.start.y < 0 and y < e.start.y) or (e.start.x < 0 and x < e.start.x) or (e.start.x > self.box_x and x > e.start.x):
                e.end = e.start
            else:
                if e.m == 0:
                    x = 0 if x - e.start.x <= 0 else self.box_x
                    e.end = Point(x, e.start.y)
                    self.voronoi_vertex.append(e.end)
                else:
                    y = self.box_y if e.m * (x - e.start.x) > 0 else 0
                    e.end = self.edge_end(e, y)
            r = r.right

        for i, e in enumerate(self.edges):
            option = 1 * self.point_outside(e.start) + 2 * self.point_outside(e.end)

            if option == 3:
                self.edges[i] = None
            elif option == 1:
                y = 0 if e.start.y < e.end.y else self.box_y
                e.start = self.edge_end(e, y)
            elif option == 2:
                y = 0 if e.end.y <= e.start.y else self.box_y
                e.end = self.edge_end(e, y)

        self.edges = [edge for edge in self.edges if edge is not None]

    def edge_end(self, e, y_lim):
        """
        Computes the intersection point between an edge and the canvas boundary
        :param e: Edge being completed
        :param y_lim: Canvas boundary (0 or max height)
        :return: Point of intersection
        """
        x = min(self.box_x, max(0, e.getX(y_lim)))
        y = e.getY(x)
        if y is None:
            y = y_lim
        p = Point(x, y)
        self.voronoi_vertex.append(p)
        return p

    def point_outside(self, p):
        """
        Checks if a point is outside the canvas boundaries
        :param p: Point to check
        :return: True if outside, False otherwise
        """
        return p.x < 0 or p.x > self.box_x or p.y < 0 or p.y > self.box_y


class Arc:
    def __init__(self, left, right, focus, edge_left, edge_right):
        self.left = left
        self.right = right
        self.focus = focus
        self.edge = {'left': edge_left, 'right': edge_right}
        self.event = None


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Edge:
    def __init__(self, p1, p2, startx=None):
        denominator = p1.y - p2.y
        if denominator == 0:
            self.m = float('inf')
            self.q = None
        else:
            self.m = -(p1.x - p2.x) / denominator
            self.q = (0.5 * (p1.x ** 2 - p2.x ** 2 + p1.y ** 2 - p2.y ** 2)) / denominator
        self.arc = {'left': p1, 'right': p2}
        self.end = None
        self.start = None
        if startx is not None:
            self.start = Point(startx, self.getY(startx) if self.m != float('inf') else None)

    def getY(self, x):
        if self.m == float('inf'):
            return None
        return x * self.m + self.q

    def getX(self, y):
        if self.m == float('inf'):
            return self.start.x
        return (y - self.q) / self.m


class Event:
    def __init__(self, type, position, caller=None, vertex=None):
        self.type = type
        self.caller = caller
        self.position = position
        self.vertex = vertex
        self.active = True


class SortedQueue:
    def __init__(self, events=None):
        self.list = events if events else []
        self.sort()

    def __len__(self):
        return len(self.list)

    def extract_first(self):
        if self.list:
            return self.list.pop(0)
        return None

    def insert(self, event):
        self.list.append(event)
        self.sort()

    @property
    def points(self):
        return self.list

    @points.setter
    def points(self, events):
        self.list = events
        self.sort()

    def sort(self):
        self.list.sort(key=lambda a: (a.position.y, a.position.x))


def main():
    # Set canvas size
    width = 100
    height = 100

    # Create a list of Point objects
    point_list = [
        Point(20, 30),
        Point(50, 50),
        Point(80, 70),
        Point(30, 80),
        Point(70, 20)
    ]

    # Initialize Voronoi diagram
    voronoi = VoronoiDiagram(point_list, width, height)
    voronoi.update()

    # Plot the edges
    for edge in voronoi.edges:
        if edge and edge.start and edge.end:
            x_values = [edge.start.x, edge.end.x]
            y_values = [edge.start.y, edge.end.y]
            plt.plot(x_values, y_values, 'k-')

    # Plot the points
    x_coords = [point.x for point in point_list]
    y_coords = [point.y for point in point_list]
    plt.scatter(x_coords, y_coords, color='red')

    # Plot the largest empty circle
    if voronoi.maxCircle['x']:
        x = voronoi.maxCircle['x'][0]
        y = voronoi.maxCircle['y'][0]
        radius = voronoi.maxCircle['radius']
        circle = plt.Circle((x, y), radius, color='blue', fill=False, linestyle='--')
        plt.gca().add_patch(circle)

    # Set plot limits
    plt.xlim(0, width)
    plt.ylim(0, height)
    plt.gca().set_aspect('equal', adjustable='box')

    # Show the plot
    plt.show()

if __name__ == '__main__':
    main()