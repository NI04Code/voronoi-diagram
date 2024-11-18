import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;
import java.util.List;


// StdDraw is retrieved from https://introcs.cs.princeton.edu/java/stdlib/StdDraw.java.html


public class Voronoi {
    private static List<Point> points;
    private static List<Parabola> beachline;
    private static List<Edge> edges;


    public Voronoi(List<Point> points) {
        this.points = points;
    }




    public static void main(String[] args) {
        points = new ArrayList<Point>();
        points.add(new Point(100, 400));
        points.add(new Point(400, 400));
        points.add(new Point(200, 300));

        Voronoi voronoi = new Voronoi(points);

        // Add List of beachline
        beachline = new ArrayList<Parabola>();

        // Add List of edges
        edges = new ArrayList<Edge>();

        // Sort points by y-coordinate descending
        points.sort((p1, p2) -> Double.compare(p2.y, p1.y));

        // Initialize StdDraw settings
        StdDraw.setCanvasSize(500, 500);
        StdDraw.setXscale(0, 500);
        StdDraw.setYscale(0, 500);

        // Draw points
        StdDraw.setPenColor(StdDraw.RED);
        StdDraw.setPenRadius(0.01);
        for (Point point : points) {
            StdDraw.point(point.x, point.y);
        }

        // Initial sweep line position from the top
        double directrix = 500;

        // Draw parabolas for each point
        // In fortune, the directrix is the y value of the sweep line

        // Trigger site event and edge-intersection event
 

        for (Point point : points) {
            // because site event, the directrix is the y value of the point
            final double EPSILON = 1e-6;
            directrix = point.y - 20;


            // Delete previous parabola
            // StdDraw.setPenColor(StdDraw.WHITE);
            StdDraw.clear();
            for (int i = 0; i < beachline.size(); i++) {
                Parabola p = beachline.get(i);
                // Change the directrix of the parabola
                p.directrix = directrix;
            }


            // Draw sweep line
            StdDraw.setPenColor(StdDraw.BLUE);
            StdDraw.setPenRadius(0.002);
            StdDraw.line(0, directrix, 500, directrix);


            // Add parabola to beachline
            Parabola parabola = new Parabola(point, directrix);
            beachline.add(parabola);

            // Draw parabola (include previous parabolas that be updated)
            StdDraw.setPenColor(StdDraw.BLACK);
            for (int i = 0; i < beachline.size(); i++) {
                Parabola p = beachline.get(i);
                p.draw();
            }
            

            // Check for edge-intersection event
            if (beachline.size() > 1) {
                checkEdgeIntersections();
                // Delete intersect parabola arc and make a new arc edge
            }

            // // Little pause
            // StdDraw.pause(1000);




        }

        // Checking circle event
        // checkCircleEvents();
        


    }

