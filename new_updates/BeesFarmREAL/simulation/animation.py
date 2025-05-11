import time
import random
from simulation.simulation_config import SIMULATION_COMPLETE, COLS, ROWS, OFFSET_X, OFFSET_Y, WAIT_BETWEEN_CYCLES
from simulation.utils import distance, debug_bee_position, check_simulation_completed
from utils.helpers import regenerate_nectar

class AnimationHandler:
    def __init__(self, landscape, circle_markers, triangle_markers, square_markers, 
                 hexagon_grid, bee_status, timestamp_text, nectar_status, 
                 bee_sizes_text, total_nectar_text, total_box, screenshot_manager=None,
                 target_timesteps=None):
        
        self.landscape = landscape
        self.circle_markers = circle_markers
        self.triangle_markers = triangle_markers
        self.square_markers = square_markers
        self.hexagon_grid = hexagon_grid
        self.bee_status = bee_status
        self.timestamp_text = timestamp_text
        self.nectar_status = nectar_status
        self.bee_sizes_text = bee_sizes_text
        self.total_nectar_text = total_nectar_text
        self.total_box = total_box
        self.screenshot_manager = screenshot_manager
        
        # Store the original target timesteps for reporting
        self.target_timesteps = target_timesteps or landscape.max_timesteps
        
        # Start time tracking
        self.start_time = time.time()
        
        # Create a list of all artists for blitting
        self.all_artists = self.create_artist_list()
        
        # Initialize tracking variables
        self.last_nectar_count = 0
        self.is_nectar_exhausted = False
        self.nectar_cycle_count = 1
        self.total_nectar_collected = 0
        self.waiting_for_next_cycle = False
        self.cycle_complete_time = None
        
        # Initialize bee tracking variables together
        self.bee_comb_positions = {}  # Dictionary to store bee positions in the comb
        self.bee_entrance_animations = {}  # {bee_index: (target_x, target_y, progress)}
        self.bees_in_hive_prev = set()  # Track which bees were previously in the hive
        self.bees_in_hive_current = set()  # Track which bees are currently in the hive
        
        # Debug tracking
        self.static_values = {
            'last_debug_frame': 0,
            'last_nectar_debug': 0
        }
    
    def create_artist_list(self):
        all_artists = []
        
        # First, add all hexagon patches
        for row in self.hexagon_grid:
            for hex_patch in row:
                all_artists.append(hex_patch)
        
        # Add all marker objects
        for marker in self.circle_markers:
            if marker.circle:
                all_artists.append(marker.circle)
        
        for marker in self.triangle_markers:
            if marker.triangle:
                all_artists.append(marker.triangle)
                
        for marker in self.square_markers:
            if marker.rectangle:
                all_artists.append(marker.rectangle)
        
        # Add text elements
        all_artists.append(self.timestamp_text)
        all_artists.append(self.nectar_status)
        all_artists.append(self.bee_sizes_text)
        all_artists.append(self.bee_status)
        all_artists.append(self.total_nectar_text)
        all_artists.append(self.total_box)  # Add the background box for total nectar
        
        return all_artists
        
    def update(self, frame):
        global SIMULATION_COMPLETE
        
        # Get real elapsed time for accurate timing
        elapsed_time = time.time() - self.start_time
        formatted_time = f"{elapsed_time:.1f}"
        
        # If simulation is complete, don't update anything - stop everything
        if SIMULATION_COMPLETE:
            # Stop screenshot timer if it exists
            if self.screenshot_manager:
                self.screenshot_manager.stop_timer()
            # Just return all_artists to keep the display but stop updates
            return self.all_artists
        
        # Track timing to reduce debug frequency
        show_debug = False
        if frame - self.static_values['last_debug_frame'] >= 50:  # Only show debug every 50 frames
            show_debug = True
            self.static_values['last_debug_frame'] = frame
        
        # Update the queen-drone-baby simulation
        from visualization.hive_view import update_queen_drone_simulation
        queen_drone_sim_complete = update_queen_drone_simulation()
        
        # Set max_timesteps from user input (only on first frame)
        if frame == 0 and hasattr(update_queen_drone_simulation, 'max_timesteps'):
            # Get the current value before we change it
            original_value = update_queen_drone_simulation.max_timesteps
            
            # Set the custom max_timesteps value from user input
            update_queen_drone_simulation.max_timesteps = self.landscape.max_timesteps
            
            # Print confirmation that we've changed the value
            print(f"✅ Overriding default simulation timesteps: {original_value} → {self.landscape.max_timesteps}")
        
        # If the queen-drone simulation is complete, stop the entire animation
        if queen_drone_sim_complete:
            print(f"\n🏁 QUEEN-DRONE SIMULATION COMPLETE: Reached {self.target_timesteps} timesteps")
            print(f"Total nectar collected: {self.total_nectar_collected + self.landscape.movement.gold_collected}")
            print(f"Total simulation time: {formatted_time} seconds")
            
            # Set global simulation_complete flag
            SIMULATION_COMPLETE = True
            
            # Force all movement to stop
            if hasattr(self.landscape, 'movement'):
                self.landscape.movement.completed = True
                # Make all bees stop moving
                for dot in self.landscape.objects.red_dots:
                    if hasattr(dot, 'velocity'):
                        dot.velocity = (0, 0)
                    if hasattr(dot, 'target'):
                        dot.target = None
            
            # Update the timestamp to show completion
            self.timestamp_text.set_text(f"Time: {formatted_time} seconds - SIMULATION COMPLETE")
            
            # Stop screenshot timer if it exists
            if self.screenshot_manager:
                self.screenshot_manager.stop_timer()
                
            return self.all_artists
        
        # Add queen, drone, and baby bee markers to all_artists for animation
        # Import the visualization simulation data to access the markers
        if hasattr(update_queen_drone_simulation, 'frame_counter'):
            from visualization.hive_view import create_beehive_visualization
            if hasattr(create_beehive_visualization, 'simulation_data'):
                data = create_beehive_visualization.simulation_data
                
                # Add queen marker
                if hasattr(data['queen_marker'], 'circle') and data['queen_marker'].circle not in self.all_artists:
                    self.all_artists.append(data['queen_marker'].circle)
                
                # Add drone markers
                for drone_marker in data['drone_markers']:
                    if hasattr(drone_marker, 'circle') and drone_marker.circle not in self.all_artists:
                        self.all_artists.append(drone_marker.circle)
                
                # Add gold dots (baby bees)
                for gold_dot in data['gold_dots']:
                    if gold_dot not in self.all_artists:
                        self.all_artists.append(gold_dot)
        
        # If we're in the waiting period between cycles
        if self.waiting_for_next_cycle:
            wait_time_elapsed = time.time() - self.cycle_complete_time
            remaining_wait = WAIT_BETWEEN_CYCLES - wait_time_elapsed
            
            if remaining_wait > 0:
                # Still waiting, update the status text
                self.timestamp_text.set_text(f"Time: {formatted_time} seconds (Next cycle in {remaining_wait:.1f}s)")
                return self.all_artists
            else:
                # Waiting period is over, regenerate nectar
                print(f"\n⏰ Waiting period complete. Regenerating nectar for cycle {self.nectar_cycle_count}...")
                self.waiting_for_next_cycle = False
                
                # Add current nectar count to total before regenerating
                self.total_nectar_collected += self.landscape.movement.gold_collected
                
                # Print the accumulated nectar information for debugging
                print(f"\n🍯 TOTAL NECTAR ACCUMULATED: {self.total_nectar_collected} (after cycle {self.nectar_cycle_count})")
                print(f"    This should make the honeycomb visibly darker now")
                
                # Regenerate nectar and reset for the next cycle
                self.nectar_cycle_count += 1
                self.landscape, total_nectar = regenerate_nectar(self.landscape, self.nectar_cycle_count, self.total_nectar_collected)
                
                # Reset tracking variables for this cycle
                self.is_nectar_exhausted = False
                self.last_nectar_count = 0
                
                # Update display to show the new cycle and total
                gold_collected = self.landscape.movement.gold_collected
                
                # Update nectar visualization with the total nectar (accumulated so far)
                from visualization.hive_view import update_nectar_level
                update_nectar_level(
                    self.hexagon_grid, 
                    gold_collected,                  # Current cycle's nectar (0 at start)
                    self.landscape.max_gold_collected,    # Max nectar per cycle
                    self.total_nectar_collected,          # Total nectar accumulated so far
                    self.nectar_cycle_count,              # Current cycle 
                    self.nectar_status
                )
                
                # Update the total counter
                self.total_nectar_text.set_text(f"TOTAL NECTAR: {self.total_nectar_collected}")
                
                # Reset circle markers to match refreshed bee attributes
                for i, red_dot in enumerate(self.landscape.objects.red_dots):
                    if i < len(self.circle_markers) and hasattr(red_dot, 'current_size'):
                        # Reset circle size to normal
                        self.circle_markers[i].radius = red_dot.current_size
                        if self.circle_markers[i].circle:
                            self.circle_markers[i].circle.set_radius(red_dot.current_size)
                            # Reset color to normal red
                            self.circle_markers[i].circle.set_facecolor('red')
                
                # Reset bee size text
                self.bee_sizes_text.set_text("Bee Growth: Normal")
                
                return self.all_artists
        
        # Check for completion directly
        simulation_should_complete = check_simulation_completed(frame, self.landscape)
        movement_completed = hasattr(self.landscape.movement, 'completed') and self.landscape.movement.completed
        
        # Log the completion status
        if frame % 20 == 0 and show_debug:  # Only log every 20 frames AND when debug is enabled
            # Simplified logging to reduce output
            print(f"[STATUS] Frame {frame} - Bees in comb view: {len(self.bees_in_hive_current)} of {len(self.landscape.objects.red_dots)}")
            
        if (simulation_should_complete or movement_completed) and not self.waiting_for_next_cycle:
            # Cycle is complete, enter waiting state
            print(f"\n🍯 NECTAR CYCLE {self.nectar_cycle_count} COMPLETED with {self.landscape.movement.gold_collected} nectar")
            print(f"Total nectar so far: {self.total_nectar_collected + self.landscape.movement.gold_collected}")
            
            self.waiting_for_next_cycle = True
            self.cycle_complete_time = time.time()
            
            # Update text to show waiting status
            self.timestamp_text.set_text(f"Time: {formatted_time} seconds (Next cycle in {WAIT_BETWEEN_CYCLES:.1f}s)")
            return self.all_artists
        
        # Update landscape simulation
        if self.landscape.movement:
            self.landscape.movement.update_state()
            
            # Get current nectar collection count
            gold_collected = self.landscape.movement.gold_collected
            
            # Only update visual elements if nectar count changed
            if gold_collected != self.last_nectar_count or not self.is_nectar_exhausted:
                # Use our new nectar update function with total nectar and cycle information
                from visualization.hive_view import update_nectar_level
                update_nectar_level(
                    self.hexagon_grid, 
                    gold_collected,                  # Current cycle's nectar
                    self.landscape.max_gold_collected,    # Max nectar per cycle
                    self.total_nectar_collected + gold_collected,  # Total nectar (previous + current)
                    self.nectar_cycle_count,              # Current cycle 
                    self.nectar_status
                )
                
                # Update total nectar text
                self.total_nectar_text.set_text(f"TOTAL NECTAR: {self.total_nectar_collected + gold_collected}")
                self.last_nectar_count = gold_collected
                
                # Check if nectar is exhausted
                if gold_collected >= self.landscape.max_gold_collected:
                    self.is_nectar_exhausted = True
                    print(f"[DEBUG] Nectar target reached ({gold_collected}/{self.landscape.max_gold_collected}), checking for completion...")
            
            # Always update timestamp and bee positions (unless we're waiting for next cycle)
            if not self.waiting_for_next_cycle:
                self.timestamp_text.set_text(f"Time: {formatted_time} seconds")
            
            # Track bee sizes for reporting
            bee_size_changes = False
            max_bee_size = 0.1  # Default bee size
            
            # Get the beehive position for checking if bees are in/near the hive
            hive_x, hive_y = self.landscape.objects.beehive["position"]
            hive_width = self.landscape.objects.beehive["width"]
            hive_height = self.landscape.objects.beehive["height"]
            
            # Beehive position from movement logic
            movement_beehive_position = self.landscape.movement.beehive_position
            
            # Keep track of which bees are currently in the hive
            self.bees_in_hive_current = set()
            
            # Update circle marker positions to match red dots
            for i, red_dot in enumerate(self.landscape.objects.red_dots):
                if i < len(self.circle_markers):
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
                    is_settled = i in self.landscape.movement.settled_dots
                    
                    # Set visibility and position based on bee location
                    if near_hive or is_settled:
                        self._handle_bee_in_hive(i, red_dot, frame, show_debug)
                    else:
                        # The bee is not in the hive, hide it in the beehive visualization
                        self.circle_markers[i].hide()
                        
                        if frame % 60 == 0 and show_debug:  # Reduce spam - once every 60 frames and only when debug is on
                            print(f"[DEBUG] Bee #{i+1} is outside hive at {red_dot.position}")
                    
                    # Update the size of the circle based on silver dot interactions
                    self._update_bee_size(i, red_dot, max_bee_size)
            
            # Update the bee sizes text
            if max_bee_size > 0.1:
                self.bee_sizes_text.set_text(f"Bee Growth: {int((max_bee_size/0.1 - 1) * 100)}% Larger")
            else:
                self.bee_sizes_text.set_text("Bee Growth: Normal")
            
            # Update which bees were in the hive for the next frame
            self.bees_in_hive_prev = self.bees_in_hive_current.copy()
        
        # Always return the same list of artists to prevent blinking
        return self.all_artists
        
    def _handle_bee_in_hive(self, i, red_dot, frame, show_debug):
        # The bee is in/near the hive, make it visible in the beehive visualization
        self.circle_markers[i].show()
        
        # Add to current bees in hive set
        self.bees_in_hive_current.add(i)
        
        # Check if this is a new bee entering the hive
        bee_just_entered = i not in self.bees_in_hive_prev
        
        if bee_just_entered or i not in self.bee_comb_positions:
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
            self.bee_comb_positions[i] = (comb_x, comb_y)
            
            # Clear debug log of new bee
            debug_bee_position(f"INITIAL ASSIGNMENT - Central cell [{random_col},{random_row}] assigned to position ({comb_x:.2f}, {comb_y:.2f})", 
                              bee_index=i, level="INFO")
            
            # Start an entrance animation - determine which edge to start from based on
            # the bee's position in the landscape
            landscape_x, landscape_y = red_dot.position
            
            # Get the beehive position for determining entrance
            hive_x, hive_y = self.landscape.objects.beehive["position"]
            
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
            self.bee_entrance_animations[i] = (comb_x, comb_y, start_x, start_y, 0.0)
            
            # More detailed debug information
            print(f"🐝 Bee #{i+1} entering hive from edge! Target: [{random_col},{random_row}] → Pos: ({comb_x:.2f}, {comb_y:.2f})")
        
        # Check if this bee is in an entrance animation
        if i in self.bee_entrance_animations:
            # Get animation parameters
            target_x, target_y, start_x, start_y, progress = self.bee_entrance_animations[i]
            
            # Increment progress
            progress += 0.05  # Adjust this for faster/slower animation
            
            if progress >= 1.0:
                # Animation complete
                beehive_x, beehive_y = self.bee_comb_positions[i]
                
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
                    self.bee_comb_positions[i] = (beehive_x, beehive_y)
                    
                    debug_bee_position(f"Repositioned to center", 
                                      bee_index=i, position=f"({beehive_x:.2f}, {beehive_y:.2f})", level="SUCCESS")
                
                del self.bee_entrance_animations[i]
                debug_bee_position(f"Entrance animation complete", 
                                  bee_index=i, position=f"({beehive_x:.2f}, {beehive_y:.2f})", level="SUCCESS")
            else:
                # Continue animation - linear interpolation
                beehive_x = start_x + (target_x - start_x) * progress
                beehive_y = start_y + (target_y - start_y) * progress
                
                # Update animation state
                self.bee_entrance_animations[i] = (target_x, target_y, start_x, start_y, progress)
        else:
            # Use the stored random position for this bee
            beehive_x, beehive_y = self.bee_comb_positions[i]
            
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
                self.bee_comb_positions[i] = (beehive_x, beehive_y)
                
                debug_bee_position(f"Repositioned to center", 
                                 bee_index=i, position=f"({beehive_x:.2f}, {beehive_y:.2f})", level="SUCCESS")
            
            # For settled bees, we might want to position them differently
            # But only if they're safely positioned away from edges
            is_settled = i in self.landscape.movement.settled_dots
            if is_settled and random.random() < 0.03:  # 3% chance to move a little
                # Occasionally move the settled bee a tiny bit to simulate movement in the hive
                # Use very small movements to avoid edge issues
                new_x = beehive_x + random.uniform(-0.08, 0.08) 
                new_y = beehive_y + random.uniform(-0.08, 0.08)
                
                # Safety check to make sure the new position is still valid
                if (edge_margin < new_x < COLS * OFFSET_X - edge_margin and 
                    edge_margin < new_y < ROWS * OFFSET_Y - edge_margin):
                    self.bee_comb_positions[i] = (new_x, new_y)
                    beehive_x, beehive_y = new_x, new_y
        
        # Final position check before moving the bee
        if not (0 < beehive_x < COLS * OFFSET_X and 0 < beehive_y < ROWS * OFFSET_Y):
            debug_bee_position(f"CRITICAL - Position completely outside bounds!", 
                              bee_index=i, position=f"({beehive_x:.2f}, {beehive_y:.2f})", level="ERROR")
            # Force to absolute center
            beehive_x, beehive_y = COLS * OFFSET_X / 2, ROWS * OFFSET_Y / 2
            self.bee_comb_positions[i] = (beehive_x, beehive_y)
        
        # Move the bee marker to the assigned position
        self.circle_markers[i].move(beehive_x, beehive_y)
        
        if frame % 60 == 0 and show_debug:  # Reduce spam - once every 60 frames and only when debug is on
            print(f"[DEBUG] Bee #{i+1} is in hive at comb position ({beehive_x:.2f}, {beehive_y:.2f})")
            
    def _update_bee_size(self, i, red_dot, max_bee_size):
        if hasattr(red_dot, 'current_size'):
            current_max_bee_size = max(max_bee_size, red_dot.current_size)
            
            if red_dot.current_size != self.circle_markers[i].radius:
                # Create a new circle with the updated size
                if self.circle_markers[i].circle:
                    self.circle_markers[i].radius = red_dot.current_size
                    self.circle_markers[i].circle.set_radius(red_dot.current_size)
                    
                    # Also change color to indicate the increased power
                    intensity = (red_dot.current_size - 0.1) / 0.25  # Normalize to 0-1 range
                    new_color = (1.0, max(0, 1.0 - intensity), max(0, 1.0 - intensity))  # Red to more saturated red
                    self.circle_markers[i].circle.set_facecolor(new_color)
            
            return current_max_bee_size
        return max_bee_size 