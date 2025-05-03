# --- Import.py ---
from Class1 import Landscape
from Class3 import Move
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import random
from Classhive import CircleMarker, TriangleMarker, RectangleMarker, hexagon

def create_beehive_view(fig, gs):
    # Size of the hexagons
    hex_size = 1
    
    # Create a grid of hexagons
    cols, rows = 10, 5  # Number of hexagons in columns and rows
    
    # Offset for staggered rows
    offset_x = 1.5 * hex_size
    offset_y = np.sqrt(3) * hex_size
    
    # Define the custom color map from lightyellow to gold
    colors = ["lightyellow", "khaki", "yellow", "gold"]
    
    # Create subplot for beehive
    ax = fig.add_subplot(gs[0, 0])
    ax.set_aspect('equal')
    ax.axis('off')  # Turn off all axes, spines, and ticks
    
    # Initialize counts for the markers
    circle_count = 1
    triangle_count = random.randint(1, 5)
    square_count = random.randint(1, 5)
    
    # Generate marker positions
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
    
    # Generate positions
    circle_positions = generate_marker_positions(circle_count)
    triangle_positions = generate_marker_positions(triangle_count)
    square_positions = generate_marker_positions(square_count)
    
    # Draw filled hexagons
    for row in range(rows):
        for col in range(cols):
            x = col * offset_x
            y = row * offset_y
            
            # Stagger odd rows
            if col % 2 == 1:
                y += offset_y / 2
                
            x_hexagon, y_hexagon = hexagon(x, y, hex_size)
            ax.fill(x_hexagon, y_hexagon, edgecolor="black", facecolor="gold", lw=1)
    
    # Plot the markers
    for circle_x, circle_y in circle_positions:
        circle_marker = CircleMarker(circle_x, circle_y)
        circle_marker.plot(ax)
        
    for triangle_x, triangle_y in triangle_positions:
        triangle_marker = TriangleMarker(triangle_x, triangle_y)
        triangle_marker.plot(ax)
        
    for square_x, square_y in square_positions:
        square_marker = RectangleMarker(square_x, square_y)
        square_marker.plot(ax)
    
    # Set title with marker counts
    ax.set_title(f"Red Circles: {circle_count}\nBlue Triangles: {triangle_count}\nPurple Squares: {square_count}\nTimestamp: 10")
    
    return ax

def main():
    try:
        num_houses = int(input("How many houses do you want (1 to 4)? "))
        if not 1 <= num_houses <= 4:
            raise ValueError
    except ValueError:
        print("Invalid input. Please enter a number between 1 and 4.")
        return

    # Create figure with grid layout for both visualizations
    fig = plt.figure(figsize=(16, 8))
    gs = GridSpec(1, 2, width_ratios=[1, 1])
    
    # Create beehive visualization
    beehive_ax = create_beehive_view(fig, gs)
    
    # Initialize the landscape grid and environment
    landscape = Landscape(block_size=15, max_gold_collected=20, num_houses=num_houses)

    # Setup objects in the environment
    landscape.objects.add_beehive(position=(11, 0), height=3, width=3)
    landscape.objects.add_pond(position=(12, 5), height=5, width=3)
    landscape.objects.add_red_dot()
    landscape.objects.add_gold_dots(count=5)
    landscape.objects.add_silver_dots()

    # Initialize movement logic with obstacle avoidance (pond + forbidden zone)
    landscape.movement = Move(
        red_dot=landscape.objects.red_dot,
        gold_dots=landscape.objects.gold_dots,
        beehive_position=(11, 2),
        max_gold_collected=landscape.max_gold_collected,
        pond_position=(12, 5),
        pond_size=(3, 5),
        forbidden_zone_func=landscape.is_inside_forbidden_zone
    )

    # Show simulation - modify to use our subplot
    landscape.display(fig=fig, subplot_spec=gs[0, 1], title="15x15 Landscape with Beehive and Pond")
    
    # Display the combined figure
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
