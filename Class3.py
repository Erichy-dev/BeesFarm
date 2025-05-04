# --- Class3.py ---
import math
import random  # Add random for logging with unique IDs

# Debug verbosity control
DEBUG_VERBOSE = False  # Set to True for verbose output

class Move:
    def __init__(self, red_dots, gold_dots, beehive_position, max_gold_collected, pond_position, pond_size, forbidden_zone_func=None, silver_dots=None):
        self.red_dots = red_dots  # Now a list of red dots
        self.dot_targets = {}  # Track which red dot is targeting which gold dot
        self.gold_dots = gold_dots
        self.silver_dots = silver_dots or []  # Track silver dots for interactions
        self.beehive_position = beehive_position
        self.last_beehive_position = (12, 2)
        self.max_gold_collected = max_gold_collected
        self.gold_collected = 0
        self.returning_dots = set()  # Track which dots are returning
        self.settled_dots = set()  # Track which dots have settled in the hive
        self.completed = False
        self.pond_position = pond_position
        self.pond_size = pond_size
        self.forbidden_zone_func = forbidden_zone_func
        self.avoidance_angle_offset = 1.2  # Larger avoidance offset
        
        # Add position history tracking for oscillation detection
        self.position_history = {}
        self.oscillation_count = {}
        self.bee_ids = {}
        
        # Track interactions with silver dots - move this BEFORE _assign_bee_ids call
        self.silver_dot_interactions = {}
        
        # Add a cycles counter to track how many nectar cycles completed
        self.cycles_completed = 0
        
        self._assign_bee_ids()
        
        print(f"Initializing simulation with {len(red_dots)} bees")
        
    def reset_for_new_cycle(self):
        """Reset the relevant state variables for a new nectar cycle"""
        self.gold_collected = 0
        self.returning_dots = set()  # Clear returning dots
        self.settled_dots = set()    # Clear settled dots
        self.dot_targets = {}        # Clear existing targets
        self.completed = False       # Reset completion state
        
        # Increment cycle counter
        self.cycles_completed += 1
        
        # We don't reset silver_dot_interactions so bees can stay enhanced
        # through multiple cycles
        print(f"Move state reset for nectar cycle {self.cycles_completed + 1}")
        
    def _assign_bee_ids(self):
        """Assign unique IDs to bees for tracking purposes"""
        for i, bee in enumerate(self.red_dots):
            self.bee_ids[i] = f"Bee-{i+1}"
            self.position_history[i] = []
            self.oscillation_count[i] = 0
            self.silver_dot_interactions[i] = 0
    
    def log_important_event(self, bee_index, message):
        """Log only important events to reduce output but maintain visibility"""
        # Only log events that are truly important, or if verbose mode is enabled
        if not DEBUG_VERBOSE and "🥈" in message:  # Silver interaction logs
            return  # Skip silver interactions unless verbose
            
        bee_id = self.bee_ids.get(bee_index, f"Bee-{bee_index}")
        print(f"{bee_id}: {message}")

    def detect_oscillation(self, bee_index, new_position):
        """Detect if a bee is oscillating (moving back and forth)"""
        history = self.position_history.get(bee_index, [])
        
        # Only check for oscillation with sufficient history
        if len(history) >= 5:
            # Check if new position is very close to a previous recent position
            for old_pos in history[-5:]:
                distance = math.hypot(old_pos[0] - new_position[0], old_pos[1] - new_position[1])
                if distance < 0.15:  # If very close to a recent position
                    self.oscillation_count[bee_index] = self.oscillation_count.get(bee_index, 0) + 1
                    
                    if self.oscillation_count[bee_index] >= 3:  # Consecutive oscillations detected
                        bee_id = self.bee_ids.get(bee_index, f"Bee-{bee_index}")
                        if DEBUG_VERBOSE:  # Only log if verbose
                            print(f"⚠️ {bee_id} oscillation detected! Breaking cycle with random movement")
                        self.oscillation_count[bee_index] = 0  # Reset counter
                        return True
                    return False
        
        # Update position history
        self.position_history[bee_index] = history + [new_position.copy()]
        
        # Keep history limited to prevent memory growth
        if len(self.position_history[bee_index]) > 20:
            self.position_history[bee_index] = self.position_history[bee_index][-20:]
            
        return False

    def move_towards(self, red_dot, target_position, step_size=0.4):
        # Apply speed modifier from silver dot interactions
        bee_index = None
        for i, dot in enumerate(self.red_dots):
            if dot is red_dot:
                bee_index = i
                break
        
        # Apply speed modifier if this bee has one
        if hasattr(red_dot, 'speed_modifier'):
            step_size *= red_dot.speed_modifier
        
        dx = target_position[0] - red_dot.position[0]
        dy = target_position[1] - red_dot.position[1]
        distance = math.hypot(dx, dy)

        if distance > 0:
            angle = math.atan2(dy, dx)
            
            # Calculate next position
            next_x = red_dot.position[0] + step_size * math.cos(angle)
            next_y = red_dot.position[1] + step_size * math.sin(angle)

            # Avoid pond
            if self.is_inside_pond(next_x, next_y):
                next_x, next_y = self.calculate_curved_detour(red_dot, angle, step_size)

            # Avoid forbidden zone
            if self.forbidden_zone_func and self.forbidden_zone_func(next_x, next_y):
                next_x, next_y = self.calculate_curved_detour(red_dot, angle, step_size)
            
            # Oscillation detection and correction
            if bee_index is not None:
                # Check for oscillation
                old_position = red_dot.position.copy()
                new_position = [next_x, next_y]
                
                is_oscillating = self.detect_oscillation(bee_index, new_position)
                
                if is_oscillating:
                    # Add randomization to break the cycle
                    random_angle = random.uniform(0, 2 * math.pi)
                    next_x = red_dot.position[0] + step_size * math.cos(random_angle)
                    next_y = red_dot.position[1] + step_size * math.sin(random_angle)
                    
                    # Check if this would put us in pond/forbidden zone and avoid if needed
                    if (self.is_inside_pond(next_x, next_y) or 
                            (self.forbidden_zone_func and self.forbidden_zone_func(next_x, next_y))):
                        # Try a different angle
                        random_angle = random.uniform(0, 2 * math.pi)
                        next_x = red_dot.position[0] + step_size * 1.5 * math.cos(random_angle)
                        next_y = red_dot.position[1] + step_size * 1.5 * math.sin(random_angle)
            
            # Update position
            red_dot.position = [next_x, next_y]
            
        return distance

    def check_silver_dot_interactions(self, red_dot, bee_index):
        """Check if a red dot has interacted with a silver dot"""
        if not self.silver_dots:
            return False
            
        # Define interaction distance
        interaction_distance = 0.6
        
        # Check distance to each silver dot
        for i, silver_dot in enumerate(self.silver_dots[:]):  # Use copy to allow removal
            sx, sy = silver_dot.position
            rx, ry = red_dot.position
            
            distance = math.hypot(sx - rx, sy - ry)
            
            if distance < interaction_distance:
                # Interaction with silver dot occurred
                changes = red_dot.interact_with_silver()
                self.log_important_event(bee_index, f"🥈 Interacted with silver dot! Growing larger, moving slower (Size: {changes['new_size']:.2f}, Speed: {changes['new_speed']:.2f})")
                
                # Remove the silver dot after interaction
                self.silver_dots.remove(silver_dot)
                return True
                
        return False

    def is_inside_pond(self, x, y):
        px, py = self.pond_position
        pw, ph = self.pond_size
        return px <= x <= px + pw and py <= y <= py + ph

    def calculate_curved_detour(self, red_dot, current_angle, step_size):
        # Randomize the avoidance angle a bit to prevent identical paths
        detour_angle = current_angle + self.avoidance_angle_offset + random.uniform(-0.3, 0.3)
        radius_multiplier = 2.0  # Wider arc around the obstacle
        new_x = red_dot.position[0] + step_size * radius_multiplier * math.cos(detour_angle)
        new_y = red_dot.position[1] + step_size * radius_multiplier * math.sin(detour_angle)
        return new_x, new_y

    def find_closest_gold_dot(self, red_dot):
        if not self.gold_dots:
            return None
            
        # Find gold dots that aren't being targeted by other red dots
        available_gold_dots = [g for g in self.gold_dots if g not in self.dot_targets.values()]
        
        # If all gold dots are targeted but there are still dots, let this dot target one too
        if not available_gold_dots and self.gold_dots:
            available_gold_dots = self.gold_dots
            
        if not available_gold_dots:
            return None
            
        return min(
            available_gold_dots,
            key=lambda g: math.hypot(g.position[0] - red_dot.position[0], g.position[1] - red_dot.position[1])
        )
        
    def are_all_nectar_collected(self):
        """Check if all nectar has been collected from the field"""
        return len(self.gold_dots) == 0 or self.gold_collected >= self.max_gold_collected

    def place_bee_in_hive(self, bee_index, red_dot):
        """Place the bee at a fixed position inside the hive"""
        # Place the bee within the hive at a specific location
        hive_x, hive_y = self.beehive_position
        
        # Create a grid position based on bee_index to neatly arrange bees
        row = bee_index // 3
        col = bee_index % 3
        
        # Calculate position within hive
        red_dot.position = [
            hive_x + 0.25 + (col * 0.25),  # Horizontal position
            hive_y + 0.25 + (row * 0.25)   # Vertical position
        ]
        
        # Remove from returning dots and add to settled dots
        if bee_index in self.returning_dots:
            self.returning_dots.remove(bee_index)
        
        self.settled_dots.add(bee_index)
        self.log_important_event(bee_index, "🏠 Settled in the hive")  # Simplified message

    def update_state(self):
        if self.completed:
            return

        # Check if we've collected all gold dots
        if self.gold_collected >= self.max_gold_collected:
            # Make sure all dots are returning if we've collected all gold
            for i in range(len(self.red_dots)):
                if i not in self.settled_dots and i not in self.returning_dots:
                    self.returning_dots.add(i)
            
            # Check if all dots have settled in the hive
            all_settled = True
            for i, red_dot in enumerate(self.red_dots):
                if i not in self.settled_dots:
                    all_settled = False
                    # If it's returning, move it to the hive
                    if i in self.returning_dots:
                        target = self.last_beehive_position
                        distance = self.move_towards(red_dot, target) 
                        
                        # If it's close to the hive, settle it
                        if distance < 0.6:
                            self.place_bee_in_hive(i, red_dot)
            
            if all_settled:
                self.completed = True
                print(f"\nCYCLE COMPLETED: All bees have settled in the hive with nectar: {self.gold_collected}/{self.max_gold_collected}")
            return
            
        # Process each red dot that hasn't settled yet
        for i, red_dot in enumerate(self.red_dots):
            # Skip bees that have already settled
            if i in self.settled_dots:
                continue
            
            # Check for interactions with silver dots
            self.check_silver_dot_interactions(red_dot, i)
                
            if i in self.returning_dots:
                # This dot is returning to beehive
                distance = self.move_towards(red_dot, self.beehive_position)
                
                if distance < 0.6:
                    # Log the successful return
                    self.log_important_event(i, f"✅ Returned to hive with nectar ({self.gold_collected}/{self.max_gold_collected})")
                    
                    # Remove from returning dots
                    self.returning_dots.remove(i)
                    
                    # Check if there are any nectar left to collect
                    if self.are_all_nectar_collected():
                        # All nectar collected, settle in the hive
                        self.place_bee_in_hive(i, red_dot)
                    else:
                        # Add a larger jump away from the hive with randomization to prevent getting stuck
                        jump_angle = random.uniform(0, 2 * math.pi)
                        jump_distance = random.uniform(0.8, 1.2)  # Randomize distance too
                        red_dot.position[0] += jump_distance * math.cos(jump_angle)
                        red_dot.position[1] += jump_distance * math.sin(jump_angle)
            else:
                # Find a target if this dot doesn't have one
                if i not in self.dot_targets or self.dot_targets[i] not in self.gold_dots:
                    gold_target = self.find_closest_gold_dot(red_dot)
                    if gold_target:
                        self.dot_targets[i] = gold_target
                        # Log targeting only occasionally to reduce spam
                        if random.random() < 0.3:  # 30% chance to log
                            target_pos = [round(p, 1) for p in gold_target.position]
                            self.log_important_event(i, f"🎯 Targeting nectar at {target_pos}")
                    else:
                        # No gold dots left to target, return to beehive
                        self.returning_dots.add(i)
                        self.log_important_event(i, "↩️ No more nectar targets, returning to hive")
                        continue
                
                # Move toward the target
                gold_target = self.dot_targets[i]
                if self.move_towards(red_dot, gold_target.position) < 0.6:
                    # Collected gold dot
                    self.log_important_event(i, f"✨ Collected nectar ({self.gold_collected+1}/{self.max_gold_collected})")
                    
                    self.gold_dots.remove(gold_target)
                    self.gold_collected += 1
                    self.dot_targets.pop(i)
                    self.returning_dots.add(i)
