import matplotlib.pyplot as plt
import random
import numpy as np
from comb.Classhive import CircleMarker, hexagon
from comb import QueenBeeDot, DroneDot
from utils.constants import HEX_SIZE, COLS, ROWS, OFFSET_X, OFFSET_Y

def create_beehive_view(fig, gs, worker_bee_count, drone_bees=4):
    """
    Create the beehive visualization.
    
    Parameters:
    - fig: Figure to use
    - gs: GridSpec to use
    - worker_bee_count: Number of worker bees
    - drone_bees: Number of drone bees for the queen-drone simulation (default: 4)
    """
    # Use our new visualization function from comb/Beehive.py
    ax, hexagon_grid, circle_markers, nectar_status, bee_status = create_beehive_visualization(
        fig=fig,
        subplot=gs[0, 0],
        worker_bees=worker_bee_count,
        max_nectar=20,  # Maximum nectar per cycle
        drone_bees=drone_bees  # Number of drone bees
    )
    
    # Position text in the extra space below the hexagons (data coordinates)
    # Add status text for bee sizes at the top
    max_x = COLS * OFFSET_X
    max_y = ROWS * OFFSET_Y + OFFSET_Y/2
    
    # Better vertical spacing between text elements
    bee_sizes_text = ax.text(max_x/2, -1.5, "Bee Growth: Normal", 
                          color='purple', fontweight='bold', fontsize=12,
                          horizontalalignment='center')
    
    timestamp_text = ax.text(max_x/2, -5, "Time: 0.0 seconds", fontsize=12,
                          horizontalalignment='center', bbox=dict(facecolor='white', alpha=0.7, pad=2))
    
    # Create a box for the total counter
    total_box = plt.Rectangle((0, -9), max_x, 1.3, facecolor='honeydew', 
                            edgecolor='forestgreen', alpha=0.8, transform=ax.transData)
    ax.add_patch(total_box)
    
    # Add the prominent text for total nectar
    total_nectar_text = ax.text(max_x/2, -8.5, "Total Nectar: 0", 
                            color='darkgreen', fontweight='bold', fontsize=16,
                            horizontalalignment='center', verticalalignment='center')
    
    # Store timestamp_text in the simulation data if it exists
    if hasattr(create_beehive_visualization, 'simulation_data') and drone_bees > 0:
        create_beehive_visualization.simulation_data['timestamp_text'] = timestamp_text
    
    # Create empty placeholder lists for compatibility with existing code
    triangle_markers = []
    square_markers = []
    
    return ax, circle_markers, triangle_markers, square_markers, hexagon_grid, bee_status, timestamp_text, nectar_status, bee_sizes_text, total_nectar_text, total_box


