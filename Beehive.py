import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import random
from Classhive import CircleMarker, TriangleMarker, RectangleMarker, hexagon  # Fixed capitalization

# Size of the hexagons
hex_size = 1

# Create a grid of hexagons
cols, rows = 10, 5  # Number of hexagons in columns and rows

# Offset for staggered rows
offset_x = 1.5 * hex_size
offset_y = np.sqrt(3) * hex_size

# Define the custom color map from lightyellow to gold
colors = ["lightyellow", "khaki", "yellow", "gold"]
cmap = ListedColormap(colors)

# Initialize counts for the markers
circle_count = 1
triangle_count = random.randint(1, 5)
square_count = random.randint(1, 5)

# Function to place markers at random hexagon centers and return their positions
def generate_marker_positions(marker_count):
    positions = []
    for _ in range(marker_count):
        random_col = random.randint(0, cols - 1)
        random_row = random.randint(0, rows - 1)
        x = random_col * offset_x  # X coordinate of the hexagon
        y = random_row * offset_y  # Y coordinate of the hexagon

        # Apply staggered row adjustment for the selected column
        if random_col % 2 == 1:
            y += offset_y / 2

        positions.append((x, y))
    return positions

# Initial marker positions
circle_positions = generate_marker_positions(circle_count)
triangle_positions = generate_marker_positions(triangle_count)
square_positions = generate_marker_positions(square_count)

# Set up the figure and axes
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_aspect('equal')
ax.axis('off')  # Turn off all axes, spines, and ticks

# Draw hexagons to form the hive
hexagons = []
hexagon_grid = []  # Store hexagons row by row for incremental plotting
for row in range(rows):
    row_hexagons = []
    for col in range(cols):
        x = col * offset_x
        y = row * offset_y

        # Stagger odd rows
        if col % 2 == 1:
            y += offset_y / 2

        x_hexagon, y_hexagon = hexagon(x, y, hex_size)
        patch = ax.fill(x_hexagon, y_hexagon, edgecolor="black", facecolor="white", lw=1)[0]
        patch.set_visible(False)  # Initially hide all hexagons
        row_hexagons.append(patch)
    hexagon_grid.append(row_hexagons)

# Create a color bar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=1))
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, orientation='vertical')
cbar.set_ticks([0, 0.33, 0.66, 1])
cbar.set_ticklabels(['Low', 'Medium', 'High', 'Very High'])
cbar.set_label("Level of Concentration")

# Title and text for markers
title = ax.set_title(f"Timestamp: 1")
red_text = fig.text(0.5, 0.95, f"Red Circles: {circle_count}", ha='center', fontsize=12, color='red') 
blue_text = fig.text(0.5, 0.9, f"Blue Triangles: {triangle_count}", ha='center', fontsize=12, color='blue') 
purple_text = fig.text(0.5, 0.85, f"Purple Squares: {square_count}", ha='center', fontsize=12, color='purple') 

# Plot the markers
circle_markers = []
triangle_markers = []
square_markers = []

for circle_x, circle_y in circle_positions:
    circle_marker = CircleMarker(circle_x, circle_y)
    circle_marker.plot(ax)
    circle_markers.append(circle_marker)

for triangle_x, triangle_y in triangle_positions:
    triangle_marker = TriangleMarker(triangle_x, triangle_y)
    triangle_marker.plot(ax)
    triangle_markers.append(triangle_marker)

for square_x, square_y in square_positions:
    square_marker = RectangleMarker(square_x, square_y)
    square_marker.plot(ax)
    square_markers.append(square_marker)

# Loop through timesteps
for i in range(1, 11):
    if i <= 5:
        # Gradually build the hexagonal grid row by row
        for row in range(i):  # Reveal one additional row at each timestamp
            for hexagon_patch in hexagon_grid[row]:
                hexagon_patch.set_visible(True)
    else:
        # Gradually fill the honey in hexagons
        for row in hexagon_grid:
            for hexagon_patch in row:
                # Update hexagon colors
                concentration_min = (i - 6) * 0.25
                concentration_max = (i - 5) * 0.25
                concentration_level = random.uniform(concentration_min, concentration_max)
                facecolor = cmap(concentration_level)
                hexagon_patch.set_facecolor(facecolor)

    # Update marker positions (dots move randomly in every timestamp)
    circle_positions = generate_marker_positions(circle_count)
    for j, (circle_x, circle_y) in enumerate(circle_positions):
        circle_markers[j].circle.set_center((circle_x, circle_y))

    triangle_positions = generate_marker_positions(triangle_count)
    for j, (triangle_x, triangle_y) in enumerate(triangle_positions):
        triangle_markers[j].triangle.set_xy([
            (triangle_x, triangle_y + 0.2),  # Top
            (triangle_x - 0.2, triangle_y - 0.2),  # Bottom left
            (triangle_x + 0.2, triangle_y - 0.2),  # Bottom right
        ])

    square_positions = generate_marker_positions(square_count)
    for j, (square_x, square_y) in enumerate(square_positions):
        square_markers[j].rectangle.set_xy((square_x - 0.15, square_y - 0.1))

    title.set_text(f"Timestamp: {i}")  # Update title
    plt.pause(1)  # Pause for 1 second between timestamps

# Keep the plot open after the animation ends
plt.show()