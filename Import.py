# --- Import.py ---
from Class1 import Landscape
from Class3 import Move
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import random
import matplotlib.animation as animation
from comb.Classhive import CircleMarker, TriangleMarker, RectangleMarker, hexagon

# Define constant parameters for the hexagon grid
HEX_SIZE = 1
COLS = 10
ROWS = 5
OFFSET_X = 1.5 * HEX_SIZE
OFFSET_Y = np.sqrt(3) * HEX_SIZE

def create_beehive_view(fig, gs, worker_bee_count):
    # Size of the hexagons
    hex_size = HEX_SIZE
    
    # Create a grid of hexagons
    cols, rows = COLS, ROWS  # Number of hexagons in columns and rows
    
    # Offset for staggered rows
    offset_x = OFFSET_X
    offset_y = OFFSET_Y
    
    # Create subplot for beehive
    ax = fig.add_subplot(gs[0, 0])
    ax.set_aspect('equal')
    ax.axis('off')  # Turn off all axes, spines, and ticks
    
    # Initialize counts for the markers
    circle_count = worker_bee_count  # Use the same number of worker bees as red dots in the simulation
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
    hexagon_grid = []
    for row in range(rows):
        row_hexagons = []
        for col in range(cols):
            x = col * offset_x
            y = row * offset_y
            
            # Stagger odd rows
            if col % 2 == 1:
                y += offset_y / 2
                
            x_hexagon, y_hexagon = hexagon(x, y, hex_size)
            patch = ax.fill(x_hexagon, y_hexagon, edgecolor="black", facecolor="gold", lw=1)[0]
            row_hexagons.append(patch)
        hexagon_grid.append(row_hexagons)
    
    # Plot the markers
    circle_markers = []
    for circle_x, circle_y in circle_positions:
        circle_marker = CircleMarker(circle_x, circle_y)
        circle_marker.plot(ax)
        circle_markers.append(circle_marker)
        
    triangle_markers = []
    for triangle_x, triangle_y in triangle_positions:
        triangle_marker = TriangleMarker(triangle_x, triangle_y)
        triangle_marker.plot(ax)
        triangle_markers.append(triangle_marker)
        
    square_markers = []
    for square_x, square_y in square_positions:
        square_marker = RectangleMarker(square_x, square_y)
        square_marker.plot(ax)
        square_markers.append(square_marker)
    
    # Add a title for the beehive view
    ax.set_title("Beehive Visualization", fontsize=14)
    
    # Set text elements at the top of the visualization
    bee_status_text = ax.text(0.05, 0.02, f"Worker Bees: {circle_count}", transform=ax.transAxes, color='red', fontweight='bold')
    timestamp_text = ax.text(0.4, 0.02, "Timestamp: 0", transform=ax.transAxes)
    nectar_text = ax.text(0.7, 0.02, "Nectar Collected: 0", transform=ax.transAxes, color='darkorange', fontweight='bold')
    
    return ax, circle_markers, triangle_markers, square_markers, hexagon_grid, bee_status_text, timestamp_text, nectar_text