def create_beehive_visualization(worker_bees=3, drone_bees=3, max_nectar=20, fig=None, subplot=None):
    """
    Creates a simplified beehive visualization with:
    - A hexagonal grid representing the honeycomb
    - Only the bees represented as red circles
    - Starting with a light color to show absence of nectar
    
    Parameters:
    - worker_bees: number of worker bees to show
    - drone_bees: number of drone bees to show (queen-drone simulation)
    - max_nectar: maximum nectar that can be collected per cycle (for coloring)
    - fig: existing figure to use (if None, creates a new one)
    - subplot: subplot specification (if None, creates a new figure)
    
    Returns axes, hexagon_patches, bee_markers, nectar_status, and bee_status for later updates
    """
    # Set up the figure and axes
    if fig is None or subplot is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        ax = fig.add_subplot(subplot)
        
    ax.set_aspect('equal')
    ax.axis('off')  # Turn off all axes, spines, and ticks
    
    # Set extended limits with extra padding at bottom for text - match original
    max_x = COLS * OFFSET_X
    max_y = ROWS * OFFSET_Y + OFFSET_Y/2
    ax.set_xlim(-1, max_x + 1)
    ax.set_ylim(-9, max_y + 1)  # Match original bottom space
    
    # Add title for the visualization
    title = ax.set_title("Beehive Visualization", fontsize=14, pad=15)
    
    # Position text in the original positions - more vertical space between them
    nectar_status = ax.text(max_x/2, -6.5, "Nectar in Hive: 0", 
                         color='darkorange', fontweight='bold', fontsize=12,
                         horizontalalignment='center', bbox=dict(facecolor='white', alpha=0.7, pad=2))
    
    # Initialize status text with worker bee count
    status_text = f"Worker Bees: {worker_bees}"
    
    # Add drone information if drones are included
    if drone_bees > 0:
        status_text = f"Worker Bees: {worker_bees} | Queen & {drone_bees} Drones (0 Babies)"
    
    # Create the bee status text with bold formatting and slightly larger font
    # Moved up to prevent overlap with other text
    bee_status = ax.text(max_x/2, -3.5, status_text, 
                       color='red', fontweight='bold', fontsize=13,
                       horizontalalignment='center', bbox=dict(facecolor='white', alpha=0.7, pad=3))
    
    # Draw hexagons to form the honeycomb - starting with very light color
    # to show absence of nectar
    hexagon_grid = []
    for row in range(ROWS):
        row_hexagons = []
        for col in range(COLS):
            x = col * OFFSET_X
            y = row * OFFSET_Y
            
            # Stagger odd columns
            if col % 2 == 1:
                y += OFFSET_Y / 2
                
            x_hexagon, y_hexagon = hexagon(x, y, HEX_SIZE)
            # Starting color: extremely light - almost white with just a hint of honey
            patch = ax.fill(x_hexagon, y_hexagon, edgecolor="black", 
                          facecolor=(1.0, 0.99, 0.95, 0.4), lw=1)[0]
            row_hexagons.append(patch)
        hexagon_grid.append(row_hexagons)
    
    # Create bee markers (initial positions don't matter - will be updated)
    circle_markers = []
    for _ in range(worker_bees):
        # Random initial position near edge of comb
        x = random.uniform(0, max_x)
        y = random.uniform(0, max_y/4)  # Start at bottom quarter
        
        # Create a marker representing a bee
        circle_marker = CircleMarker(x, y, radius=0.1, color='red')  # Match original radius
        circle_marker.plot(ax)
        # Initially hide the markers since bees start outside the hive
        circle_marker.hide()
        circle_markers.append(circle_marker)

    # queen-baby-drone simulation
    if drone_bees > 0:
        print("👑🐝 QUEEN-DRONE DEBUG: Initializing queen-drone simulation with", drone_bees, "drones")
        
        # Store these for later updates in the simulation
        if not hasattr(create_beehive_visualization, 'simulation_data'):
            create_beehive_visualization.simulation_data = {}
        
        # Create queen bee marker (blue) - start near center of the hive
        queen_bee = QueenBeeDot()
        
        # Position queen in center of hive (around 7.5, 7.5 in QueenBeeDot coordinates)
        queen_bee.position_x = 7.5 + random.uniform(-1.0, 1.0)  # Center with small variation
        queen_bee.position_y = 7.5 + random.uniform(-1.0, 1.0)
        
        # Map to beehive coordinates
        qx, qy = map_to_beehive(queen_bee.position_x, queen_bee.position_y, max_x, max_y)
        
        # If coordinates are outside the safe zone, force to center
        if not (2 < qx < max_x - 2 and 2 < qy < max_y - 2):
            qx, qy = max_x/2, max_y/2
            
        # Make queen more visible - larger and blue
        queen_marker = CircleMarker(qx, qy, radius=0.25, color='blue')  # Bigger for visibility
        queen_marker.plot(ax)
        queen_marker.show()
        
        print(f"👑 QUEEN: Created at center position {queen_bee.get_position()} -> ({qx:.1f}, {qy:.1f})")
        
        # Create drone bee markers (black)
        drones = []
        drone_markers = []
        for i in range(drone_bees):
            drone = DroneDot()
            
            # Position drones around center too, but slightly more spread out than queen
            drone.position_x = 7.5 + random.uniform(-2.0, 2.0)
            drone.position_y = 7.5 + random.uniform(-2.0, 2.0)
            
            drones.append(drone)
            
            dx, dy = map_to_beehive(drone.position_x, drone.position_y, max_x, max_y)
            drone_marker = CircleMarker(dx, dy, radius=0.15, color='black')  # Slightly bigger for visibility
            drone_marker.plot(ax)
            drone_marker.show()
            drone_markers.append(drone_marker)
            
            print(f"🐝 DRONE {i+1}: Created at center area position {drone.get_position()} -> ({dx:.1f}, {dy:.1f})")
        
        # Store the simulation data in a static variable
        simulation_data = {
            'ax': ax,
            'queen_bee': queen_bee,
            'queen_marker': queen_marker,
            'drones': drones,
            'drone_markers': drone_markers,
            'bee_status': bee_status,
            'nectar_status': nectar_status,
            'max_x': max_x,
            'max_y': max_y,
            'gold_dots': [],
            'baby_bees_count': 0,
            'interaction_radius': 1.5,
            'random_move_timer': 0
        }
        create_beehive_visualization.simulation_data = simulation_data
    
    # Return all the elements needed for later updates
    return ax, hexagon_grid, circle_markers, nectar_status, bee_status

