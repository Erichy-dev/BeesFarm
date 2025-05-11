import random

# Define a function to measure distance between two points
def distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

# A function to print focused debug information about bee placement
def debug_bee_position(message, bee_index=None, position=None, level="INFO"):
    # Only print if it's an important message or we explicitly want verbose logs
    from simulation.simulation_config import DEBUG_VERBOSE
    
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

def check_simulation_completed(frame, landscape):
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