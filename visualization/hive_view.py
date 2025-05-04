import matplotlib.pyplot as plt
import random
import numpy as np
from comb.Classhive import CircleMarker, hexagon
from utils.constants import HEX_SIZE, COLS, ROWS, OFFSET_X, OFFSET_Y

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


def create_beehive_visualization(num_bees=3, max_nectar=20, fig=None, subplot=None):
    """
    Creates a simplified beehive visualization with:
    - A hexagonal grid representing the honeycomb
    - Only the bees represented as red circles
    - Starting with a light color to show absence of nectar
    
    Parameters:
    - num_bees: number of bees to show
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
    
    # Position text in the original positions
    nectar_status = ax.text(max_x/2 - 2, -7, "Nectar in Hive: 0", 
                         color='darkorange', fontweight='bold', fontsize=12,
                         horizontalalignment='center')
    
    bee_status = ax.text(max_x/2 - 2, -3, f"Worker Bees: {num_bees}", 
                       color='red', fontweight='bold', fontsize=12,
                       horizontalalignment='center')
    
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
    for _ in range(num_bees):
        # Random initial position near edge of comb
        x = random.uniform(0, max_x)
        y = random.uniform(0, max_y/4)  # Start at bottom quarter
        
        # Create a marker representing a bee
        circle_marker = CircleMarker(x, y, radius=0.1, color='red')  # Match original radius
        circle_marker.plot(ax)
        # Initially hide the markers since bees start outside the hive
        circle_marker.hide()
        circle_markers.append(circle_marker)
    
    # Return all the elements needed for later updates
    return ax, hexagon_grid, circle_markers, nectar_status, bee_status

def update_nectar_level(hexagon_grid, current_nectar, max_nectar_per_cycle, total_nectar, cycle_count, nectar_status):
    """
    Update the hexagon colors based on the TOTAL amount of nectar collected across all cycles.
    The color darkens progressively over time, without resetting between cycles.
    
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
    
    # We no longer use a ratio based on current cycle, but on overall accumulation
    # Estimate how dark the hive should be based on total nectar
    # The hive can get very dark after several complete cycles
    
    # For color calculation, reduce max_expected_nectar to see changes sooner
    # With 20 nectar per cycle, we'll see max darkness after 2 cycles
    max_expected_nectar = 40  # After this much nectar, the comb is at maximum darkness
    
    # Calculate the darkness level (0 to 1)
    darkness_level = min(1.0, total_nectar / max_expected_nectar)
    
    # Only print debug info very occasionally to reduce noise
    # Use a static variable to track when we last printed
    if not hasattr(update_nectar_level, '_last_printed_nectar'):
        update_nectar_level._last_printed_nectar = -1
    
    # Only log when nectar amount has changed AND it's a significant change
    if total_nectar != update_nectar_level._last_printed_nectar and (
        total_nectar % 10 == 0 or  # Print on multiples of 10
        total_nectar - update_nectar_level._last_printed_nectar >= 10  # Or every 10 increase
    ):
        print(f"[NECTAR] Total: {total_nectar}, Darkness: {darkness_level:.2f}")
        update_nectar_level._last_printed_nectar = total_nectar
    
    # Calculate color based on nectar level - MORE dramatic shift from light to dark gold
    # Start with a very light color (r=1.0, g=0.98, b=0.9)
    # End with deep amber gold (r=1.0, g=0.75, b=0.0)
    r = 1.0  # Red stays at max
    g = 0.98 - (0.23 * darkness_level)  # Green decreases more dramatically
    b = 0.9 - (0.9 * darkness_level)    # Blue decreases to zero completely
    
    # Add some alpha to make it look richer when filled
    alpha = 0.7 + (0.3 * darkness_level)
    
    # Fill all hexagons in the grid with the same color
    # For a more sophisticated look, we could darken from bottom to top
    
    # Calculate how many rows should be filled based on the darkness
    # All rows get some color, but darker at the bottom
    for row_idx in range(ROWS):
        row = hexagon_grid[row_idx]
        
        # Add gradient effect - bottom rows much darker than top rows
        # Apply 100% of darkness at the bottom row, decreasing as we move up
        row_factor = 1.0 - (row_idx / ROWS * 0.7)  # 1.0 to 0.3 from bottom to top (steeper gradient)
        row_darkness = darkness_level * row_factor
        
        # Row-specific color - more dramatic contrast
        row_g = 0.98 - (0.3 * row_darkness)  # Greater green decrease
        row_b = 0.9 - (0.9 * row_darkness)   # Eliminate blue completely
        
        # Set color for all hexagons in this row
        for hex_patch in row:
            hex_patch.set_facecolor((r, row_g, row_b, alpha)) 