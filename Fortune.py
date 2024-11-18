import sys
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton

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
            self.q = (0.5 * (p1.x**2 - p2.x**2 + p1.y**2 - p2.y**2)) / denominator
        self.arc = {'left': p1, 'right': p2}
        self.end = None
        self.start = None
        if startx is not None:
            y_start = self.getY(startx)
            self.start = Point(startx, y_start if y_start is not None else 0)

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

class Arc:
    def __init__(self, left, right, focus, edge_left, edge_right):
        self.left = left
        self.right = right
        self.focus = focus
        self.edge = {'left': edge_left, 'right': edge_right}
        self.event = None

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

class VoronoiDiagram:
    def __init__(self, points, width, height):
        self.point_list = points
        self.reset()
        self.box_x = width
        self.box_y = height
        self.maxCircle = {'x': [], 'y': [], 'radius': 0}

    def reset(self):
        self.event_list = SortedQueue()
        self.beachline_root = None
        self.voronoi_vertex = []
        self.edges = []
        self.maxCircle = {'x': [], 'y': [], 'radius': 0}

    def update(self):
        self.reset()
        points = [Event("point", p) for p in self.point_list]
        self.event_list.points = points
        e = None
        while len(self.event_list) > 0:
            e = self.event_list.extract_first()
            if e.type == "point":
                self.point_event(e.position)
            elif e.active:
                self.circle_event(e)
        if e:
            self.complete_segments(e.position)

    def point_event(self, p):
        q = self.beachline_root
        if q is None:
            self.beachline_root = Arc(None, None, p, None, None)
        else:
            while q.right and self.parabola_intersection(p.y, q.focus, q.right.focus) <= p.x:
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
            self.edges.extend([e_qp, e_pq])

    def circle_event(self, e):
        arc = e.caller
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
        edge_new.start = e.vertex
        arc.edge['left'].end = e.vertex
        arc.edge['right'].end = e.vertex
        self.add_circle_event(e.position, arc.left)
        self.add_circle_event(e.position, arc.right)
        circle_radius = float('inf')
        if arc.left.left and arc.left.right:
            focus = arc.left.focus
            circle_radius_left = ((e.vertex.x - focus.x)**2 + (e.vertex.y - focus.y)**2)**0.5
            circle_radius = min(circle_radius, circle_radius_left)
        if arc.right.left and arc.right.right:
            focus = arc.right.focus
            circle_radius_right = ((e.vertex.x - focus.x)**2 + (e.vertex.y - focus.y)**2)**0.5
            circle_radius = min(circle_radius, circle_radius_right)
        if self.maxCircle['radius'] == circle_radius:
            self.maxCircle['x'].append(e.vertex.x)
            self.maxCircle['y'].append(e.vertex.y)
        elif self.maxCircle['radius'] < circle_radius:
            self.maxCircle['x'] = [e.vertex.x]
            self.maxCircle['y'] = [e.vertex.y]
            self.maxCircle['radius'] = circle_radius

    def add_circle_event(self, p, arc):
        if arc.left and arc.right:
            a = arc.left.focus
            b = arc.focus
            c = arc.right.focus
            if (b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y) > 0:
                new_inters = self.edge_intersection(arc.edge['left'], arc.edge['right'])
                if new_inters:
                    circle_radius = ((new_inters.x - arc.focus.x)**2 + (new_inters.y - arc.focus.y)**2)**0.5
                    event_pos = circle_radius + new_inters.y
                    if event_pos > p.y and new_inters.y < self.box_y:
                        e = Event("circle", Point(new_inters.x, event_pos), arc, new_inters)
                        arc.event = e
                        self.event_list.insert(e)

    def parabola_intersection(self, y, f1, f2):
        fy_diff = f1.y - f2.y
        if fy_diff == 0:
            return (f1.x + f2.x) / 2
        fx_diff = f1.x - f2.x
        b1md = f1.y - y
        b2md = f2.y - y
        h1 = (-f1.x * b2md + f2.x * b1md) / fy_diff
        h2 = ((b1md * b2md * (fx_diff**2 + fy_diff**2))**0.5) / fy_diff
        return h1 + h2

    def edge_intersection(self, e1, e2):
        if e1.m == float('inf'):
            x = e1.start.x
            y = e2.getY(x)
            return Point(x, y)
        elif e2.m == float('inf'):
            x = e2.start.x
            y = e1.getY(x)
            return Point(x, y)
        else:
            mdif = e1.m - e2.m
            if mdif == 0:
                return None
            x = (e2.q - e1.q) / mdif
            y = e1.getY(x)
            return Point(x, y)

    def complete_segments(self, last):
        r = self.beachline_root
        while r.right:
            e = r.edge['right']
            x = self.parabola_intersection(last.y * 1.1, e.arc['left'], e.arc['right'])
            y = e.getY(x)
            if (e.start.y < 0 and y < e.start.y) or \
               (e.start.x < 0 and x < e.start.x) or \
               (e.start.x > self.box_x and x > e.start.x):
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

        new_edges = []
        for e in self.edges:
            if e and e.start and e.end:
                option = int(self.point_outside(e.start)) + 2 * int(self.point_outside(e.end))
                if option == 3:
                    continue
                elif option == 1:
                    y = 0 if e.start.y < e.end.y else self.box_y
                    e.start = self.edge_end(e, y)
                elif option == 2:
                    y = 0 if e.end.y <= e.start.y else self.box_y
                    e.end = self.edge_end(e, y)
                new_edges.append(e)
        self.edges = new_edges

    def edge_end(self, e, y_lim):
        x = min(self.box_x, max(0, e.getX(y_lim)))
        y = e.getY(x)
        if y is None:
            y = y_lim
        p = Point(x, y)
        self.voronoi_vertex.append(p)
        return p

    def point_outside(self, p):
        return p.x < 0 or p.x > self.box_x or p.y < 0 or p.y > self.box_y

