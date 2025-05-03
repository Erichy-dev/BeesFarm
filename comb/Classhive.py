import numpy as np
import matplotlib.pyplot as plt

# Function to draw a hexagon
def hexagon(x_center, y_center, size):
    """Draw a hexagon given a center (x, y) and size."""
    angle = np.linspace(0, 2 * np.pi, 7)  # Hexagon has 6 sides
    x_hexagon = x_center + size * np.cos(angle)
    y_hexagon = y_center + size * np.sin(angle)
    return x_hexagon, y_hexagon

# Marker Class for Circle
class CircleMarker:
    def __init__(self, x, y, radius=0.2, color='red'):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.circle = None  # Store the circle object

    def plot(self, ax):
        """Plots the circle marker on the given axis."""
        self.circle = plt.Circle((self.x, self.y), self.radius, color=self.color)
        ax.add_artist(self.circle)
    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
        if self.circle:
            self.circle.set_center((self.x, self.y))
# Marker Class for Triangle
class TriangleMarker:
    def __init__(self, x, y, size=0.2, color='blue'):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.triangle = None  # Store the triangle object

    def plot(self, ax):
        """Plots the triangle marker on the given axis."""
        triangle = plt.Polygon(
            [
                (self.x, self.y + self.size),  # Top
                (self.x - self.size, self.y - self.size),  # Bottom left
                (self.x + self.size, self.y - self.size),  # Bottom right
            ],
            color=self.color
        )
        self.triangle = triangle
        ax.add_artist(triangle)

    def move(self, new_x, new_y):
        """Moves the triangle marker to a new position."""
        self.x = new_x
        self.y = new_y
        if self.triangle:
            self.triangle.set_xy([
                (self.x, self.y + self.size),  # Top
                (self.x - self.size, self.y - self.size),  # Bottom left
                (self.x + self.size, self.y - self.size),  # Bottom right
            ])
class RectangleMarker:
    def __init__(self, x, y, width=0.5, height=0.5, color='purple'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rectangle = None  # Store the rectangle object

    def plot(self, ax):
        """Plots the rectangle marker on the given axis."""
        rectangle = plt.Rectangle(
            (self.x - self.width / 2, self.y - self.height / 2),
            self.width,
            self.height,
            color=self.color
        )
        self.rectangle = rectangle
        ax.add_artist(rectangle)

    def move(self, new_x, new_y):
        """Moves the rectangle marker to a new position."""
        self.x = new_x
        self.y = new_y
        if self.rectangle:
            self.rectangle.set_xy((self.x - self.width / 2, self.y - self.height / 2))