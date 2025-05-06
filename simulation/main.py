import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import random
import numpy as np
from matplotlib.gridspec import GridSpec
import os

from visualization.hive_view import create_beehive_view, update_nectar_level, update_queen_drone_simulation
from entities.landscape import Landscape
from movement.movement import Move
from utils.helpers import ensure_gold_dots_at_spawn_points, regenerate_nectar, reset_bee_positions
from utils.constants import FPS, WAIT_BETWEEN_CYCLES, DEBUG_VERBOSE, COLS, ROWS, OFFSET_X, OFFSET_Y

# Global variable to track if simulation is complete
SIMULATION_COMPLETE = False

def main():
    try:
        num_houses = int(input("How many houses do you want (1 to 4)? "))
        if not 1 <= num_houses <= 4:
            raise ValueError
            
        num_red_dots = int(input("How many worker bees (red dots) do you want (1 to 4)? "))
        if not 1 <= num_red_dots <= 4:
            raise ValueError
            
        num_drone_bees = int(input("How many drone bees (black dots) do you want (1 to 4)? "))
        if not 1 <= num_drone_bees <= 4:
            raise ValueError
            
        max_timesteps = int(input("How many simulation timesteps do you want (10-1000)? "))
        if not 10 <= max_timesteps <= 1000:
            max_timesteps = 10  # Default to 10 if invalid input
            print("Using default of 10 timesteps.")
    except ValueError:
        print("Invalid input. Please enter valid numbers as requested.")
        return

    # Create figure with grid layout for both visualizations
    fig = plt.figure(figsize=(16, 8))
    gs = GridSpec(1, 2, width_ratios=[1, 1])
    
    # Create beehive visualization with the correct number of worker bees
    beehive_ax, circle_markers, triangle_markers, square_markers, hexagon_grid, bee_status, timestamp_text, nectar_status, bee_sizes_text, total_nectar_text, total_box = create_beehive_view(fig, gs, num_red_dots, drone_bees=num_drone_bees)
    
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
    all_artists.append(bee_status)
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
    
    # Initialize animation variable
    ani = None
    
    # Initialize bee tracking variables together
    # Track bee positions in comb - where they should appear when they're in the hive
    bee_comb_positions = {}  # Dictionary to store bee positions in the comb
    
    # Track entrance animations - for bees that are still moving to their final position
    bee_entrance_animations = {}  # {bee_index: (target_x, target_y, progress)}
    
    # Track which bees are visible in the hive
    bees_in_hive_prev = set()  # Track which bees were previously in the hive
    bees_in_hive_current = set()  # Track which bees are currently in the hive
    
    # Define a function to measure distance between two points
    def distance(p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5
    
    # Add a debug function at the beginning of main():
    # A function to print focused debug information about bee placement
    def debug_bee_position(message, bee_index=None, position=None, level="INFO"):
        # Only print if it's an important message or we explicitly want verbose logs
        if level in ["ERROR", "WARNING", "SUCCESS"] or DEBUG_VERBOSE:
            prefix = ""
            if level == "ERROR":
                prefix = "🚨 ERROR: "
            elif level == "WARNING":
                prefix = "⚠️ WARNING: "
            elif level == "SUCCESS":
                prefix = "✅ SUCCESS: "
            elif level == "INFO":
                prefix = "ℹ️ INFO: "
            
            bee_info = f"Bee #{bee_index+1} " if bee_index is not None else ""
            position_info = f"at position {position}" if position is not None else ""
            
            print(f"{prefix}{bee_info}{position_info} {message}")
    
    # Modify the check_simulation_completed function to accept frame as a parameter:
    def check_simulation_completed(frame):
        """Check if simulation should be considered complete"""
        # First check if all nectar has been collected
        nectar_all_collected = landscape.movement.are_all_nectar_collected()
        
        # Only proceed with detailed checks when needed
        if not nectar_all_collected:
            # No need to log this every time - it's too verbose
            # Only log occasionally for status updates
            if frame % 100 == 0:  # Only every 100 frames
                print(f"[INFO] Nectar collection in progress: {landscape.movement.gold_collected}/{landscape.max_gold_collected}")
            return False
        
        # Nectar is collected, only do detailed checks every few frames to reduce spam
        if frame % 10 != 0:  # Skip most frames
            return False  # Not checking this frame
        
        # We're checking completion this frame
        # Get the actual beehive position from the movement logic (no need to log this)
        movement_beehive_position = landscape.movement.beehive_position
            
        # Check if all bees are in the beehive area OR close enough to the beehive
        all_returned = True
        max_distance_threshold = 2.0  # Maximum allowed distance from beehive center
            
        for i, dot in enumerate(landscape.objects.red_dots):
            x, y = dot.position
            # Check distance to beehive center
            dist_to_hive = distance((x, y), movement_beehive_position)
            is_close_enough = dist_to_hive <= max_distance_threshold
                
            # Only print warnings if bees aren't close enough
            if not is_close_enough:
                all_returned = False
            
        return all_returned
    
    # Add this near the beginning of the update function to reduce update frequency:
    static_values = {
        'last_debug_frame': 0,
        'last_nectar_debug': 0
    }
    
    # Define animation update function that updates both displays
    def update(frame):
        global SIMULATION_COMPLETE
        
        nonlocal last_nectar_count, is_nectar_exhausted, nectar_cycle_count
        nonlocal waiting_for_next_cycle, cycle_complete_time, total_nectar_collected
        nonlocal landscape
        nonlocal bee_comb_positions, bee_entrance_animations, bees_in_hive_prev, bees_in_hive_current
        nonlocal all_artists, ani
        
        # Get real elapsed time for accurate timing
        elapsed_time = time.time() - start_time
        formatted_time = f"{elapsed_time:.1f}"
        
        # If simulation is complete, don't update anything - stop everything
        if SIMULATION_COMPLETE:
            # Just return all_artists to keep the display but stop updates
            return all_artists
        
        # Track timing to reduce debug frequency
        show_debug = False
        if frame - static_values['last_debug_frame'] >= 50:  # Only show debug every 50 frames
            show_debug = True
            static_values['last_debug_frame'] = frame
        
        # Update the queen-drone-baby simulation
        queen_drone_sim_complete = update_queen_drone_simulation()
        
        # Set max_timesteps from user input (only on first frame)
        if frame == 0 and hasattr(update_queen_drone_simulation, 'max_timesteps'):
            # Get the current value before we change it
            original_value = update_queen_drone_simulation.max_timesteps
            
            # Set the custom max_timesteps value from user input
            update_queen_drone_simulation.max_timesteps = max_timesteps
            
            # Print confirmation that we've changed the value
            print(f"✅ Overriding default simulation timesteps: {original_value} → {max_timesteps}")
        
        # If the queen-drone simulation is complete, stop the entire animation
        if queen_drone_sim_complete:
            print(f"\n🏁 SIMULATION COMPLETE: Queen-drone simulation reached {max_timesteps} timesteps.")
            print(f"Total nectar collected: {total_nectar_collected + landscape.movement.gold_collected}")
            print(f"Total simulation time: {formatted_time} seconds")
            
            # Set global simulation_complete flag
            SIMULATION_COMPLETE = True
            
            # Force all movement to stop
            if hasattr(landscape, 'movement'):
                landscape.movement.completed = True
                # Make all bees stop moving
                for dot in landscape.objects.red_dots:
                    if hasattr(dot, 'velocity'):
                        dot.velocity = (0, 0)
                    if hasattr(dot, 'target'):
                        dot.target = None
            
            # Update the timestamp to show completion
            timestamp_text.set_text(f"Time: {formatted_time} seconds - SIMULATION COMPLETE")
            
            return all_artists
        
        # Add queen, drone, and baby bee markers to all_artists for animation
        # Import the visualization simulation data to access the markers
        if hasattr(update_queen_drone_simulation, 'frame_counter'):
            from visualization.hive_view import create_beehive_visualization
            if hasattr(create_beehive_visualization, 'simulation_data'):
                data = create_beehive_visualization.simulation_data
                
                # Add queen marker
                if hasattr(data['queen_marker'], 'circle') and data['queen_marker'].circle not in all_artists:
                    all_artists.append(data['queen_marker'].circle)
                
                # Add drone markers
                for drone_marker in data['drone_markers']:
                    if hasattr(drone_marker, 'circle') and drone_marker.circle not in all_artists:
                        all_artists.append(drone_marker.circle)
                
                # Add gold dots (baby bees)
                for gold_dot in data['gold_dots']:
                    if gold_dot not in all_artists:
                        all_artists.append(gold_dot)
        
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
                
                return all_artists
        
        # Check for completion directly
        simulation_should_complete = check_simulation_completed(frame)
        movement_completed = hasattr(landscape.movement, 'completed') and landscape.movement.completed
        
        # Log the completion status
        if frame % 20 == 0 and show_debug:  # Only log every 20 frames AND when debug is enabled
            # Simplified logging to reduce output
            print(f"[STATUS] Frame {frame} - Bees in comb view: {len(bees_in_hive_current)} of {len(landscape.objects.red_dots)}")
            
        if (simulation_should_complete or movement_completed) and not waiting_for_next_cycle:
            # Cycle is complete, enter waiting state
            print(f"\n🍯 NECTAR CYCLE {nectar_cycle_count} COMPLETED with {landscape.movement.gold_collected} nectar")
            print(f"Total nectar so far: {total_nectar_collected + landscape.movement.gold_collected}")
            
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
            
            # Keep track of which bees are currently in the hive
            bees_in_hive_current = set()
            
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
                    
                    # Set visibility and position based on bee location
                    if near_hive or is_settled:
                        # The bee is in/near the hive, make it visible in the beehive visualization
                        circle_markers[i].show()
                        
                        # Add to current bees in hive set
                        bees_in_hive_current.add(i)
                        
                        # Check if this is a new bee entering the hive
                        bee_just_entered = i not in bees_in_hive_prev
                        
                        if bee_just_entered or i not in bee_comb_positions:
                            # Bee just entered the hive, assign a random position in the comb
                            # Use much more conservative values - only use the central area of the comb
                            # Avoid edges completely by using a smaller range
                            central_cols = max(4, COLS - 4)  # Ensure we have at least some columns
                            central_rows = max(2, ROWS - 2)  # Ensure we have at least some rows
                            
                            # Use only the central portion of the comb
                            random_col = random.randint(2, central_cols)
                            random_row = random.randint(1, central_rows)
                            
                            # Calculate position coordinates - apply a scaling factor to ensure bees stay central
                            # Scale coordinates to be more centralized
                            comb_x = (COLS / 2) + (random_col - central_cols/2) * 0.8 * OFFSET_X
                            comb_y = (ROWS / 2) + (random_row - central_rows/2) * 0.8 * OFFSET_Y
                            
                            # Minimal randomness within cells to avoid edge issues
                            comb_x += random.uniform(-0.1, 0.1)
                            comb_y += random.uniform(-0.1, 0.1)
                            
                            # Very strict safety check to ensure coordinates are well within bounds
                            # Force coordinates to be at least 2 units away from any edge
                            edge_margin = 2
                            comb_x = max(edge_margin, min(comb_x, COLS * OFFSET_X - edge_margin))
                            comb_y = max(edge_margin, min(comb_y, ROWS * OFFSET_Y - edge_margin))
                            
                            # Store this position
                            bee_comb_positions[i] = (comb_x, comb_y)
                            
                            # Clear debug log of new bee
                            debug_bee_position(f"INITIAL ASSIGNMENT - Central cell [{random_col},{random_row}] assigned to position ({comb_x:.2f}, {comb_y:.2f})", 
                                              bee_index=i, level="INFO")
                            
                            # Start an entrance animation - determine which edge to start from based on
                            # the bee's position in the landscape
                            landscape_x, landscape_y = red_dot.position
                            
                            # Determine which side of the hive the bee is coming from
                            dx = landscape_x - hive_x
                            dy = landscape_y - hive_y
                            
                            # Start position at the edge of the comb but slightly inward
                            edge_inset = 2  # Stay 2 units away from the actual edge
                            if abs(dx) > abs(dy):  # Coming from left or right
                                if dx > 0:  # Coming from right
                                    start_x = COLS * OFFSET_X - edge_inset  # Right edge (inset)
                                else:  # Coming from left
                                    start_x = edge_inset  # Left edge (inset)
                                start_y = comb_y  # Same y-level as target
                            else:  # Coming from top or bottom
                                if dy > 0:  # Coming from top
                                    start_y = ROWS * OFFSET_Y - edge_inset  # Top edge (inset)
                                else:  # Coming from bottom
                                    start_y = edge_inset  # Bottom edge (inset)
                                start_x = comb_x  # Same x-level as target
                            
                            # Start the animation
                            bee_entrance_animations[i] = (comb_x, comb_y, start_x, start_y, 0.0)
                            
                            # More detailed debug information
                            print(f"🐝 Bee #{i+1} entering hive from edge! Target: [{random_col},{random_row}] → Pos: ({comb_x:.2f}, {comb_y:.2f})")
                        
                        # Check if this bee is in an entrance animation
                        if i in bee_entrance_animations:
                            # Get animation parameters
                            target_x, target_y, start_x, start_y, progress = bee_entrance_animations[i]
                            
                            # Increment progress
                            progress += 0.05  # Adjust this for faster/slower animation
                            
                            if progress >= 1.0:
                                # Animation complete
                                beehive_x, beehive_y = bee_comb_positions[i]
                                
                                # Safety check with even stricter bounds
                                edge_margin = 2
                                if not (edge_margin < beehive_x < COLS * OFFSET_X - edge_margin and 
                                        edge_margin < beehive_y < ROWS * OFFSET_Y - edge_margin):
                                    debug_bee_position(f"Position too close to edge! Moving to center.", 
                                                      bee_index=i, position=f"({beehive_x:.2f}, {beehive_y:.2f})", level="WARNING")
                                    
                                    # Force to center area
                                    beehive_x = COLS * OFFSET_X / 2 + random.uniform(-3, 3)
                                    beehive_y = ROWS * OFFSET_Y / 2 + random.uniform(-2, 2)
                                    # Update the stored position
                                    bee_comb_positions[i] = (beehive_x, beehive_y)
                                    
                                    debug_bee_position(f"Repositioned to center", 
                                                      bee_index=i, position=f"({beehive_x:.2f}, {beehive_y:.2f})", level="SUCCESS")
                                
                                del bee_entrance_animations[i]
                                debug_bee_position(f"Entrance animation complete", 
                                                  bee_index=i, position=f"({beehive_x:.2f}, {beehive_y:.2f})", level="SUCCESS")
                            else:
                                # Continue animation - linear interpolation
                                beehive_x = start_x + (target_x - start_x) * progress
                                beehive_y = start_y + (target_y - start_y) * progress
                                
                                # Update animation state
                                bee_entrance_animations[i] = (target_x, target_y, start_x, start_y, progress)
                        else:
                            # Use the stored random position for this bee
                            beehive_x, beehive_y = bee_comb_positions[i]
                            
                            # Extra safety check for existing positions
                            edge_margin = 2
                            if not (edge_margin < beehive_x < COLS * OFFSET_X - edge_margin and 
                                    edge_margin < beehive_y < ROWS * OFFSET_Y - edge_margin):
                                debug_bee_position(f"Position too close to edge! Moving to center", 
                                                 bee_index=i, position=f"({beehive_x:.2f}, {beehive_y:.2f})", level="ERROR")
                                
                                # Force to center area
                                beehive_x = COLS * OFFSET_X / 2 + random.uniform(-3, 3)
                                beehive_y = ROWS * OFFSET_Y / 2 + random.uniform(-2, 2)
                                # Update the stored position
                                bee_comb_positions[i] = (beehive_x, beehive_y)
                                
                                debug_bee_position(f"Repositioned to center", 
                                                 bee_index=i, position=f"({beehive_x:.2f}, {beehive_y:.2f})", level="SUCCESS")
                            
                            # For settled bees, we might want to position them differently
                            # But only if they're safely positioned away from edges
                            if is_settled and random.random() < 0.03:  # 3% chance to move a little
                                # Occasionally move the settled bee a tiny bit to simulate movement in the hive
                                # Use very small movements to avoid edge issues
                                new_x = beehive_x + random.uniform(-0.08, 0.08) 
                                new_y = beehive_y + random.uniform(-0.08, 0.08)
                                
                                # Safety check to make sure the new position is still valid
                                if (edge_margin < new_x < COLS * OFFSET_X - edge_margin and 
                                    edge_margin < new_y < ROWS * OFFSET_Y - edge_margin):
                                    bee_comb_positions[i] = (new_x, new_y)
                                    beehive_x, beehive_y = new_x, new_y
                        
                        # Final position check before moving the bee
                        if not (0 < beehive_x < COLS * OFFSET_X and 0 < beehive_y < ROWS * OFFSET_Y):
                            debug_bee_position(f"CRITICAL - Position completely outside bounds!", 
                                              bee_index=i, position=f"({beehive_x:.2f}, {beehive_y:.2f})", level="ERROR")
                            # Force to absolute center
                            beehive_x, beehive_y = COLS * OFFSET_X / 2, ROWS * OFFSET_Y / 2
                            bee_comb_positions[i] = (beehive_x, beehive_y)
                        
                        # Move the bee marker to the assigned position
                        circle_markers[i].move(beehive_x, beehive_y)
                        
                        if frame % 60 == 0 and show_debug:  # Reduce spam - once every 60 frames and only when debug is on
                            print(f"[DEBUG] Bee #{i+1} is in hive at comb position ({beehive_x:.2f}, {beehive_y:.2f})")
                    else:
                        # The bee is not in the hive, hide it in the beehive visualization
                        circle_markers[i].hide()
                        
                        if frame % 60 == 0 and show_debug:  # Reduce spam - once every 60 frames and only when debug is on
                            print(f"[DEBUG] Bee #{i+1} is outside hive at {red_dot.position}")
                    
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
            
            # Update which bees were in the hive for the next frame
            bees_in_hive_prev = bees_in_hive_current.copy()
        
        # Always return the same list of artists to prevent blinking
        return all_artists
    
    try:
        # Create a combined animation with a very large number of frames to ensure it doesn't stop
        ani = animation.FuncAnimation(
            fig, 
            update, 
            frames=999999,  # Keep this at a large value - separate from max_timesteps
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