def map_to_beehive(x, y, max_x, max_y):
    """Map coordinates from the 0-15 range to beehive coordinates"""
    mapped_x = (x / 15) * max_x
    mapped_y = (y / 20) * max_y
    return mapped_x, mapped_y

def update_queen_drone_simulation():
    """
    Update the queen and drone simulation for one timestep.
    This function uses the simulation data stored in create_beehive_visualization.simulation_data
    to update the queen-drone-baby simulation.
    
    Usage:
    ------
    Call this function in your animation or update loop to animate the queen-drone interaction.
    Example:
        def update():
            # Update worker bees, nectar, etc.
            ...
            # Update queen-drone simulation (no parameters needed)
            update_queen_drone_simulation()
            ...
            
    Returns:
    -------
    simulation_completed: Boolean indicating if the simulation has reached its time limit
    """
    # Check if simulation data exists
    if not hasattr(create_beehive_visualization, 'simulation_data'):
        print("👑🐝 QUEEN-DRONE DEBUG: No simulation data found! Queen-drone simulation not initialized.")
        return False
    
    data = create_beehive_visualization.simulation_data
    ax = data['ax']
    queen_bee = data['queen_bee']
    queen_marker = data['queen_marker']
    drones = data['drones']
    drone_markers = data['drone_markers']
    bee_status = data['bee_status']
    nectar_status = data['nectar_status']
    max_x = data['max_x']
    max_y = data['max_y']
    
    # Add a static counter to reduce log frequency and track total timesteps
    if not hasattr(update_queen_drone_simulation, 'frame_counter'):
        update_queen_drone_simulation.frame_counter = 0
        # Default to 10, but this will be overridden by user input in main.py
        update_queen_drone_simulation.max_timesteps = 10  # Initial value, can be changed
        print("👑🐝 QUEEN-DRONE DEBUG: First simulation update! Queen at", queen_bee.get_position())
        
        # Make sure they're visible with good contrast
        queen_marker.radius = 0.25  # Make queen larger for visibility
        if hasattr(queen_marker, 'circle'):
            queen_marker.circle.set_radius(0.25)
            queen_marker.circle.set_color('blue')
            queen_marker.circle.set_zorder(100)  # Ensure queen is on top
        
        for marker in drone_markers:
            marker.radius = 0.15  # Make drones visible too
            if hasattr(marker, 'circle'):
                marker.circle.set_radius(0.15)
                marker.circle.set_color('black')
                marker.circle.set_zorder(90)  # Drones below queen but above other markers
    
    update_queen_drone_simulation.frame_counter += 1
    
    # Check if we've reached the timestep limit
    if update_queen_drone_simulation.frame_counter >= update_queen_drone_simulation.max_timesteps:
        print(f"🏁 QUEEN-DRONE SIMULATION COMPLETE: Reached {update_queen_drone_simulation.frame_counter} timesteps")
        return True
    
    # Log every 50 frames to avoid console flood
    should_log = update_queen_drone_simulation.frame_counter % 50 == 0
    
    # Move queen bee - keep mostly in center region
    queen_bee.move_randomly(max_delta=0.2)
    
    # Gently nudge the queen back towards center if she wanders too far
    center_x, center_y = 7.5, 7.5
    dist_from_center = ((queen_bee.position_x - center_x)**2 + 
                         (queen_bee.position_y - center_y)**2)**0.5
    
    # If queen is too far from center, apply gentle force back toward center
    if dist_from_center > 3.0:  # Allow some movement, but not too far
        # Calculate direction vector to center
        dir_x = center_x - queen_bee.position_x
        dir_y = center_y - queen_bee.position_y
        # Normalize
        mag = (dir_x**2 + dir_y**2)**0.5
        if mag > 0:
            dir_x /= mag
            dir_y /= mag
        # Apply gentle force toward center
        queen_bee.position_x += dir_x * 0.1
        queen_bee.position_y += dir_y * 0.1
    
    # Convert to beehive coordinates
    qx, qy = map_to_beehive(queen_bee.position_x, queen_bee.position_y, max_x, max_y)
    queen_marker.move(qx, qy)
    
    if should_log:
        print(f"👑 QUEEN: Moving to ({qx:.1f}, {qy:.1f}) - Original pos: {queen_bee.get_position()}")
        print(f"⏱️ SIMULATION TIMESTEP: {update_queen_drone_simulation.frame_counter}/{update_queen_drone_simulation.max_timesteps}")
    
    # Count drones in different states
    approaching = 0
    ready = 0
    moving_away = 0
    waiting = 0
    
    # Move drones
    for i, drone in enumerate(drones):
        marker = drone_markers[i]
        
        if drone.state == "approaching":
            approaching += 1
            drone.approach_queen(queen_bee.get_position(), max_delta=0.6)
            if distance_between(drone.get_position(), queen_bee.get_position()) <= data['interaction_radius']:
                drone.state = "ready_for_gold"
                if should_log:
                    print(f"🐝 DRONE {i+1}: Reached queen! Now ready for mating.")
        elif drone.state == "moving_away":
            moving_away += 1
            drone.move_away_from_queen(max_delta=0.7)
            
            # Keep drones within reasonable bounds from center
            center_x, center_y = 7.5, 7.5
            dist_from_center = ((drone.position_x - center_x)**2 + 
                               (drone.position_y - center_y)**2)**0.5
            if dist_from_center > 4.0:  # Further than queen but still contained
                # Apply gentle force toward center
                dir_x = center_x - drone.position_x
                dir_y = center_y - drone.position_y
                # Normalize
                mag = (dir_x**2 + dir_y**2)**0.5
                if mag > 0:
                    dir_x /= mag
                    dir_y /= mag
                # Apply gentle centering force
                drone.position_x += dir_x * 0.1
                drone.position_y += dir_y * 0.1
                
        elif drone.state == "waiting":
            waiting += 1
            # Keep drones in the center area when waiting
            center_x, center_y = 7.5, 7.5
            
            # Small random movement
            drone.move_randomly(max_delta=0.3)
            
            # Keep drones from wandering too far in waiting state
            dist_from_center = ((drone.position_x - center_x)**2 + 
                               (drone.position_y - center_y)**2)**0.5
            if dist_from_center > 4.0:
                # Move back toward center more strongly when waiting
                dir_x = center_x - drone.position_x
                dir_y = center_y - drone.position_y
                # Normalize
                mag = (dir_x**2 + dir_y**2)**0.5
                if mag > 0:
                    dir_x /= mag
                    dir_y /= mag
                # Apply stronger centering force
                drone.position_x += dir_x * 0.15
                drone.position_y += dir_y * 0.15
        elif drone.state == "ready_for_gold":
            ready += 1
        
        dx, dy = map_to_beehive(drone.position_x, drone.position_y, max_x, max_y)
        marker.move(dx, dy)
        
        # Make sure markers are visible 
        marker.show()
    
    # Always ensure queen is visible
    queen_marker.show()
    
    if should_log:
        print(f"🐝 DRONES: {len(drones)} total - Approaching: {approaching}, Ready: {ready}, Moving away: {moving_away}, Waiting: {waiting}")
    
    # Check if all drones are ready for gold (mating)
    if all(drone.state == "ready_for_gold" for drone in drones):
        # Create a baby bee (gold dot)
        data['baby_bees_count'] += 1
        
        # Ensure baby bee appears in the visible center area
        # Instead of using the queen's exact position, create babies in the same general area
        baby_x = max_x/2 + random.uniform(-1.5, 1.5)  # Center area of the hive
        baby_y = max_y/2 + random.uniform(-1.5, 1.5)
        
        # Vary the size of baby bees slightly for visual interest
        baby_size = 0.15 + random.uniform(-0.03, 0.03)
        
        # Create a gold dot marker for the baby bee with varied size
        gold_dot = plt.Circle((baby_x, baby_y), baby_size, color='gold', zorder=80)
        ax.add_artist(gold_dot)
        data['gold_dots'].append(gold_dot)
        
        print(f"🎉 BABY BEE BORN! Total babies: {data['baby_bees_count']} at ({baby_x:.1f}, {baby_y:.1f})")
        
        # Update status
        nectar_status.set_text(f"Mating simulation - Baby Bees: {data['baby_bees_count']}")
        
        # Drones move away after mating
        for drone in drones:
            drone.queen_reference = queen_bee.get_position()
            drone.state = "moving_away"
    
    # Check if all drones are waiting
    if all(drone.state == "waiting" for drone in drones):
        data['random_move_timer'] += 1
        if data['random_move_timer'] >= 5:
            for drone in drones:
                drone.state = "approaching"
            data['random_move_timer'] = 0
            if should_log:
                print("🔄 All drones now approaching queen again")
    
    # Get the current status text and maintain worker bee info
    current_text = bee_status.get_text()
    
    # Count the current state of drones for detailed status
    drone_states = {
        "approaching": approaching,
        "ready": ready,
        "moving_away": moving_away,
        "waiting": waiting
    }
    
    # Create clean simple status text - minimize complexity to prevent scribbling
    if "Worker Bees:" in current_text:
        worker_info = current_text.split('|')[0].strip()
        status = f"{worker_info} | Queen, {len(drones)} Drones"
    else:
        status = f"Queen, {len(drones)} Drones"
    
    # Add simple activity label
    if approaching > 0:
        status += " (approaching)"
    elif ready > 0:
        status += " (mating)"
    elif moving_away > 0:
        status += " (departing)"
    
    # Add baby count if any
    if data['baby_bees_count'] > 0:
        status += f" - {data['baby_bees_count']} Babies"
    
    # Replace text completely
    bee_status.set_text(status)
    
    # Consistent styling
    bee_status.set_color('red')
    bee_status.set_fontweight('bold')
    
    # Update timestamp text to show simulation progress
    if 'timestamp_text' in data:
        # Show both the frame counter and baby bee count in the timestamp
        data['timestamp_text'].set_text(f"Queen-Drone Sim: {update_queen_drone_simulation.frame_counter}/{update_queen_drone_simulation.max_timesteps} steps | {data['baby_bees_count']} Baby Bees")
    
    # Simulation is still running
    return False

