import numpy as np
import matplotlib.pyplot as plt
import time
from construction.construction_phase import update_comb_construction
from utils.constants import COLS, ROWS

def run_construction_animation(fig, hexagon_grid, circle_markers, num_worker_bees, max_frames=500, construction_speed=0.2):
    """
    Run the construction animation on the existing honeycomb grid
    
    Parameters:
    - fig: Matplotlib figure
    - hexagon_grid: Existing hexagon grid from create_beehive_view
    - circle_markers: Marker objects for worker bees
    - num_worker_bees: Number of worker bees to animate
    - max_frames: Maximum number of frames to run animation
    - construction_speed: Speed of construction (cells per frame)
    
    Returns:
    - construction_completed: Boolean indicating if construction finished
    """
    print(f"🏗️ Starting honeycomb construction phase with {num_worker_bees} worker bees")
    
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
    
    # Set all cells to initially transparent
    for row in range(ROWS):
        for col in range(COLS):
            if row < len(hexagon_grid) and col < len(hexagon_grid[row]):
                hex_patch = hexagon_grid[row][col]
                hex_patch.set_facecolor((0.9, 0.9, 0.9, 0.2))  # Very transparent
    
    # Set up construction progress tracking
    construction_progress = {
        'build_order': build_order,
        'built_cells': 0,
        'total_cells': len(build_order),
        'worker_markers': circle_markers[:num_worker_bees],  # Use existing markers
        'construction_speed': construction_speed,
        'last_reported': -1
    }
    
    # Generate initial worker bee positions (near the center of the honeycomb)
    worker_bee_positions = []
    for i in range(num_worker_bees):
        # Position bees around the center with some randomness
        x = center_col + np.random.uniform(-2, 2)
        y = center_row + np.random.uniform(-2, 2)
        worker_bee_positions.append((x, y))
        
        # Show the worker markers
        if i < len(circle_markers):
            circle_markers[i].move(x, y)
            circle_markers[i].show()
    
    # Hide any unused markers
    for i in range(num_worker_bees, len(circle_markers)):
        circle_markers[i].hide()
    
    # Run the construction animation
    construction_completed = False
    frame_count = 0
    
    # Update the figure to show initial state
    plt.draw()
    plt.pause(0.1)
    
    start_time = time.time()
    
    # Animation loop for construction phase
    while not construction_completed and frame_count < max_frames:
        # Move worker bees towards the next cell to build
        if frame_count % 5 == 0 and construction_progress['built_cells'] < construction_progress['total_cells']:
            target_cell_idx = min(construction_progress['built_cells'], len(build_order) - 1)
            target_row, target_col = build_order[target_cell_idx]
            
            # Move workers towards the target cell with some randomness
            for i in range(len(worker_bee_positions)):
                x, y = worker_bee_positions[i]
                
                # Add randomness to worker movement
                rand_x = np.random.uniform(-0.5, 0.5)
                rand_y = np.random.uniform(-0.5, 0.5)
                
                # Calculate direction to target
                dx = (target_col + rand_x) - x
                dy = (target_row + rand_y) - y
                
                # Normalize and scale
                dist = np.sqrt(dx**2 + dy**2)
                if dist > 0.1:
                    scale = 0.3 / dist  # Movement speed
                    worker_bee_positions[i] = (
                        x + dx * scale,
                        y + dy * scale
                    )
                
                # Update marker position
                if i < len(circle_markers):
                    circle_markers[i].move(worker_bee_positions[i][0], worker_bee_positions[i][1])
        
        # Update construction progress
        construction_completed = update_construction_cells(hexagon_grid, construction_progress)
        
        # Update the figure
        plt.draw()
        plt.pause(0.05)  # Short pause for animation
        
        frame_count += 1
        
        # Add progress indicator
        if frame_count % 20 == 0:
            elapsed = time.time() - start_time
            percent = (construction_progress['built_cells'] / construction_progress['total_cells']) * 100
            print(f"Construction progress: {percent:.1f}% ({frame_count} frames, {elapsed:.1f} seconds)")
    
    # Final update to ensure all cells are built
    if not construction_completed:
        # Force completion
        for row, col in build_order[construction_progress['built_cells']:]:
            if row < len(hexagon_grid) and col < len(hexagon_grid[row]):
                hex_patch = hexagon_grid[row][col]
                hex_patch.set_facecolor((1.0, 0.95, 0.8, 0.6))  # Light honey color
        
        construction_completed = True
    
    elapsed_time = time.time() - start_time
    print(f"🏗️ Construction phase completed in {frame_count} frames ({elapsed_time:.1f} seconds)")
    
    return construction_completed

def update_construction_cells(hexagon_grid, construction_progress):
    """
    Update the honeycomb cell colors based on construction progress
    
    Parameters:
    - hexagon_grid: Grid of hexagon patches
    - construction_progress: Dictionary with construction status
    
    Returns:
    - construction_complete: Boolean indicating if construction is complete
    """
    build_order = construction_progress['build_order']
    built_cells = construction_progress['built_cells']
    total_cells = construction_progress['total_cells']
    construction_speed = construction_progress.get('construction_speed', 0.2)
    
    # Check if construction is already complete
    if built_cells >= total_cells:
        return True  # Construction is complete
    
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
                if row < len(hexagon_grid) and col < len(hexagon_grid[row]):
                    hex_patch = hexagon_grid[row][col]
                    hex_patch.set_facecolor((1.0, 0.95, 0.8, 0.6))  # Light honey color with opacity
                
                # Increment built cells count
                built_cells += 1
    
    # Update the construction progress
    construction_progress['built_cells'] = built_cells
    
    # Print progress occasionally
    if built_cells % 10 == 0 and built_cells > construction_progress.get('last_reported', -1):
        construction_progress['last_reported'] = built_cells
        percent_complete = (built_cells / total_cells) * 100
        print(f"Construction progress: {built_cells}/{total_cells} cells ({percent_complete:.1f}%)")
    
    # Check if construction is now complete
    construction_complete = built_cells >= total_cells
    
    if construction_complete:
        print("🏗️ Honeycomb construction complete!")
    
    return construction_complete 