# --- Class3.py ---
import math

class Move:
    def __init__(self, red_dot, gold_dots, beehive_position, max_gold_collected, pond_position, pond_size, forbidden_zone_func=None):
        self.red_dot = red_dot
        self.gold_dots = gold_dots
        self.beehive_position = beehive_position
        self.last_beehive_position = (12, 2)
        self.max_gold_collected = max_gold_collected
        self.gold_collected = 0
        self.returning_to_beehive = False
        self.completed = False
        self.pond_position = pond_position
        self.pond_size = pond_size
        self.forbidden_zone_func = forbidden_zone_func
        self.avoidance_angle_offset = 1.2  # Larger avoidance offset

    def move_towards(self, target_position, step_size=0.4):
        dx = target_position[0] - self.red_dot.position[0]
        dy = target_position[1] - self.red_dot.position[1]
        distance = math.hypot(dx, dy)

        if distance > 0:
            angle = math.atan2(dy, dx)
            next_x = self.red_dot.position[0] + step_size * math.cos(angle)
            next_y = self.red_dot.position[1] + step_size * math.sin(angle)

            # Avoid pond
            if self.is_inside_pond(next_x, next_y):
                next_x, next_y = self.calculate_curved_detour(angle, step_size)

            # Avoid forbidden zone
            if self.forbidden_zone_func and self.forbidden_zone_func(next_x, next_y):
                next_x, next_y = self.calculate_curved_detour(angle, step_size)

            self.red_dot.position = [next_x, next_y]
        return distance

    def is_inside_pond(self, x, y):
        px, py = self.pond_position
        pw, ph = self.pond_size
        return px <= x <= px + pw and py <= y <= py + ph

    def calculate_curved_detour(self, current_angle, step_size):
        detour_angle = current_angle + self.avoidance_angle_offset
        radius_multiplier = 2.0  # Wider arc around the obstacle
        new_x = self.red_dot.position[0] + step_size * radius_multiplier * math.cos(detour_angle)
        new_y = self.red_dot.position[1] + step_size * radius_multiplier * math.sin(detour_angle)
        return new_x, new_y

    def update_state(self):
        if self.completed:
            return

        if self.returning_to_beehive:
            target = self.last_beehive_position if self.gold_collected >= self.max_gold_collected else self.beehive_position
            if self.move_towards(target) < 0.6:
                if self.gold_collected >= self.max_gold_collected:
                    self.completed = True
                else:
                    self.returning_to_beehive = False
        else:
            # Collect the closest gold dot
            if self.gold_dots:
                closest = min(
                    self.gold_dots,
                    key=lambda g: math.hypot(g.position[0] - self.red_dot.position[0], g.position[1] - self.red_dot.position[1])
                )
                if self.move_towards(closest.position) < 0.6:
                    self.gold_dots.remove(closest)
                    self.gold_collected += 1
                    self.returning_to_beehive = True