def distance_between(p1, p2):
    """Calculate Euclidean distance between two points"""
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

def update_nectar_level(hexagon_grid, current_nectar, max_nectar_per_cycle, total_nectar, cycle_count, nectar_status):
    """
    Update the hexagon colors based on the TOTAL amount of nectar collected across all cycles.
    The color darkens progressively using an exponential function for faster darkening.
    
    Parameters:
    - hexagon_grid: The grid of hexagon patches
    - current_nectar: Current nectar amount collected in this cycle
    - max_nectar_per_cycle: Maximum nectar that can be collected in one cycle
    - total_nectar: Total nectar collected across all cycles
    - cycle_count: Current cycle number
    - nectar_status: Text object to update with nectar status
    """
    # Update the nectar status text to show current cycle info
    nectar_status.set_text(f"Nectar in Hive: {current_nectar}/{max_nectar_per_cycle} (Cycle {cycle_count})")
    
    # For color calculation, reduce max_expected_nectar to see changes sooner
    # With 20 nectar per cycle, we'll see significant darkening after just 1 cycle
    max_expected_nectar = 30  # Lower threshold for faster visual feedback
    
    # Calculate the darkness level (0 to 1) using an exponential function
    # This will make the darkness increase more dramatically at first
    linear_ratio = min(1.0, total_nectar / max_expected_nectar)
    exponent = 2.5  # Increased from 2.0 for even faster darkening
    darkness_level = 1.0 - (1.0 - linear_ratio) ** exponent
    
    # Only print debug info very occasionally to reduce noise
    # Use a static variable to track when we last printed
    if not hasattr(update_nectar_level, '_last_printed_nectar'):
        update_nectar_level._last_printed_nectar = -1
    
    # Only log when nectar amount has changed AND it's a significant change
    if total_nectar != update_nectar_level._last_printed_nectar and (
        total_nectar % 5 == 0 or  # Print on multiples of 5
        total_nectar - update_nectar_level._last_printed_nectar >= 5  # Or every 5 increase
    ):
        print(f"[NECTAR] Total: {total_nectar}, Darkness: {darkness_level:.2f}, Exponential function applied")
        update_nectar_level._last_printed_nectar = total_nectar
    
    # Calculate color based on nectar level - MUCH more dramatic shift from light to dark gold
    # Start with a very light color (r=1.0, g=0.98, b=0.9)
    # End with rich golden amber (r=1.0, g=0.55, b=0.0)
    r = 1.0  # Red stays at max for golden appearance
    g = 0.98 - (0.43 * darkness_level)  # Green decreases more dramatically for richer gold
    b = 0.9 - (0.9 * darkness_level)    # Blue decreases to zero completely
    
    # Add some alpha to make it look richer when filled
    alpha = 0.75 + (0.25 * darkness_level)  # Slightly higher base alpha for richer appearance
    
    # Center coordinates for radial gradient
    center_col = COLS / 2
    center_row = ROWS / 2
    
    # Maximum distance from center for normalization
    max_distance = ((COLS/2)**2 + (ROWS/2)**2)**0.5
    
    # Apply different darkness levels based on row position and distance from center
    for row_idx in range(ROWS):
        row = hexagon_grid[row_idx]
        
        # Apply gradient effect - bottom rows and center cells darker
        # Apply exponential gradient from bottom to top
        row_factor = 1.0 - (row_idx / ROWS) ** 1.5  # Steeper gradient (1.0 to ~0.2)
        
        for col_idx, hex_patch in enumerate(row):
            # Calculate distance from center
            dist_from_center = ((col_idx - center_col)**2 + (row_idx - center_row)**2)**0.5
            # Normalize to 0-1 range and invert (center = 1, edges = 0)
            center_factor = 1.0 - (dist_from_center / max_distance) ** 1.2  # Exponential falloff from center
            
            # Combine row gradient and center gradient
            # Weight the center gradient more (60% center, 40% row gradient)
            combined_factor = 0.4 * row_factor + 0.6 * center_factor
            
            # Apply the combined factor to the darkness
            cell_darkness = darkness_level * combined_factor
            
            # Cell-specific color with dramatic contrast
            cell_g = 0.98 - (0.43 * cell_darkness)  # Green decreases
            cell_b = 0.9 - (0.9 * cell_darkness)   # Blue decreases completely
            
            # Set color for this hexagon
            hex_patch.set_facecolor((r, cell_g, cell_b, alpha))

def save_image(fig, filename):
    """Save the current figure as an image"""
    # Use transparent=True to ensure we don't affect the background
    fig.savefig(filename, transparent=False)
    print(f"Image saved to {filename}") 