import matplotlib
matplotlib.use('Qt5Agg')  # Set backend

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import random
import time
import argparse
from matplotlib.gridspec import GridSpec

# Import the construction phase functions
from construction.construction_phase import initialize_comb_construction, update_comb_construction
from comb.Classhive import CircleMarker, hexagon
from utils.constants import HEX_SIZE, COLS, ROWS, OFFSET_X, OFFSET_Y

# Default construction simulation constants
FPS = 30  # Frames per second for animation
CONSTRUCTION_SPEED = 0.1  # Cells built per update (reduced to make it much slower)
DEFAULT_WORKER_BEES = 5  # Default number of worker bees

# Global variables
construction_complete = False
start_time = None
bee_targets = []  # Target positions for worker bees

def create_construction_view(fig, num_worker_bees):
    """Create the visualization for the construction mini-simulation"""
    
    # Set up the axes
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    ax.axis('off')  # Turn off all axes, spines, and ticks
    
    # Set extended limits with extra padding
    max_x = COLS * OFFSET_X
    max_y = ROWS * OFFSET_Y + OFFSET_Y/2
    ax.set_xlim(-1, max_x + 1)
    ax.set_ylim(-9, max_y + 1)  # Match original bottom space
    
    # Add title
    ax.set_title("Honeycomb Construction Simulation", fontsize=14, pad=15)
    
    # Add status text
    status_text = ax.text(max_x/2, -5, "Construction Phase", 
                         color='orange', fontweight='bold', fontsize=12,
                         horizontalalignment='center', bbox=dict(facecolor='white', alpha=0.7, pad=2))
    
    # Initialize honeycomb grid with construction phase
    hexagon_grid, construction_progress = initialize_comb_construction(ax, max_x, max_y)
    
    # Store the worker bee count in the construction progress
    construction_progress['num_worker_bees'] = num_worker_bees
    
    return ax, hexagon_grid, construction_progress, status_text, max_x, max_y

def generate_worker_positions(construction_progress):
    """Generate realistic worker positions inside the honeycomb"""
    global bee_targets
    
    # Get the number of worker bees from the construction progress
    num_worker_bees = construction_progress.get('num_worker_bees', DEFAULT_WORKER_BEES)
    
    # Initialize targets on first call
    if len(bee_targets) == 0:
        bee_targets = [None] * num_worker_bees
    
    # Get current build position from construction progress
    if 'build_order' in construction_progress and construction_progress['built_cells'] < len(construction_progress['build_order']):
        # Get next few cells to build to distribute workers
        next_cells = []
        for i in range(min(num_worker_bees, len(construction_progress['build_order']) - construction_progress['built_cells'])):
            if construction_progress['built_cells'] + i < len(construction_progress['build_order']):
                next_cells.append(construction_progress['build_order'][construction_progress['built_cells'] + i])
    
        # Assign workers to cells
        for i in range(num_worker_bees):
            if i < len(next_cells):
                row, col = next_cells[i]
                # Calculate position
                x = col * OFFSET_X
                y = row * OFFSET_Y
                
                # Stagger odd columns
                if col % 2 == 1:
                    y += OFFSET_Y / 2
                
                # Add slight random offset within the cell
                x += random.uniform(-0.05, 0.05)
                y += random.uniform(-0.05, 0.05)
                
                bee_targets[i] = (x, y)
            elif bee_targets[i] is None or random.random() < 0.05:
                # Random position for other bees
                x = random.uniform(OFFSET_X, (COLS-1) * OFFSET_X)
                y = random.uniform(OFFSET_Y, (ROWS-1) * OFFSET_Y)
                bee_targets[i] = (x, y)
    else:
        # Random positions if no build order available
        for i in range(num_worker_bees):
            if bee_targets[i] is None or random.random() < 0.05:
                x = random.uniform(OFFSET_X, (COLS-1) * OFFSET_X)
                y = random.uniform(OFFSET_Y, (ROWS-1) * OFFSET_Y)
                bee_targets[i] = (x, y)
    
    # Generate current positions based on targets and gradual movement
    worker_positions = []
    for i in range(num_worker_bees):
        if 'worker_markers' in construction_progress and i < len(construction_progress['worker_markers']):
            marker = construction_progress['worker_markers'][i]
            if hasattr(marker, 'x') and hasattr(marker, 'y') and bee_targets[i] is not None:
                # Current position
                current_x, current_y = marker.x, marker.y
                target_x, target_y = bee_targets[i]
                
                # Move gradually toward target
                dx = target_x - current_x
                dy = target_y - current_y
                
                # Add position with some movement toward target
                worker_positions.append((current_x + dx * 0.2, current_y + dy * 0.2))
                continue
        
        # Fallback: use target position directly
        if bee_targets[i] is not None:
            worker_positions.append(bee_targets[i])
        else:
            # Random position if no target
            x = random.uniform(OFFSET_X, (COLS-1) * OFFSET_X)
            y = random.uniform(OFFSET_Y, (ROWS-1) * OFFSET_Y)
            worker_positions.append((x, y))
    
    return worker_positions