def main():
    try:
        num_houses = int(input("How many houses do you want (1 to 4)? "))
        if not 1 <= num_houses <= 4:
            raise ValueError
            
        num_red_dots = int(input("How many worker bees (red dots) do you want (1 to 4)? "))
        if not 1 <= num_red_dots <= 4:
            raise ValueError
    except ValueError:
        print("Invalid input. Please enter valid numbers as requested.")
        return

    # Create figure with grid layout for both visualizations
    fig = plt.figure(figsize=(16, 8))
    gs = GridSpec(1, 2, width_ratios=[1, 1])
    
    # Create beehive visualization with the correct number of worker bees
    beehive_ax, circle_markers, triangle_markers, square_markers, hexagon_grid, bee_status_text, timestamp_text, nectar_text = create_beehive_view(fig, gs, num_red_dots)
    
    # Initialize the landscape grid and environment
    landscape = Landscape(block_size=15, max_gold_collected=20, num_houses=num_houses)

    # Setup objects in the environment
    landscape.objects.add_beehive(position=(11, 0), height=3, width=3)
    landscape.objects.add_pond(position=(12, 5), height=5, width=3)
    landscape.objects.add_red_dots(count=num_red_dots)  # Now using add_red_dots with count
    landscape.objects.add_gold_dots(count=5)
    landscape.objects.add_silver_dots()

    # Initialize movement logic with obstacle avoidance (pond + forbidden zone)
    landscape.movement = Move(
        red_dots=landscape.objects.red_dots,  # Pass all red dots
        gold_dots=landscape.objects.gold_dots,
        beehive_position=(11, 2),
        max_gold_collected=landscape.max_gold_collected,
        pond_position=(12, 5),
        pond_size=(3, 5),
        forbidden_zone_func=landscape.is_inside_forbidden_zone
    )

    # Show landscape initially
    landscape.display(fig=fig, subplot_spec=gs[0, 1], title=f"Landscape with {num_red_dots} Worker Bees")
    
    # Track animation frame
    frame_count = [0]
    
    # Create static list of artists to avoid flickering
    all_artists = []
    
    # First, add all hexagon patches
    for row in hexagon_grid:
        for hex_patch in row:
            all_artists.append(hex_patch)
    
    # Add all marker objects
    for marker in circle_markers:
        if marker.circle:
            all_artists.append(marker.circle)
    
    for marker in triangle_markers:
        if marker.triangle:
            all_artists.append(marker.triangle)
            
    for marker in square_markers:
        if marker.rectangle:
            all_artists.append(marker.rectangle)
    
    # Add text elements
    all_artists.append(timestamp_text)
    all_artists.append(nectar_text)
    all_artists.append(bee_status_text)
    
    # Last nectar count to detect changes
    last_nectar_count = 0
    is_nectar_exhausted = False
    
    # Define animation update function that updates both displays
    def update(frame):
        nonlocal last_nectar_count, is_nectar_exhausted
        
        frame_count[0] += 1
        
        # Update landscape simulation
        if landscape.movement and not landscape.movement.completed:
            landscape.movement.update_state()
            
            # Get current nectar collection count
            gold_collected = landscape.movement.gold_collected
            
            # Only update visual elements if nectar count changed
            if gold_collected != last_nectar_count or not is_nectar_exhausted:
                # Update the hexagon colors based on nectar collection progress
                if gold_collected > 0:
                    # Calculate how many rows to fill based on nectar collection
                    fill_level = min(5, max(1, int(gold_collected / landscape.max_gold_collected * 5)))
                    
                    # Fill hexagons with honey color based on collection progress
                    for row_idx in range(fill_level):
                        row = hexagon_grid[row_idx]
                        for hex_patch in row:
                            # Set a honey color gradient based on collection progress
                            honey_intensity = gold_collected / landscape.max_gold_collected
                            hex_patch.set_facecolor((1.0, 0.8 - honey_intensity * 0.3, 0.2, 0.7 + honey_intensity * 0.3))
                
                # Update status text only if something changed
                nectar_text.set_text(f"Nectar Collected: {gold_collected}/{landscape.max_gold_collected}")
                last_nectar_count = gold_collected
                
                # Check if nectar is exhausted
                if gold_collected >= landscape.max_gold_collected:
                    is_nectar_exhausted = True
            
            # Always update timestamp and bee positions
            timestamp_text.set_text(f"Timestamp: {frame_count[0]}")
            
            # Update circle marker positions to match red dots
            for i, red_dot in enumerate(landscape.objects.red_dots):
                if i < len(circle_markers):
                    # Map the positions from landscape to beehive
                    beehive_x = (red_dot.position[0] / landscape.block_size) * (COLS * OFFSET_X * 0.8)
                    beehive_y = (red_dot.position[1] / landscape.block_size) * (ROWS * OFFSET_Y * 0.8)
                    circle_markers[i].move(beehive_x, beehive_y)
        
        # Always return the same list of artists to prevent blinking
        return all_artists
    
    # Create a combined animation
    ani = animation.FuncAnimation(
        fig, 
        update, 
        frames=1000,
        interval=200,
        blit=True,  # Re-enable blitting but with proper artist management
        repeat=False
    )
    
    # Display the combined figure
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