def main():
    width = 600
    height = 800

    point_list = []

    if len(sys.argv) > 1:
        # Read points from text file
        filename = sys.argv[1]
        with open(filename, 'r') as f:
            for line in f:
                x_str, y_str = line.strip().split(',')
                x, y = float(x_str), float(y_str)
                point_list.append(Point(x, y))

        if len(point_list) < 2:
            print("Need at least two points to compute Voronoi diagram.")
            return

        voronoi = VoronoiDiagram(point_list, width, height)
        voronoi.update()

        fig, ax = plt.subplots()
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.set_aspect('equal', adjustable='box')
        plt.title('Voronoi Diagram from File Input, click to add points')

        # Plot the edges
        for edge in voronoi.edges:
            if edge and edge.start and edge.end:
                x_values = [edge.start.x, edge.end.x]
                y_values = [edge.start.y, edge.end.y]
                ax.plot(x_values, y_values, 'k-')

        # Plot the points
        x_coords = [p.x for p in point_list]
        y_coords = [p.y for p in point_list]
        ax.scatter(x_coords, y_coords, color='red')

        # Plot the largest empty circle
        if voronoi.maxCircle['x']:
            x_c = voronoi.maxCircle['x'][0]
            y_c = voronoi.maxCircle['y'][0]
            radius = voronoi.maxCircle['radius']
            circle = plt.Circle((x_c, y_c), radius, color='blue', fill=False, linestyle='--')
            ax.add_patch(circle)
            
        # Put event for point by mouse click    
        def on_click(event):
            if event.button == MouseButton.LEFT and event.inaxes:
                x, y = event.xdata, event.ydata
                point_list.append(Point(x, y))

                if len(point_list) >= 2:
                    voronoi = VoronoiDiagram(point_list, width, height)
                    voronoi.update()
                else:
                    voronoi = None

                ax.clear()
                ax.set_xlim(0, width)
                ax.set_ylim(0, height)
                ax.set_aspect('equal', adjustable='box')
                plt.title('Voronoi Diagram from File Input, click to add points')

                # Plot the edges
                if voronoi:
                    for edge in voronoi.edges:
                        if edge and edge.start and edge.end:
                            x_values = [edge.start.x, edge.end.x]
                            y_values = [edge.start.y, edge.end.y]
                            ax.plot(x_values, y_values, 'k-')

                    # Plot the largest empty circle
                    for x, y in zip(voronoi.maxCircle['x'], voronoi.maxCircle['y']):
                        circle = plt.Circle((x, y), voronoi.maxCircle['radius'], color='blue', fill=False, linestyle='--')
                        plt.gca().add_patch(circle)


                # Plot the points
                x_coords = [p.x for p in point_list]
                y_coords = [p.y for p in point_list]
                ax.scatter(x_coords, y_coords, color='red')

                plt.draw()

        fig.canvas.mpl_connect('button_press_event', on_click)
        plt.show()
        
    else:
        # No file input, accept points interactively
        point_list = []

        fig, ax = plt.subplots()
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.set_aspect('equal', adjustable='box')
        plt.title('Click to add points')

        voronoi = None

        def on_click(event):
            if event.button == MouseButton.LEFT and event.inaxes:
                x, y = event.xdata, event.ydata
                point_list.append(Point(x, y))

                if len(point_list) >= 2:
                    voronoi = VoronoiDiagram(point_list, width, height)
                    voronoi.update()
                else:
                    voronoi = None

                ax.clear()
                ax.set_xlim(0, width)
                ax.set_ylim(0, height)
                ax.set_aspect('equal', adjustable='box')
                plt.title('Click to add points')

                # Plot the edges
                if voronoi:
                    for edge in voronoi.edges:
                        if edge and edge.start and edge.end:
                            x_values = [edge.start.x, edge.end.x]
                            y_values = [edge.start.y, edge.end.y]
                            ax.plot(x_values, y_values, 'k-')

                    # Plot the largest empty circle
                    # if voronoi.maxCircle['x']:
                    #     x_c = voronoi.maxCircle['x'][0]
                    #     y_c = voronoi.maxCircle['y'][0]
                    #     radius = voronoi.maxCircle['radius']
                    #     circle = plt.Circle((x_c, y_c), radius, color='blue', fill=False, linestyle='--')
                    #     ax.add_patch(circle)
                    for x, y in zip(voronoi.maxCircle['x'], voronoi.maxCircle['y']):
                        circle = plt.Circle((x, y), voronoi.maxCircle['radius'], color='blue', fill=False, linestyle='--')
                        plt.gca().add_patch(circle)

                # Plot the points
                x_coords = [p.x for p in point_list]
                y_coords = [p.y for p in point_list]
                ax.scatter(x_coords, y_coords, color='red')

                plt.draw()
        
        #Put event for reset diagram
        def on_reset(event):
            point_list.clear()
            ax.clear()
            ax.set_xlim(0, width)
            ax.set_ylim(0, height)
            ax.set_aspect('equal', adjustable='box')
            plt.title('Click to add points')
            plt.draw()
        
        #Add reset button
        resetax = plt.axes([0.8, 0.9, 0.1, 0.04])
        reset_button = plt.Button(resetax, 'Reset', color='lightgoldenrodyellow', hovercolor='0.975')
        reset_button.on_clicked(on_reset)
        
        fig.canvas.mpl_connect('button_press_event', on_click)
        plt.show()

if __name__ == '__main__':
    main()