def update(frame, ax, hexagon_grid, construction_progress, status_text, max_x, max_y, all_artists):
    """Update function for animation"""
    global construction_complete, start_time
    
    # Initialize start time on first frame
    if start_time is None:
        start_time = time.time()
    
    # Get elapsed time
    elapsed_time = time.time() - start_time
    formatted_time = f"{elapsed_time:.1f}"
    
    # If construction is already complete, don't do anything
    if construction_complete:
        status_text.set_text(f"Construction Complete! (Time: {formatted_time}s)")
        return all_artists
    
    # Generate worker positions that move gradually toward build targets
    worker_positions = generate_worker_positions(construction_progress)
    
    # Update construction progress
    construction_complete = update_comb_construction(hexagon_grid, construction_progress, worker_positions)
    
    # Make sure construction worker markers are added to all_artists for animation
    if 'worker_markers' in construction_progress:
        for marker in construction_progress['worker_markers']:
            if hasattr(marker, 'circle') and marker.circle not in all_artists:
                all_artists.append(marker.circle)
    
    # Update status text
    if construction_complete:
        status_text.set_text(f"Construction Complete! (Time: {formatted_time}s)")
        print(f"\n🏗️ Construction completed in {formatted_time} seconds!")
    else:
        percent_complete = (construction_progress['built_cells'] / construction_progress['total_cells']) * 100
        status_text.set_text(f"Construction Progress: {percent_complete:.1f}% (Time: {formatted_time}s)")
    
    # Print progress every 50 frames
    if frame % 50 == 0:
        percent_complete = (construction_progress['built_cells'] / construction_progress['total_cells']) * 100
        print(f"Construction progress: {percent_complete:.1f}% (Frame {frame})")
    
    return all_artists

def main():
    """Main function to run the mini-simulation"""
    # Global declaration must come before any use of the variable
    global CONSTRUCTION_SPEED
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Honeycomb Construction Mini-Simulation")
    parser.add_argument("-w", "--workers", type=int, default=DEFAULT_WORKER_BEES,
                        help=f"Number of construction worker bees (default: {DEFAULT_WORKER_BEES})")
    parser.add_argument("-s", "--speed", type=int, default=CONSTRUCTION_SPEED,
                        help=f"Construction speed in cells per update (default: {CONSTRUCTION_SPEED})")
    args = parser.parse_args()
    
    # Validate arguments
    if args.workers < 1:
        print("Warning: At least 1 construction worker bee is required. Setting to 1.")
        args.workers = 1
    
    if args.speed < 1:
        print("Warning: Construction speed must be at least 1. Setting to 1.")
        args.speed = 1
    
    # Update global variables with command line arguments
    CONSTRUCTION_SPEED = args.speed
    
    print("Starting Honeycomb Construction Mini-Simulation")
    print(f"Construction worker bees: {args.workers}")
    print(f"Construction speed: {CONSTRUCTION_SPEED} cells/update")
    
    # Create figure
    fig = plt.figure(figsize=(10, 8))
    
    # Create visualization with specified number of bees
    ax, hexagon_grid, construction_progress, status_text, max_x, max_y = create_construction_view(
        fig, args.workers)
    
    # Create list of artists to animate
    all_artists = []
    
    # Add all hexagon patches to artists
    for row in hexagon_grid:
        for hex_patch in row:
            all_artists.append(hex_patch)
    
    # Add status text to artists
    all_artists.append(status_text)
    
    # Create animation
    ani = animation.FuncAnimation(
        fig, 
        update, 
        fargs=(ax, hexagon_grid, construction_progress, status_text, max_x, max_y, all_artists),
        frames=9999,  # Effectively infinite
        interval=1000/FPS,  # Convert FPS to milliseconds
        blit=True,  # Use blitting for performance
        repeat=False  # Don't repeat when we reach the end
    )
    
    # Display the plot
    plt.tight_layout()
    plt.show()
    
    print("Simulation complete.")

if __name__ == "__main__":
    main() 