    private static void checkEdgeIntersections() {
        // Check for edge-intersection event
        for (int i = 0; i < beachline.size(); i++) {
            for (int j = 0; j < beachline.size(); j++) {
                // Skip if the same parabola
                if (i == j) {
                    continue;
                }

                // We must assure that p1.focus.y > p2.focus.y
                if (beachline.get(i).focus.y < beachline.get(j).focus.y) {
                    continue;
                }
                
                Parabola p1 = beachline.get(i);
                Parabola p2 = beachline.get(j);


            

                // Calculate intersection
                List <Point> intersects = calculateParabolaIntersections(p1, p2);
    
                if (intersects != null) {
                    StdDraw.setPenColor(StdDraw.GREEN);
                    StdDraw.setPenRadius(0.01);
                    for (Point intersect : intersects) {
                        StdDraw.point(intersect.x, intersect.y);
                    }
                }
            }
        }
        // Reset the beachline start and end point
        for (Parabola p : beachline) {
            p.start = new Point(0, 0);
            p.end = new Point(500, 500);
        }
        return;
    }
    private static List <Point> calculateParabolaIntersections(Parabola p1, Parabola p2) {
        // Calculate intersection of two parabolas
        double x = 0.0;
        double maxX = 500.0;
        double step = 0.5;
        List <Point> intersects = new ArrayList<Point>();
        
        while (x <= maxX) {
            double y1 = Math.pow((x - p1.focus.x), 2) / (2 * (p1.focus.y - p1.directrix)) + (p1.focus.y + p1.directrix) / 2;
            double y2 = Math.pow((x - p2.focus.x), 2) / (2 * (p2.focus.y - p2.directrix)) + (p2.focus.y + p2.directrix) / 2;
            // y1 and y2 must be in range 0 to 500
            if(y1 < 0 || y1 > 500 || y2 < 0 || y2 > 500) {
                x += step;
                continue;

            }



            if (Math.abs(y1 - y2) < 2) {
                // If the intersection is outside the range of the parabola, then skip
                if(x < p1.start.x || x > p1.end.x || x < p2.start.x || x > p2.end.x) {
                    if(x == 31.5) {
                        System.out.println(p1.start.x + " " + p1.end.x + " " + p2.start.x + " " + p2.end.x);
                    }
                    x += step;
                    continue;
                }


                System.out.println("Intersection found at " + x + ", " + y1);
                intersects.add(new Point(x, y1));
                x += step;
            }
            x += step;
        }
        if(intersects == null) {
            return null;
        }
        for (Point intersect : intersects) {
             // Delete the arc parabola after intersection
        x = 0.0;
        boolean isStartingPoint = true;
        while (x <= maxX) {
            if (x > intersect.x) {
                isStartingPoint = false;
            }
            double y1 = Math.pow((x - p1.focus.x), 2) / (2 * (p1.focus.y - p1.directrix)) + (p1.focus.y + p1.directrix) / 2;
            double y2 = Math.pow((x - p2.focus.x), 2) / (2 * (p2.focus.y - p2.directrix)) + (p2.focus.y + p2.directrix) / 2;
            // y1 and y2 must be in range 0 to 500
            if(y1 < 0 || y1 > 500 || y2 < 0 || y2 > 500) {
                x += step;
                continue;

            }


            if(intersect.y < y1 && y1 > y2) {
                // delete the arc that satisfy the condition
                StdDraw.setPenColor(StdDraw.WHITE);
                StdDraw.setPenRadius(0.01);
                StdDraw.setPenRadius(0.001);
                StdDraw.point(x, y1);
                x += step;
                if(isStartingPoint) {
                    p1.start = new Point(x, y1);
                    // p1.end = new Point(intersect.x, intersect.y);
                }
                else {
                    // p1.start = new Point(intersect.x, intersect.y);
                    p1.end = new Point(x, y1);
                }


                


            }
            else if(intersect.y < y2 && y2 > y1) {
                // delete the arc that satisfy the condition
                StdDraw.setPenColor(StdDraw.WHITE);
                StdDraw.setPenRadius(0.01);
                StdDraw.setPenRadius(0.001);
                StdDraw.point(x, y2);
                x += step;
                if(isStartingPoint) {
                    p2.start = new Point(x, y2);
                    // p2.end = new Point(intersect.x, intersect.y);
                }
                else {
                    // p2.start = new Point(intersect.x, intersect.y);
                    p2.end = new Point(x, y2);
                }
      

            }
            else {
                isStartingPoint = false;
                x += step;
                continue;
            }
        }

        // Draw the edge using bisector
        x = 0.0;

        // Calculate bisector between two foci
        double dx = p2.focus.x - p1.focus.x;
        double dy = p2.focus.y - p1.focus.y;
        // if(dy == 0) {
        //     dy = 1e-6;

        // }
        double m = -dx / dy;

        isStartingPoint = true;
        Edge edge = null;


        while(x <= maxX && dy != 0) {
            double y = intersect.y + m * (x - intersect.x);
            if(y < 0 || y > 500) {
                x += step;
                continue;
            }
            else if (y < intersect.y) {
                x += step;
                continue;
            }
            // We must assure that the edge is not created below any parabola
            else if (y < Math.pow((x - p1.focus.x), 2) / (2 * (p1.focus.y - p1.directrix)) + (p1.focus.y + p1.directrix) / 2) {
                x += step;
                continue;
            }
            else if (y < Math.pow((x - p2.focus.x), 2) / (2 * (p2.focus.y - p2.directrix)) + (p2.focus.y + p2.directrix) / 2) {
                x += step;
                continue;
            }



            if(isStartingPoint) {
                Point start = new Point(x, y);
                isStartingPoint = false;
                edge = new Edge(start, null);
            }
            edge.end = new Point(x, y);
            StdDraw.setPenColor(StdDraw.BLACK);
            StdDraw.setPenRadius(0.01);
            StdDraw.setPenRadius(0.001);
            StdDraw.point(x, y);
            x += step;

        }
        if(dy == 0) {
            // If the foci are in the same y-coordinate, then the edge is vertical
            x = intersect.x;
            edge = new Edge(new Point(x, intersect.y), new Point(x, 500));

        }


        if(edge != null) {
            

            edges.add(edge);
        }



        }
       


        return intersects;
    }

// Method to check if the point is above any existing edge
private static boolean isAboveExistingEdges(double x, double y) {
    for (Edge edge : edges) {
        double x1 = edge.start.x;
        double y1 = edge.start.y;
        double x2 = edge.end.x;
        double y2 = edge.end.y;


        // Calculate the cross product
        double cross = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1);

        // If cross product is positive, then the point is above the edge
        if (cross > 0) {
            return true;
        }

    }
    return false;
}


    
    
}



