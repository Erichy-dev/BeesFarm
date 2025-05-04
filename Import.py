# --- Import.py ---
from Class1 import Landscape
from Class3 import Move
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import random
import matplotlib.animation as animation
import time  # For tracking real elapsed time
from comb.Classhive import CircleMarker, TriangleMarker, RectangleMarker, hexagon

# Define constant parameters for the hexagon grid
HEX_SIZE = 1
COLS = 10
ROWS = 5
OFFSET_X = 1.5 * HEX_SIZE
OFFSET_Y = np.sqrt(3) * HEX_SIZE

# Define simulation speed parameters
FPS = 5  # Frames per second (determines animation interval)
SIMULATION_SPEED = 1.0/FPS  # Seconds per frame - synchronized with FPS for real-time accuracy

# Define the waiting period between nectar cycles (in seconds)
WAIT_BETWEEN_CYCLES = 10.0  # Increased from 5 to 10 seconds

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
    
    # Adjust axis limits to create more space for text
    # Calculate the max extent of the hexagon grid
    max_x = cols * offset_x
    max_y = rows * offset_y + offset_y/2
    
    # Set extended limits with extra padding at bottom for text
    ax.set_xlim(-1, max_x + 1)
    ax.set_ylim(-9, max_y + 1)  # Increase bottom space to -9 for more text space
    
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
        # Initial size is just the default (will be updated when bees interact with silver)
        circle_marker = CircleMarker(circle_x, circle_y, radius=0.1, color='red')
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
    ax.set_title("Beehive Visualization", fontsize=14, pad=15)
    
    # Position text in the extra space below the hexagons (using data coordinates, not axes coordinates)
    # Add status text for bee sizes at the top
    bee_sizes_text = ax.text(max_x/2 - 2, -1.5, "Bee Growth: Normal", 
                           color='purple', fontweight='bold', fontsize=12,
                           horizontalalignment='center')
    
    # Position the other three texts below the Bee Growth text, one per line
    bee_status_text = ax.text(max_x/2 - 2, -3, f"Worker Bees: {circle_count}", 
                             color='red', fontweight='bold', fontsize=12,
                             horizontalalignment='center')
    
    timestamp_text = ax.text(max_x/2 - 2, -5, "Time: 0.0 seconds", fontsize=12,
                           horizontalalignment='center')
    
    nectar_text = ax.text(max_x/2 - 2, -7, "Nectar Collected: 0", 
                         color='darkorange', fontweight='bold', fontsize=12,
                         horizontalalignment='center')
    
    # Add text for total nectar collected - make it more prominent
    # Create a box for the total counter
    total_box = plt.Rectangle((0, -9), max_x, 1.3, facecolor='honeydew', 
                             edgecolor='forestgreen', alpha=0.8, transform=ax.transData)
    ax.add_patch(total_box)
    
    # Add the prominent text for total nectar
    total_nectar_text = ax.text(max_x/2, -8.5, "Total Nectar: 0", 
                             color='darkgreen', fontweight='bold', fontsize=16,
                             horizontalalignment='center', verticalalignment='center')
    
    return ax, circle_markers, triangle_markers, square_markers, hexagon_grid, bee_status_text, timestamp_text, nectar_text, bee_sizes_text, total_nectar_text, total_box

def ensure_gold_dots_at_spawn_points(landscape_objects):
    """
    Ensures that each spawn point has at least one gold dot (alliance).
    This function checks if there are gold dots in each spawn area and 
    adds one if none are found.
    """
    spawn_areas = [
        {"position": (1, 4), "width": 3, "height": 3},
        {"position": (1, 11), "width": 3, "height": 3},
        {"position": (7, 4), "width": 3, "height": 3},
        {"position": (7, 11), "width": 3, "height": 3}
    ]
    
    # Check each spawn area
    for area in spawn_areas:
        x0, y0 = area["position"]
        width, height = area["width"], area["height"]
        
        # Define the area boundaries
        x_min, x_max = x0, x0 + width
        y_min, y_max = y0, y0 + height
        
        # Check if any gold dots are in this area
        has_gold_in_area = False
        for gold_dot in landscape_objects.gold_dots:
            gx, gy = gold_dot.position
            if x_min <= gx <= x_max and y_min <= gy <= y_max:
                has_gold_in_area = True
                break
        
        # If no gold dots in this area, add one (alliance)
        if not has_gold_in_area:
            print(f"Adding alliance (gold nectar) to spawn area at {area['position']}")
            # Generate a gold dot in the center of the area
            dot_x = x0 + width // 2
            dot_y = y0 + height // 2
            from Class2 import CircleDot
            alliance_dot = CircleDot((dot_x + 0.5, dot_y + 0.5))
            landscape_objects.gold_dots.append(alliance_dot)

