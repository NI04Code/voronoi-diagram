import javax.swing.*;
import java.awt.*;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class VoronoiDiagram extends JPanel {
    private final List<Point> points = new ArrayList<>();
    private final Random random = new Random();

    public VoronoiDiagram() {
        // Mouse listener for adding points
        addMouseListener(new MouseAdapter() {
            @Override
            public void mousePressed(MouseEvent e) {
                points.add(e.getPoint());
                repaint();
            }
        });
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        if (points.isEmpty()) return;

        // Generate Voronoi diagram
        int width = getWidth();
        int height = getHeight();
        
        // Assign random colors to each cell
        Color[] colors = new Color[points.size()];
        for (int i = 0; i < points.size(); i++) {
            colors[i] = new Color(random.nextInt(256), random.nextInt(256), random.nextInt(256));
        }

        // Compute Voronoi cells by closest-point sampling
        for (int x = 0; x < width; x++) {
            for (int y = 0; y < height; y++) {
                Point closest = null;
                double minDist = Double.MAX_VALUE;
                int pointIndex = -1;

                // Find the closest point to each pixel
                for (int i = 0; i < points.size(); i++) {
                    Point p = points.get(i);
                    double dist = p.distance(x, y);
                    if (dist < minDist) {
                        minDist = dist;
                        closest = p;
                        pointIndex = i;
                    }
                }
                
                // Set pixel color based on closest point
                g.setColor(colors[pointIndex]);
                g.drawRect(x, y, 1, 1);
            }
        }

        // Draw points and boundaries
        g.setColor(Color.BLACK);
        for (Point p : points) {
            g.fillOval(p.x - 3, p.y - 3, 6, 6);
        }
    }

    public static void main(String[] args) {
        JFrame frame = new JFrame("Voronoi Diagram");
        VoronoiDiagram voronoiPanel = new VoronoiDiagram();
        
        frame.add(voronoiPanel);
        frame.setSize(800, 600);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setVisible(true);
    }
}
