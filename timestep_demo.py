#!/usr/bin/env python3
"""
Demo script for the Timestep simulation integrated with beehive visualization.
Shows queen bee and drone movements with mating behavior in a honeycomb.
"""
import matplotlib.pyplot as plt
import numpy as np
import os
import time

from comb import QueenBeeDot, DroneDot
from comb.Beehive import create_beehive_visualization

# Constants for beehive visualization
HEX_SIZE = 1
COLS, ROWS = 10, 5
OFFSET_X = 1.5 * HEX_SIZE
OFFSET_Y = np.sqrt(3) * HEX_SIZE
MAX_X = COLS * OFFSET_X
MAX_Y = ROWS * OFFSET_Y + OFFSET_Y/2

def map_to_beehive(x, y):
    """Map coordinates from the 0-15 range to beehive coordinates"""
    mapped_x = (x / 15) * MAX_X
    mapped_y = (y / 15) * MAX_Y
    return mapped_x, mapped_y

def main():
    # Set up directory for saving images
    save_dir = "beehive_timesteps"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Create a queen bee and drones
    queen_bee = QueenBeeDot()
    print(f"Queen Bee Initial Position: {queen_bee}")
    
    drones = [DroneDot() for _ in range(4)]
    print("Drone Initial Positions:")
    for i, drone in enumerate(drones):
        print(f"Drone {i+1}: {drone}")
    
    # Set up the beehive visualization
    plt.ion()
    fig = plt.figure(figsize=(12, 8))
    
    # Create beehive visualization
    ax, hexagon_grid, circle_markers, nectar_status, bee_status = create_beehive_visualization(
        num_bees=len(drones)+1,  # +1 for queen bee
        max_nectar=20,
        fig=fig,
        subplot=111
    )
    
    # Configure the first marker as the queen bee (blue)
    queen_marker = circle_markers[0]
    queen_marker.color = 'blue'
    if hasattr(queen_marker, 'circle'):
        queen_marker.circle.set_color('blue')
    
    # Map initial positions to beehive coordinates
    qx, qy = map_to_beehive(queen_bee.position_x, queen_bee.position_y)
    queen_marker.move(qx, qy)
    queen_marker.show()
    
    # Configure the remaining markers as drones (black)
    for i, drone in enumerate(drones):
        marker = circle_markers[i+1]
        marker.color = 'black'
        if hasattr(marker, 'circle'):
            marker.circle.set_color('black')
        dx, dy = map_to_beehive(drone.position_x, drone.position_y)
        marker.move(dx, dy)
        marker.show()
    
    # Update status text
    bee_status.set_text(f"Queen Bee (blue) and {len(drones)} Drones (black)")
    nectar_status.set_text("Mating simulation - Gold dots show new bees")
    
    # Interaction settings
    interaction_radius = 1.5
    random_move_timer = 0
    gold_dots = []  # Store gold dot markers
    baby_bees_count = 0
    
    # Simulation loop
    total_steps = 60
    for step in range(total_steps):
        # Move queen bee
        queen_bee.move_randomly(max_delta=0.2)
        qx, qy = map_to_beehive(queen_bee.position_x, queen_bee.position_y)
        queen_marker.move(qx, qy)
        
        # Move drones
        for i, drone in enumerate(drones):
            marker = circle_markers[i+1]
            
            if drone.state == "approaching":
                drone.approach_queen(queen_bee.get_position(), max_delta=0.6)
                if distance_between(drone.get_position(), queen_bee.get_position()) <= interaction_radius:
                    drone.state = "ready_for_gold"
            elif drone.state == "moving_away":
                drone.move_away_from_queen(max_delta=0.7)
            elif drone.state == "waiting":
                drone.move_randomly(max_delta=0.3)
            
            dx, dy = map_to_beehive(drone.position_x, drone.position_y)
            marker.move(dx, dy)
        
        # Check if all drones are ready for gold (mating)
        if all(drone.state == "ready_for_gold" for drone in drones):
            # Create a baby bee (gold dot)
            baby_bees_count += 1
            queen_x, queen_y = map_to_beehive(queen_bee.position_x, queen_bee.position_y)
            
            # Create a gold dot marker for the baby bee
            gold_dot = plt.Circle((queen_x, queen_y), 0.15, color='gold')
            ax.add_artist(gold_dot)
            gold_dots.append(gold_dot)
            
            print(f"\n🎉 Baby Bee Born at: {queen_bee.get_position()} (Total: {baby_bees_count})")
            
            # Update status
            nectar_status.set_text(f"Mating simulation - Baby Bees: {baby_bees_count}")
            
            # Drones move away after mating
            for drone in drones:
                drone.queen_reference = queen_bee.get_position()
                drone.state = "moving_away"
        
        # Check if all drones are waiting
        if all(drone.state == "waiting" for drone in drones):
            random_move_timer += 1
            if random_move_timer >= 5:
                for drone in drones:
                    drone.state = "approaching"
                random_move_timer = 0
        
        # Print status
        print(f"\nStep {step + 1}: Queen Bee: {queen_bee}")
        for i, drone in enumerate(drones):
            print(f"Drone {i + 1}: {drone}")
        
        # Save the figure
        plt.savefig(f"{save_dir}/beehive_step_{step+1}.png")
        plt.pause(0.5)
    
    plt.ioff()
    plt.show()

def distance_between(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

if __name__ == "__main__":
    main() 