def regenerate_nectar(landscape, cycle_count, total_nectar):
    """
    Regenerate nectar for the next collection cycle
    """
    # Don't increment total here - it's already being done in the update function
    # before this function is called
    
    # Clear existing gold dots and reset the counter
    landscape.objects.gold_dots = []
    landscape.movement.gold_dots = []
    
    # Use the reset method in the Move class
    landscape.movement.reset_for_new_cycle()
    
    # Generate new gold dots
    landscape.objects.add_gold_dots(count=5)
    
    # Ensure each spawn point has at least one gold dot
    ensure_gold_dots_at_spawn_points(landscape.objects)
    
    # Update the movement logic to use the new gold dots
    landscape.movement.gold_dots = landscape.objects.gold_dots
    
    # Reset bee positions to near the hive to start the new cycle
    reset_bee_positions(landscape, reset_attributes=True)
    
    print(f"\n🌱 NECTAR REGENERATED - Starting cycle {cycle_count} (Total nectar so far: {total_nectar})")
    return landscape, total_nectar

def reset_bee_positions(landscape, reset_attributes=False):
    """
    Reset bee positions to near the hive to start a new collection cycle
    If reset_attributes is True, also reset bee size and speed to normal
    """
    hive_x, hive_y = landscape.objects.beehive["position"]
    hive_width = landscape.objects.beehive["width"]
    hive_height = landscape.objects.beehive["height"]
    
    for i, bee in enumerate(landscape.objects.red_dots):
        # Position just outside the hive with some randomness
        x_offset = random.uniform(0.5, 1.5)
        y_offset = random.uniform(0.5, 1.5)
        
        # Position around the hive
        position_side = i % 4  # 0: right, 1: top, 2: left, 3: bottom
        
        if position_side == 0:  # right side
            bee.position = [hive_x + hive_width + x_offset, hive_y + random.uniform(0, hive_height)]
        elif position_side == 1:  # top
            bee.position = [hive_x + random.uniform(0, hive_width), hive_y + hive_height + y_offset]
        elif position_side == 2:  # left side
            bee.position = [hive_x - x_offset, hive_y + random.uniform(0, hive_height)]
        else:  # bottom
            bee.position = [hive_x + random.uniform(0, hive_width), hive_y - y_offset]
            
        # Reset bee attributes if requested
        if reset_attributes and hasattr(bee, 'original_size'):
            # Reset size to original
            bee.current_size = bee.original_size
            # Reset speed to normal
            bee.speed_modifier = 1.0
            
            print(f"Reset bee #{i+1} attributes to normal (size: {bee.current_size}, speed: {bee.speed_modifier})")

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
    beehive_ax, circle_markers, triangle_markers, square_markers, hexagon_grid, bee_status_text, timestamp_text, nectar_text, bee_sizes_text, total_nectar_text, total_box = create_beehive_view(fig, gs, num_red_dots)
    
    # Initialize the landscape grid and environment
    landscape = Landscape(block_size=15, max_gold_collected=20, num_houses=num_houses)

    # Setup objects in the environment
    landscape.objects.add_beehive(position=(11, 0), height=3, width=3)
    landscape.objects.add_pond(position=(12, 5), height=5, width=3)
    landscape.objects.add_red_dots(count=num_red_dots)  # Now using add_red_dots with count
    landscape.objects.add_gold_dots(count=5)
    landscape.objects.add_silver_dots()
    
    # Ensure there's gold nectar (alliance) at each spawn point
    ensure_gold_dots_at_spawn_points(landscape.objects)

    # Initialize movement logic with obstacle avoidance (pond + forbidden zone)
    landscape.movement = Move(
        red_dots=landscape.objects.red_dots,  # Pass all red dots
        gold_dots=landscape.objects.gold_dots,
        beehive_position=(11, 2),
        max_gold_collected=landscape.max_gold_collected,
        pond_position=(12, 5),
        pond_size=(3, 5),
        forbidden_zone_func=landscape.is_inside_forbidden_zone,
        silver_dots=landscape.objects.silver_dots  # Pass silver dots for interaction
    )

    # Show landscape initially
    landscape.display(fig=fig, subplot_spec=gs[0, 1], title=f"Landscape with {num_red_dots} Worker Bees")
    
    # Track real time when animation starts
    start_time = time.time()
    
    # Simulation completion flag (separate from landscape.movement.completed)
    # Remove final_time variable as we never want the simulation to be marked as "COMPLETED"
    simulation_completed = False
    
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
    all_artists.append(bee_sizes_text)
    all_artists.append(total_nectar_text)
    all_artists.append(total_box)  # Add the background box for total nectar
    
    # Last nectar count to detect changes
    last_nectar_count = 0
    is_nectar_exhausted = False
    
    # Track nectar regeneration cycles
    nectar_cycle_count = 1
    
    # Track total nectar collected across all cycles
    total_nectar_collected = 0
    
    # Add waiting state variables
    waiting_for_next_cycle = False
    cycle_complete_time = None
    
    # Define a function to measure distance between two points
    def distance(p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5
    
    # Define custom completion check that's more robust
    def check_simulation_completed():
        """Check if simulation should be considered complete"""
        # First check if all nectar has been collected
        nectar_all_collected = landscape.movement.are_all_nectar_collected()
        if not nectar_all_collected:
            print(f"[DEBUG] Not all nectar collected yet: {landscape.movement.gold_collected}/{landscape.max_gold_collected}")
            return False
        
        # Only check bee positions if all nectar is collected
        print(f"\n[DEBUG] All nectar collected ({landscape.movement.gold_collected}/{landscape.max_gold_collected}), checking bees")
            
        # Get the actual beehive position from the movement logic
        movement_beehive_position = landscape.movement.beehive_position
        print(f"[DEBUG] Beehive position: {movement_beehive_position}")
            
        # Check if all bees are in the beehive area OR close enough to the beehive
        all_returned = True
        max_distance_threshold = 2.0  # Maximum allowed distance from beehive center
            
        for i, dot in enumerate(landscape.objects.red_dots):
            x, y = dot.position
            # Check distance to beehive center
            dist_to_hive = distance((x, y), movement_beehive_position)
            is_close_enough = dist_to_hive <= max_distance_threshold
                
            print(f"[DEBUG] Bee #{i+1} at position {dot.position} - Distance to hive: {dist_to_hive:.2f}, Close enough: {is_close_enough}")
                
            # Consider the bee "returned" if it's close enough
            if not is_close_enough:
                all_returned = False
            
        print(f"[DEBUG] All bees returned: {all_returned}")
            
        return all_returned
    
    # Define animation update function that updates both displays
    def update(frame):
        nonlocal last_nectar_count, is_nectar_exhausted, nectar_cycle_count
        nonlocal waiting_for_next_cycle, cycle_complete_time, total_nectar_collected
        nonlocal landscape, simulation_completed  # Make landscape nonlocal so we can modify it
        
        # Get real elapsed time for accurate timing
        elapsed_time = time.time() - start_time
        formatted_time = f"{elapsed_time:.1f}"
        
        # Note: we never permanently mark the simulation as completed
        # so this block should never execute
        if simulation_completed:
            timestamp_text.set_text(f"Time: {formatted_time} seconds")
            return all_artists
        
        # If we're in the waiting period between cycles
        if waiting_for_next_cycle:
            wait_time_elapsed = time.time() - cycle_complete_time
            remaining_wait = WAIT_BETWEEN_CYCLES - wait_time_elapsed
            
            if remaining_wait > 0:
                # Still waiting, update the status text
                timestamp_text.set_text(f"Time: {formatted_time} seconds (Next cycle in {remaining_wait:.1f}s)")
                return all_artists
            else:
                # Waiting period is over, regenerate nectar
                print(f"\n⏰ Waiting period complete. Regenerating nectar for cycle {nectar_cycle_count}...")
                waiting_for_next_cycle = False
                
                # Add current nectar count to total before regenerating
                total_nectar_collected += landscape.movement.gold_collected
                
                # Regenerate nectar and reset for the next cycle
                nectar_cycle_count += 1
                landscape, total_nectar = regenerate_nectar(landscape, nectar_cycle_count, total_nectar_collected)
                
                # Reset tracking variables
                is_nectar_exhausted = False
                last_nectar_count = 0
                
                # Update display to show the new cycle and total
                gold_collected = landscape.movement.gold_collected
                nectar_text.set_text(f"Nectar Collected: {gold_collected}/{landscape.max_gold_collected} (Cycle {nectar_cycle_count})")
                total_nectar_text.set_text(f"TOTAL NECTAR: {total_nectar_collected}")
                
                # Reset circle markers to match refreshed bee attributes
                for i, red_dot in enumerate(landscape.objects.red_dots):
                    if i < len(circle_markers) and hasattr(red_dot, 'current_size'):
                        # Reset circle size to normal
                        circle_markers[i].radius = red_dot.current_size
                        if circle_markers[i].circle:
                            circle_markers[i].circle.set_radius(red_dot.current_size)
                            # Reset color to normal red
                            circle_markers[i].circle.set_facecolor('red')
                
                # Reset bee size text
                bee_sizes_text.set_text("Bee Growth: Normal")
                
                return all_artists
        
        # Check for completion directly
        simulation_should_complete = check_simulation_completed()
        movement_completed = hasattr(landscape.movement, 'completed') and landscape.movement.completed
        
        # Log the completion status
        if frame % 20 == 0:  # Only log every 20 frames to reduce spam
            print(f"[DEBUG] Frame {frame} - Simulation should complete: {simulation_should_complete}")
            print(f"[DEBUG] Frame {frame} - Movement completed: {movement_completed}")
            print(f"[DEBUG] Current nectar: {landscape.movement.gold_collected}/{landscape.max_gold_collected}")
            for i, dot in enumerate(landscape.objects.red_dots):
                print(f"[DEBUG] Bee #{i+1} at position {dot.position}")
            
        if (simulation_should_complete or movement_completed) and not waiting_for_next_cycle:
            # Cycle is complete, enter waiting state
            print(f"\n🍯 NECTAR CYCLE {nectar_cycle_count} COMPLETED at {elapsed_time:.1f} seconds")
            print(f"All {len(landscape.objects.red_dots)} bees returned to hive with {landscape.movement.gold_collected}/{landscape.max_gold_collected} nectar")
            print(f"Total nectar collected so far: {total_nectar_collected + landscape.movement.gold_collected}")
            print(f"Waiting {WAIT_BETWEEN_CYCLES} seconds before starting next cycle...")
            
            waiting_for_next_cycle = True
            cycle_complete_time = time.time()
            
            # Update text to show waiting status
            timestamp_text.set_text(f"Time: {formatted_time} seconds (Next cycle in {WAIT_BETWEEN_CYCLES:.1f}s)")
            return all_artists
        
        # Update landscape simulation
        if landscape.movement:
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
                nectar_text.set_text(f"Nectar Collected: {gold_collected}/{landscape.max_gold_collected} (Cycle {nectar_cycle_count})")
                total_nectar_text.set_text(f"TOTAL NECTAR: {total_nectar_collected}")
                last_nectar_count = gold_collected
                
                # Check if nectar is exhausted
                if gold_collected >= landscape.max_gold_collected:
                    is_nectar_exhausted = True
                    print(f"[DEBUG] Nectar target reached ({gold_collected}/{landscape.max_gold_collected}), checking for completion...")
            
            # Always update timestamp and bee positions (unless we're waiting for next cycle)
            if not waiting_for_next_cycle:
                timestamp_text.set_text(f"Time: {formatted_time} seconds")
            
            # Track bee sizes for reporting
            bee_size_changes = False
            max_bee_size = 0.1  # Default bee size
            
            # Update circle marker positions to match red dots
            for i, red_dot in enumerate(landscape.objects.red_dots):
                if i < len(circle_markers):
                    # Map the positions from landscape to beehive
                    beehive_x = (red_dot.position[0] / landscape.block_size) * (COLS * OFFSET_X * 0.8)
                    beehive_y = (red_dot.position[1] / landscape.block_size) * (ROWS * OFFSET_Y * 0.8)
                    circle_markers[i].move(beehive_x, beehive_y)
                    
                    # Update the size of the circle based on silver dot interactions
                    if hasattr(red_dot, 'current_size'):
                        max_bee_size = max(max_bee_size, red_dot.current_size)
                        
                        if red_dot.current_size != circle_markers[i].radius:
                            bee_size_changes = True
                            # Create a new circle with the updated size
                            if circle_markers[i].circle:
                                circle_markers[i].radius = red_dot.current_size
                                circle_markers[i].circle.set_radius(red_dot.current_size)
                                
                                # Also change color to indicate the increased power
                                intensity = (red_dot.current_size - 0.1) / 0.25  # Normalize to 0-1 range
                                new_color = (1.0, max(0, 1.0 - intensity), max(0, 1.0 - intensity))  # Red to more saturated red
                                circle_markers[i].circle.set_facecolor(new_color)
            
            # Update the bee sizes text
            if max_bee_size > 0.1:
                bee_sizes_text.set_text(f"Bee Growth: {int((max_bee_size/0.1 - 1) * 100)}% Larger")
            else:
                bee_sizes_text.set_text("Bee Growth: Normal")
        
        # Always return the same list of artists to prevent blinking
        return all_artists
    
    try:
        # Create a combined animation with a very large number of frames to ensure it doesn't stop
        ani = animation.FuncAnimation(
            fig, 
            update, 
            frames=999999,  # Increased from 1000 to practically infinite
            interval=1000/FPS,  # Convert FPS to milliseconds between frames
            blit=True,  # Re-enable blitting but with proper artist management
            repeat=True  # Set to True to make sure it repeats if it ever reaches the end
        )
        
        # Display the combined figure with right plot margin for annotations
        plt.tight_layout()
        plt.show()
    except Exception as e:
        # Print any error that occurs during animation
        print(f"Error during animation: {e}")
        print(f"Total nectar collected: {total_nectar_collected}")
        
if __name__ == "__main__":
    main()
