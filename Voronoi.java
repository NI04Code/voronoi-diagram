import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;
import java.util.List;


// StdDraw is retrieved from https://introcs.cs.princeton.edu/java/stdlib/StdDraw.java.html


public class Voronoi {
    private List<Point> points;


    public Voronoi(List<Point> points) {
        this.points = points;
    }




    public static void main(String[] args) {
        List<Point> points = new ArrayList<Point>();
        points.add(new Point(100, 100));
        points.add(new Point(200, 100));
        points.add(new Point(100, 200));
        points.add(new Point(200, 200));
        points.add(new Point(150, 150));
        Voronoi voronoi = new Voronoi(points);

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

        // Draw parabolas for each point
        double directrix = 250; // Example directrix value
        for (Point point : points) {
            Parabola parabola = new Parabola(point, directrix);
            parabola.draw();
        }
        


    }
    
}



class Point {
    public int x;
    public int y;

    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
}


class Parabola {
    public Point focus;
    public double directrix;

    public Parabola(Point focus, double directrix) {
        this.focus = focus;
        this.directrix = directrix;
    }

    public void draw() {
        StdDraw.setPenColor(StdDraw.BLACK);
        StdDraw.setPenRadius(0.01);
        StdDraw.point(focus.x, focus.y);
        StdDraw.setPenRadius(0.001);
        for (int x = 0; x < 1000; x++) {
            double y = (x - focus.x) * (x - focus.x) / (2 * (focus.y - directrix)) + (focus.y + directrix) / 2;
            StdDraw.point(x, y);
        }
    }
}