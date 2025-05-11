import numpy as np
import matplotlib.pyplot as plt

# Function to draw a hexagon
def hexagon(x_center, y_center, size):
    """Draw a hexagon given a center (x, y) and size."""
    angle = np.linspace(0, 2 * np.pi, 7)  # Hexagon has 6 sides
    x_hexagon = x_center + size * np.cos(angle)
    y_hexagon = y_center + size * np.sin(angle)
    return x_hexagon, y_hexagon

# Marker Class for Circle (representing bees)
class CircleMarker:
    def __init__(self, x, y, radius=0.2, color='red'):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.circle = None  # Store the circle object
        self.visible = True  # Track visibility state

    def plot(self, ax):
        """Plots the circle marker on the given axis."""
        self.circle = plt.Circle((self.x, self.y), self.radius, color=self.color)
        self.circle.set_visible(self.visible)  # Set initial visibility
        ax.add_artist(self.circle)
        
    def move(self, new_x, new_y):
        """Moves the circle marker to a new position."""
        self.x = new_x
        self.y = new_y
        if self.circle:
            self.circle.set_center((self.x, self.y))
    
    def show(self):
        """Make the circle visible."""
        if self.circle and not self.visible:
            self.circle.set_visible(True)
            self.visible = True
    
    def hide(self):
        """Make the circle invisible."""
        if self.circle and self.visible:
            self.circle.set_visible(False)
            self.visible = False
            
    def set_visibility(self, is_visible):
        """Set the visibility state of the circle."""
        if is_visible:
            self.show()
        else:
            self.hide()

# Simpler placeholder classes for other markers (not used in the simplified version)
class TriangleMarker:
    def __init__(self, x, y, size=0.2, color='blue'):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.triangle = None

    def plot(self, ax):
        pass  # Empty implementation

    def move(self, new_x, new_y):
        pass  # Empty implementation

class RectangleMarker:
    def __init__(self, x, y, width=0.5, height=0.5, color='purple'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rectangle = None

    def plot(self, ax):
        pass  # Empty implementation

    def move(self, new_x, new_y):
        pass  # Empty implementation 