class Point {
    public double x;
    public double y;

    public Point(double x, double y) {
        this.x = x;
        this.y = y;
    }

    public String toString() {
        return "(" + x + ", " + y + ")";
    }
}

class Edge {
    public Point start;
    public Point end;

    public Edge(Point start, Point end) {
        this.start = start;
        this.end = end;
    }

    public void draw() {
        StdDraw.setPenColor(StdDraw.BLACK);
        StdDraw.setPenRadius(0.002);
        StdDraw.line(start.x, start.y, end.x, end.y);
    }
}


class Parabola {
    public Point focus;
    public double directrix;
    // If the parabola intersects the edge, we need to know the start and end point
    public Point start;
    public Point end;

    public Parabola(Point focus, double directrix) {
        this.focus = focus;
        // In fortune, directrix is the y value of the sweep line
        this.directrix = directrix;
        this.start = new Point(0, 0);
        this.end = new Point(500, 500);
    }


    public void draw() {
        StdDraw.setPenColor(StdDraw.BLACK);
        StdDraw.setPenRadius(0.01);
        StdDraw.point(focus.x, focus.y);
        StdDraw.setPenRadius(0.001);

        double x = 0.0;
        double maxX = 500.0;
        double step = 0.5;
        while (x <= maxX) {
            double y = Math.pow((x - focus.x), 2) / (2 * (focus.y - directrix)) + (focus.y + directrix) / 2;
            if (y < 0 || y > 500) {
                double xbefore = x - step;
                double ybefore = Math.pow((xbefore - focus.x), 2) / (2 * (focus.y - directrix)) + (focus.y + directrix) / 2;
                if (ybefore >= 0 && ybefore <= 500) {
                    break;
                }
                x += step; 
                continue;
            }
            StdDraw.point(x, y);
            x += step;
        }
    }
    public void delete() {
        StdDraw.setPenColor(StdDraw.WHITE);
        StdDraw.setPenRadius(0.01);
        StdDraw.setPenRadius(0.001);

        double x = 0.0;
        double maxX = 500.0;
        double step = 0.5;
        while (x <= maxX) {
            double y = Math.pow((x - focus.x), 2) / (2 * (focus.y - directrix)) + (focus.y + directrix) / 2;
            if (y < 0 || y > 500) {
                double xbefore = x - step;
                double ybefore = Math.pow((xbefore - focus.x), 2) / (2 * (focus.y - directrix)) + (focus.y + directrix) / 2;
                if (ybefore >= 0 && ybefore <= 500) {
                    break;
                }
                x += step; 
                continue;
            }
            StdDraw.setPenColor(StdDraw.WHITE);
            StdDraw.point(x, y);
            x += step;
        }
    }
}