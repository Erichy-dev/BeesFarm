# --- Class3.py ---
import math

class Move:
    def __init__(self, red_dots, gold_dots, beehive_position, max_gold_collected, pond_position, pond_size, forbidden_zone_func=None):
        self.red_dots = red_dots  # Now a list of red dots
        self.dot_targets = {}  # Track which red dot is targeting which gold dot
        self.gold_dots = gold_dots
        self.beehive_position = beehive_position
        self.last_beehive_position = (12, 2)
        self.max_gold_collected = max_gold_collected
        self.gold_collected = 0
        self.returning_dots = set()  # Track which dots are returning
        self.completed = False
        self.pond_position = pond_position
        self.pond_size = pond_size
        self.forbidden_zone_func = forbidden_zone_func
        self.avoidance_angle_offset = 1.2  # Larger avoidance offset

    def move_towards(self, red_dot, target_position, step_size=0.4):
        dx = target_position[0] - red_dot.position[0]
        dy = target_position[1] - red_dot.position[1]
        distance = math.hypot(dx, dy)

        if distance > 0:
            angle = math.atan2(dy, dx)
            next_x = red_dot.position[0] + step_size * math.cos(angle)
            next_y = red_dot.position[1] + step_size * math.sin(angle)

            # Avoid pond
            if self.is_inside_pond(next_x, next_y):
                next_x, next_y = self.calculate_curved_detour(red_dot, angle, step_size)

            # Avoid forbidden zone
            if self.forbidden_zone_func and self.forbidden_zone_func(next_x, next_y):
                next_x, next_y = self.calculate_curved_detour(red_dot, angle, step_size)

            red_dot.position = [next_x, next_y]
        return distance

    def is_inside_pond(self, x, y):
        px, py = self.pond_position
        pw, ph = self.pond_size
        return px <= x <= px + pw and py <= y <= py + ph

    def calculate_curved_detour(self, red_dot, current_angle, step_size):
        detour_angle = current_angle + self.avoidance_angle_offset
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

    def update_state(self):
        if self.completed:
            return

        # Check if we've collected all gold dots
        if self.gold_collected >= self.max_gold_collected:
            # Make sure all dots are returning if we've collected all gold
            self.returning_dots = set(range(len(self.red_dots)))
            
            # Check if all dots have made it back to the beehive
            all_back = True
            for i, red_dot in enumerate(self.red_dots):
                target = self.last_beehive_position
                if self.move_towards(red_dot, target) >= 0.6:
                    all_back = False
            
            if all_back:
                self.completed = True
            return
            
        # Process each red dot
        for i, red_dot in enumerate(self.red_dots):
            if i in self.returning_dots:
                # This dot is returning to beehive
                if self.move_towards(red_dot, self.beehive_position) < 0.6:
                    # Reached beehive, now ready to go out again
                    self.returning_dots.remove(i)
            else:
                # Find a target if this dot doesn't have one
                if i not in self.dot_targets or self.dot_targets[i] not in self.gold_dots:
                    gold_target = self.find_closest_gold_dot(red_dot)
                    if gold_target:
                        self.dot_targets[i] = gold_target
                    else:
                        # No gold dots left to target, return to beehive
                        self.returning_dots.add(i)
                        continue
                
                # Move toward the target
                gold_target = self.dot_targets[i]
                if self.move_towards(red_dot, gold_target.position) < 0.6:
                    # Collected gold dot
                    self.gold_dots.remove(gold_target)
                    self.gold_collected += 1
                    self.dot_targets.pop(i)
                    self.returning_dots.add(i)
