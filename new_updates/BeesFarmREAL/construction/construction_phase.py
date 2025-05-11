import numpy as np
import random
import matplotlib.pyplot as plt
from comb.Classhive import CircleMarker, hexagon
from utils.constants import HEX_SIZE, COLS, ROWS, OFFSET_X, OFFSET_Y

# Construction phase global variables - default values
CONSTRUCTION_SPEED = 0.1  # Default number of cells to build per update (slower for better visualization)

def initialize_comb_construction(ax, max_x, max_y):
    """
    Initialize the honeycomb grid with construction indicators.
    
    Parameters:
    - ax: Matplotlib axes
    - max_x: Maximum x-coordinate
    - max_y: Maximum y-coordinate
    
    Returns:
    - hexagon_grid: Grid of hexagon patches
    - construction_progress: Dictionary with construction status information
    """
    # Create the honeycomb grid
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
            # Very transparent initial state for unbuilt cells
            patch = ax.fill(x_hexagon, y_hexagon, edgecolor="black", 
                          facecolor=(0.9, 0.9, 0.9, 0.2), lw=1)[0]
            row_hexagons.append(patch)
        hexagon_grid.append(row_hexagons)
    
    # Create a build order starting from the center and spiraling outward
    center_row = ROWS // 2
    center_col = COLS // 2
    
    # Define the build order (spiral pattern)
    build_order = []
    max_spiral = max(ROWS, COLS) // 2 + 1
    for spiral in range(max_spiral):
        for i in range(spiral * 2):
            # Right edge
            if center_row - spiral + i >= 0 and center_row - spiral + i < ROWS and center_col + spiral < COLS:
                build_order.append((center_row - spiral + i, center_col + spiral))
        
        for i in range(spiral * 2):
            # Bottom edge
            if center_row + spiral < ROWS and center_col + spiral - i >= 0 and center_col + spiral - i < COLS:
                build_order.append((center_row + spiral, center_col + spiral - i))
        
        for i in range(spiral * 2):
            # Left edge
            if center_row + spiral - i >= 0 and center_row + spiral - i < ROWS and center_col - spiral >= 0:
                build_order.append((center_row + spiral - i, center_col - spiral))
        
        for i in range(spiral * 2):
            # Top edge
            if center_row - spiral >= 0 and center_col - spiral + i >= 0 and center_col - spiral + i < COLS:
                build_order.append((center_row - spiral, center_col - spiral + i))
    
    # Filter out any duplicates and invalid coordinates
    build_order = list(dict.fromkeys(
        (row, col) for row, col in build_order 
        if 0 <= row < ROWS and 0 <= col < COLS
    ))
    
    # Create markers for construction worker bees
    worker_markers = []
    
    # Set up construction progress tracking
    construction_progress = {
        'build_order': build_order,
        'built_cells': 0,
        'total_cells': len(build_order),
        'worker_markers': worker_markers,
        'construction_speed': CONSTRUCTION_SPEED,
        'ax': ax  # Store the axes for marker creation
    }
    
    print(f"Construction initialized with {len(build_order)} cells to build")
    
    return hexagon_grid, construction_progress

def update_comb_construction(hexagon_grid, construction_progress, worker_positions):
    """
    Update the honeycomb construction progress based on worker bee positions.
    
    Parameters:
    - hexagon_grid: Grid of hexagon patches
    - construction_progress: Dictionary with construction status
    - worker_positions: List of worker bee positions (x, y)
    
    Returns:
    - construction_complete: Boolean indicating if construction is complete
    """
    build_order = construction_progress['build_order']
    built_cells = construction_progress['built_cells']
    total_cells = construction_progress['total_cells']
    worker_markers = construction_progress['worker_markers']
    construction_speed = construction_progress.get('construction_speed', CONSTRUCTION_SPEED)
    
    # Check if construction is already complete
    if built_cells >= total_cells:
        # Remove worker markers if not already done
        for marker in worker_markers:
            if hasattr(marker, 'circle'):
                marker.hide()
        
        # Clear the worker markers list to prevent memory leak
        worker_markers.clear()
        
        return True  # Construction is complete
    
    # Update worker bee markers if they don't exist or count doesn't match
    if len(worker_markers) != len(worker_positions):
        # Clear existing markers if count doesn't match
        for marker in worker_markers:
            if hasattr(marker, 'circle'):
                marker.hide()
        worker_markers.clear()
        
        # Create new markers
        for x, y in worker_positions:
            marker = CircleMarker(x, y, radius=0.1, color='red')
            marker.plot(construction_progress.get('ax', plt.gca()))
            marker.show()
            worker_markers.append(marker)
    else:
        # Update existing marker positions
        for i, (x, y) in enumerate(worker_positions):
            if i < len(worker_markers):
                worker_markers[i].move(x, y)
                worker_markers[i].show()
    
    # Handle fractional construction speed by accumulating progress
    construction_progress['build_accumulator'] = construction_progress.get('build_accumulator', 0) + construction_speed
    
    # Only build cells when the accumulator reaches at least 1
    cells_to_build = int(construction_progress['build_accumulator'])
    if cells_to_build >= 1:
        # Remove the used portion from the accumulator
        construction_progress['build_accumulator'] -= cells_to_build
        
        # Limit by remaining cells
        cells_to_build = min(cells_to_build, total_cells - built_cells)
        
        for _ in range(cells_to_build):
            if built_cells < total_cells:
                row, col = build_order[built_cells]
                
                # Update the cell appearance to show it's built
                hex_patch = hexagon_grid[row][col]
                hex_patch.set_facecolor((1.0, 0.95, 0.8, 0.6))  # Light honey color with opacity
                
                # Increment built cells count
                built_cells += 1
    
    # Update the construction progress
    construction_progress['built_cells'] = built_cells
    
    # Print progress occasionally
    if built_cells % 5 == 0 and built_cells > construction_progress.get('last_reported', -1):
        construction_progress['last_reported'] = built_cells
        percent_complete = (built_cells / total_cells) * 100
        print(f"Construction progress: {built_cells}/{total_cells} cells ({percent_complete:.1f}%)")
    
    # Check if construction is now complete
    construction_complete = built_cells >= total_cells
    
    if construction_complete:
        print("🏗️ Construction phase complete!")
        
        # Remove worker markers
        for marker in worker_markers:
            if hasattr(marker, 'circle'):
                marker.hide()
        
        # Clear the worker markers list
        worker_markers.clear()
    
    return construction_complete 