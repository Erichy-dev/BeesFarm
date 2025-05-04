import random
import math
from entities.circle_dot import CircleDot

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