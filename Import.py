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
from comb.Beehive import create_beehive_visualization, update_nectar_level

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
    """
    Create the beehive visualization using the new simplified version.
    This is a wrapper around the create_beehive_visualization function.
    """
    # Use our new visualization function from comb/Beehive.py
    ax, hexagon_grid, circle_markers, nectar_status, bee_status = create_beehive_visualization(
        fig=fig,
        subplot=gs[0, 0],
        num_bees=worker_bee_count,
        max_nectar=20  # Maximum nectar per cycle
    )
    
    # Position text in the extra space below the hexagons (data coordinates)
    # Add status text for bee sizes at the top
    max_x = 10 * 1.5  # COLS * OFFSET_X from Beehive.py
    
    bee_sizes_text = ax.text(max_x/2 - 2, -1.5, "Bee Growth: Normal", 
                           color='purple', fontweight='bold', fontsize=12,
                           horizontalalignment='center')
    
    timestamp_text = ax.text(max_x/2 - 2, -5, "Time: 0.0 seconds", fontsize=12,
                          horizontalalignment='center')
    
    # Create a box for the total counter
    total_box = plt.Rectangle((0, -9), max_x, 1.3, facecolor='honeydew', 
                            edgecolor='forestgreen', alpha=0.8, transform=ax.transData)
    ax.add_patch(total_box)
    
    # Add the prominent text for total nectar
    total_nectar_text = ax.text(max_x/2, -8.5, "Total Nectar: 0", 
                             color='darkgreen', fontweight='bold', fontsize=16,
                             horizontalalignment='center', verticalalignment='center')
    
    # Create empty placeholder lists for compatibility with existing code
    triangle_markers = []
    square_markers = []
    
    return ax, circle_markers, triangle_markers, square_markers, hexagon_grid, bee_status, timestamp_text, nectar_status, bee_sizes_text, total_nectar_text, total_box

def ensure_gold_dots_at_spawn_points(landscape_objects):
    """
    Ensures that nectar is accessible on flowers.
    This function adds additional gold dots to flower areas if necessary to ensure bees can find nectar.
    """
    # If we already have enough gold dots, don't add more
    min_required_dots = 5
    if len(landscape_objects.gold_dots) >= min_required_dots:
        return
        
    # Define flower areas where nectar can spawn
    flower_areas = [
        {"position": (4, 7), "width": 3, "height": 3, "name": "Center Flowers"},  # Center flower area
        {"position": (7, 4), "width": 3, "height": 3, "name": "Right Flowers"},   # Right flowers
        {"position": (1, 4), "width": 3, "height": 3, "name": "Left Flowers"},    # Left flowers
        {"position": (7, 11), "width": 3, "height": 3, "name": "Top Flowers"},    # Top flowers
        {"position": (1, 11), "width": 3, "height": 3, "name": "Upper Left Flowers"}, # Upper left flowers
    ]
    
    # Define forbidden zone - circular area centered at (5.5, 8.5) with radius 1.5
    forbidden_center_x = 5.5
    forbidden_center_y = 8.5
    forbidden_radius = 1.5
    
    # Helper function to check if a point is in the forbidden zone
    def is_in_forbidden_zone(x, y):
        distance = ((x - forbidden_center_x) ** 2 + (y - forbidden_center_y) ** 2) ** 0.5
        return distance <= forbidden_radius
    
    # Shuffle the flower areas to add randomness
    random.shuffle(flower_areas)
    
    # Count how many more dots we need
    dots_to_add = min_required_dots - len(landscape_objects.gold_dots)
    
    # Add dots to random flower areas until we have enough
    for area in flower_areas:
        if dots_to_add <= 0:
            break
            
        x0, y0 = area["position"]
        width, height = area["width"], area["height"]
        
        # Try multiple times to find a valid position
        max_attempts = 10
        for attempt in range(max_attempts):
            # Generate a random position within the flower area
            dot_x = x0 + random.randint(0, width-1) + 0.5
            dot_y = y0 + random.randint(0, height-1) + 0.5
            
            # Check if this position is in the forbidden zone
            if not is_in_forbidden_zone(dot_x, dot_y):
                # Valid position found
                print(f"Adding nectar to ensure accessibility on {area['name']} at ({dot_x}, {dot_y})")
                from Class2 import CircleDot
                alliance_dot = CircleDot((dot_x, dot_y))
                landscape_objects.gold_dots.append(alliance_dot)
                dots_to_add -= 1
                break
                
            if attempt == max_attempts - 1:
                print(f"⚠️ WARNING: Could not find valid position for nectar in {area['name']} after {max_attempts} attempts")

