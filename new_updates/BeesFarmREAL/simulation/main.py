import matplotlib
# Set Qt backend before importing pyplot
matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import random
import numpy as np
import argparse
from matplotlib.gridspec import GridSpec
import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import sys
import csv
from simulation.simulation_config import FPS, SCREENSHOT_INTERVAL, WAIT_BETWEEN_CYCLES
from simulation.input_handlers import interactive_mode, batch_mode
from visualization.hive_view import create_beehive_view, update_nectar_level, update_queen_drone_simulation
from entities.landscape import Landscape
from movement.movement import Move
from utils.helpers import ensure_gold_dots_at_spawn_points, regenerate_nectar, reset_bee_positions
from utils.constants import DEBUG_VERBOSE, COLS, ROWS, OFFSET_X, OFFSET_Y
from simulation.screenshot import ScreenshotManager
from simulation.animation import AnimationHandler
from construction.construction_animation import run_construction_animation

# Screenshot configuration
ENABLE_SCREENSHOTS = True  # Set to False to disable screenshots

# Global variable to track if simulation is complete
SIMULATION_COMPLETE = False

def read_para_csv(file_name):
    defaults = {}
    try:
        with open(file_name, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) == 2:
                    key, value = row
                    defaults[key.strip()] = int(value.strip())
    except FileNotFoundError:
        print(f"")
    return(
        defaults.get("num_houses", 4),
        defaults.get("num_red_dots", 1)
    )
def read_map_csv(file_name):
    values = {}
    try:
        with open(file_name, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) == 2:
                    key, value = row
                    values[key.strip()] = int(value.strip())
    except FileNotFoundError:
        print(f".")
    return (
        values.get("num_drone_bees", 2),
        values.get("timesteps", 100)
    )

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Bee World Simulation")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run the program in interactive mode")
    parser.add_argument("-f", "--terrain", type=str, help="Terrain file for batch mode")
    parser.add_argument("-p", "--parameters", type=str, help="Parameters file for batch mode")
    parser.add_argument("--skip-construction", action="store_true", help="Skip the construction phase animation")

    args = parser.parse_args()

    # Create Qt application
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    if args.interactive:
        # If -i flag is provided, run interactive mode
        num_houses, num_red_dots, num_drone_bees, max_timesteps = interactive_mode()
    elif args.terrain and args.parameters:
        # If both -f and -p flags are provided, run batch mode
        num_houses, num_red_dots, num_drone_bees, max_timesteps = batch_mode(args.terrain, args.parameters)
    else:
        print("Invalid input. Use -i for interactive mode or -f and -p for batch mode.")
        return

    # Store original target timesteps before adding compensation
    original_timesteps = max_timesteps
    
    # Add 15 timesteps to compensate for construction phase
    if not args.skip_construction:
        compensation_timesteps = 20
        max_timesteps += compensation_timesteps
        print(f"Adding {compensation_timesteps} timesteps to compensate for construction phase ({original_timesteps} → {max_timesteps})")

    # Set target timesteps in the update function (for displaying the correct target)
    update_queen_drone_simulation.target_timesteps = original_timesteps

    # Create figure with grid layout for both visualizations
    fig = plt.figure(figsize=(16, 8))
    gs = GridSpec(1, 2, width_ratios=[1, 1])
    
    # Create beehive visualization with the correct number of worker bees
    beehive_ax, circle_markers, triangle_markers, square_markers, hexagon_grid, bee_status, timestamp_text, nectar_status, bee_sizes_text, total_nectar_text, total_box = create_beehive_view(fig, gs, num_red_dots, drone_bees=num_drone_bees)
    
    # Set up the right subplot for landscape but don't populate it yet
    landscape_ax = fig.add_subplot(gs[0, 1])
    landscape_ax.set_title("Landscape (Construction in Progress)")
    landscape_ax.axis('off')  # Hide axes during construction
    
    # Run the construction phase first if not skipped
    if not args.skip_construction:
        print("\n=== CONSTRUCTION PHASE ===")
        
        # Run the construction animation using the existing board
        run_construction_animation(
            fig=fig,
            hexagon_grid=hexagon_grid,
            circle_markers=circle_markers,
            num_worker_bees=num_red_dots,
            max_frames=500,
            construction_speed=0.2
        )
        
        print("\n=== CONSTRUCTION COMPLETE ===")
        plt.pause(0.5)  # Brief pause after construction
    
    # NOW setup objects in the environment (after construction)
    landscape = Landscape(block_size=15, max_gold_collected=20, num_houses=num_houses)
    
    # Set max timesteps with compensation for construction time
    landscape.max_timesteps = max_timesteps
    # Store original timesteps for reporting
    landscape.original_timesteps = original_timesteps
    print(f"Simulation will run for {max_timesteps} timesteps (target: {original_timesteps})")
    
    landscape.objects.add_beehive(position=(11, 0), height=3, width=3)
    landscape.objects.add_pond(position=(12, 5), height=5, width=3)
    landscape.objects.add_red_dots(count=num_red_dots)
    landscape.objects.add_gold_dots(count=5)
    landscape.objects.add_silver_dots()
    
    # Ensure there's gold nectar (alliance) at each spawn point
    ensure_gold_dots_at_spawn_points(landscape.objects)

    # Initialize movement logic with obstacle avoidance (pond + forbidden zone)
    landscape.movement = Move(
        red_dots=landscape.objects.red_dots,
        gold_dots=landscape.objects.gold_dots,
        beehive_position=(11, 2),
        max_gold_collected=landscape.max_gold_collected,
        pond_position=(12, 5),
        pond_size=(3, 5),
        forbidden_zone_func=landscape.is_inside_forbidden_zone,
        silver_dots=landscape.objects.silver_dots
    )

    # NOW show landscape (after construction)
    landscape.display(fig=fig, subplot_spec=gs[0, 1], title=f"Landscape with {num_red_dots} Worker Bees")
    
    print("\n=== MAIN SIMULATION STARTING ===")
    
    # Initialize screenshot manager
    screenshot_manager = ScreenshotManager(fig)
    screenshot_manager.initialize_timer(SCREENSHOT_INTERVAL)
    
    # Initialize animation handler
    animation_handler = AnimationHandler(
        landscape=landscape,
        circle_markers=circle_markers,
        triangle_markers=triangle_markers,
        square_markers=square_markers,
        hexagon_grid=hexagon_grid,
        bee_status=bee_status,
        timestamp_text=timestamp_text,
        nectar_status=nectar_status,
        bee_sizes_text=bee_sizes_text,
        total_nectar_text=total_nectar_text,
        total_box=total_box,
        screenshot_manager=screenshot_manager,
        target_timesteps=original_timesteps  # Pass original target timesteps
    )
    
    try:
        # Create a combined animation
        ani = animation.FuncAnimation(
            fig, 
            animation_handler.update, 
            frames=999999,
            interval=1000/FPS,
            blit=True,
            repeat=True
        )
        
        # Display the combined figure with right plot margin for annotations
        plt.tight_layout()
        
        # Show the plot with Qt's main loop
        plt.show()
        
        # Stop the screenshot timer when animation ends
        screenshot_manager.stop_timer()
        
    except Exception as e:
        # Print any error that occurs during animation
        print(f"Error during animation: {e}")
        print(f"Total nectar collected: {animation_handler.total_nectar_collected}")

if __name__ == "__main__":
    main() 