def regenerate_nectar(landscape, cycle_count, total_nectar):
    """
    Regenerate nectar for the next collection cycle
    """
    # Don't increment total here - it's already being done in the update function
    # before this function is called
    
    # Clear existing gold dots and reset the counter
    landscape.objects.gold_dots = []
    landscape.movement.gold_dots = []
    
    # Clear silver dots to regenerate them
    landscape.objects.silver_dots = []
    landscape.movement.silver_dots = []
    
    # Use the reset method in the Move class
    landscape.movement.reset_for_new_cycle()
    
    # Generate new gold dots - increase count for more variety (8-12 dots)
    nectar_count = random.randint(8, 12)
    landscape.objects.add_gold_dots(count=nectar_count)
    
    # Generate new silver dots for this cycle
    landscape.objects.add_silver_dots()
    
    # Ensure there's enough accessible nectar
    ensure_gold_dots_at_spawn_points(landscape.objects)
    
    # Update the movement logic to use the new gold dots and silver dots
    landscape.movement.gold_dots = landscape.objects.gold_dots
    landscape.movement.silver_dots = landscape.objects.silver_dots
    
    # Reset bee positions to near the hive to start the new cycle
    reset_bee_positions(landscape, reset_attributes=True)
    
    print(f"\n🌱 NECTAR REGENERATED - Starting cycle {cycle_count} (Total nectar so far: {total_nectar})")
    print(f"    - {len(landscape.objects.gold_dots)} gold nectar points generated")
    print(f"    - {len(landscape.objects.silver_dots)} silver power-ups generated")
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
            # Reset silver interaction counter to allow growth in the new cycle
            bee.silver_interactions = 0
            
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
    beehive_ax, circle_markers, triangle_markers, square_markers, hexagon_grid, bee_status, timestamp_text, nectar_status, bee_sizes_text, total_nectar_text, total_box = create_beehive_view(fig, gs, num_red_dots)
    
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
    all_artists.append(nectar_status)
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
                
                # Print the accumulated nectar information for debugging
                print(f"\n🍯 TOTAL NECTAR ACCUMULATED: {total_nectar_collected} (after cycle {nectar_cycle_count})")
                print(f"    This should make the honeycomb visibly darker now")
                
                # Regenerate nectar and reset for the next cycle
                nectar_cycle_count += 1
                landscape, total_nectar = regenerate_nectar(landscape, nectar_cycle_count, total_nectar_collected)
                
                # Reset tracking variables for this cycle
                is_nectar_exhausted = False
                last_nectar_count = 0
                
                # Update display to show the new cycle and total
                gold_collected = landscape.movement.gold_collected
                
                # Update nectar visualization with the total nectar (accumulated so far)
                update_nectar_level(
                    hexagon_grid, 
                    gold_collected,                  # Current cycle's nectar (0 at start)
                    landscape.max_gold_collected,    # Max nectar per cycle
                    total_nectar_collected,          # Total nectar accumulated so far
                    nectar_cycle_count,              # Current cycle 
                    nectar_status
                )
                
                # Update the total counter
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
                
                # Also update this for cycle completion:
                if (simulation_should_complete or movement_completed) and not waiting_for_next_cycle:
                    # Cycle is complete, enter waiting state
                    print(f"\n🍯 NECTAR CYCLE {nectar_cycle_count} COMPLETED at {elapsed_time:.1f} seconds")
                    print(f"All {len(landscape.objects.red_dots)} bees returned to hive with {landscape.movement.gold_collected}/{landscape.max_gold_collected} nectar")
                    print(f"Total nectar collected so far: {total_nectar_collected + landscape.movement.gold_collected}")
                    print(f"Waiting {WAIT_BETWEEN_CYCLES} seconds before starting next cycle...")
                    
                    # Update final appearance of the honeycomb before entering waiting state
                    update_nectar_level(
                        hexagon_grid, 
                        landscape.movement.gold_collected,  # Current cycle's nectar
                        landscape.max_gold_collected,       # Max nectar per cycle
                        total_nectar_collected + landscape.movement.gold_collected,  # Total including this cycle
                        nectar_cycle_count,                 # Current cycle 
                        nectar_status
                    )
                    
                    waiting_for_next_cycle = True
                    cycle_complete_time = time.time()
                
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
                # Use our new nectar update function with total nectar and cycle information
                update_nectar_level(
                    hexagon_grid, 
                    gold_collected,                  # Current cycle's nectar
                    landscape.max_gold_collected,    # Max nectar per cycle
                    total_nectar_collected + gold_collected,  # Total nectar (previous + current)
                    nectar_cycle_count,              # Current cycle 
                    nectar_status
                )
                
                # We don't need to set nectar_status text here, as the update_nectar_level function now does it
                
                # Update total nectar text
                total_nectar_text.set_text(f"TOTAL NECTAR: {total_nectar_collected + gold_collected}")
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
            
            # Get the beehive position for checking if bees are in/near the hive
            hive_x, hive_y = landscape.objects.beehive["position"]
            hive_width = landscape.objects.beehive["width"]
            hive_height = landscape.objects.beehive["height"]
            
            # Beehive position from movement logic
            movement_beehive_position = landscape.movement.beehive_position
            
            # Update circle marker positions to match red dots
            for i, red_dot in enumerate(landscape.objects.red_dots):
                if i < len(circle_markers):
                    # Check if the bee is in or very near the hive
                    x, y = red_dot.position
                    
                    # Calculate distance to hive
                    dist_to_hive = distance(
                        (x, y),
                        movement_beehive_position
                    )
                    
                    # Define threshold for being "in" the hive
                    hive_threshold = 1.0  # Units from hive center
                    
                    # Alternative check: see if bee is inside the hive rectangle or very close to it
                    in_hive_rect = (
                        hive_x <= x <= hive_x + hive_width and
                        hive_y <= y <= hive_y + hive_height
                    )
                    
                    near_hive = dist_to_hive <= hive_threshold or in_hive_rect
                    
                    # Also check if this bee is in the settled_dots set
                    is_settled = i in landscape.movement.settled_dots
                    
                    # Set visibility based on bee location
                    if near_hive or is_settled:
                        # The bee is in/near the hive, make it visible in the beehive visualization
                        circle_markers[i].show()
                        
                        # Map the positions from landscape to beehive
                        beehive_x = (red_dot.position[0] / landscape.block_size) * (COLS * OFFSET_X * 0.8)
                        beehive_y = (red_dot.position[1] / landscape.block_size) * (ROWS * OFFSET_Y * 0.8)
                        circle_markers[i].move(beehive_x, beehive_y)
                        
                        # Debug output for visibility
                        if frame % 20 == 0:  # Reduce spam
                            print(f"[DEBUG] Bee #{i+1} is in/near hive at {red_dot.position}, showing in comb")
                    else:
                        # The bee is not in the hive, hide it in the beehive visualization
                        circle_markers[i].hide()
                        
                        if frame % 20 == 0:  # Reduce spam
                            print(f"[DEBUG] Bee #{i+1} is outside hive at {red_dot.position}, hiding from comb")
                    
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
