# --- Class2.py ---
import random

class CircleDot:
    def __init__(self, position):
        self.position = list(position)

class Object:
    def __init__(self, block_size=15, spawn=None):
        self.block_size = block_size
        self.beehive = None
        self.silver_dots = []
        self.red_dots = []
        self.gold_dots = []
        self.spawn = spawn
        self.pond = None

    def add_beehive(self, position=(5, 5), height=2, width=3):
        self.beehive = {"position": position, "height": height, "width": width}

    def add_red_dots(self, count=1):
        if self.beehive:
            hive_x, hive_y = self.beehive["position"]
            hive_width = self.beehive["width"]
            hive_height = self.beehive["height"]
            
            # Expanded positioning for up to 10 bees in a larger grid pattern
            preset_positions = [
                # First row (4 positions)
                (0.2, 0.2), (0.4, 0.2), (0.6, 0.2), (0.8, 0.2),
                # Second row (3 positions)
                (0.3, 0.5), (0.5, 0.5), (0.7, 0.5),
                # Third row (3 positions)
                (0.3, 0.8), (0.5, 0.8), (0.7, 0.8)
            ]
            
            for i in range(min(count, len(preset_positions))):
                rel_x, rel_y = preset_positions[i]
                # Apply to the beehive dimensions
                dot_x = hive_x + rel_x * hive_width
                dot_y = hive_y + rel_y * hive_height
                
                # Add some small randomness
                dot_x += random.uniform(-0.1, 0.1)
                dot_y += random.uniform(-0.1, 0.1)
                
                self.red_dots.append(CircleDot((dot_x, dot_y)))
                
            # If more bees requested than preset positions, add them with general spacing
            if count > len(preset_positions):
                for i in range(len(preset_positions), count):
                    dot_x = hive_x + random.uniform(0.2, 0.8) * hive_width
                    dot_y = hive_y + random.uniform(0.2, 0.8) * hive_height
                    self.red_dots.append(CircleDot((dot_x, dot_y)))
        else:
            # If no beehive, place dots with spacing across the grid
            existing_positions = []
            min_distance = 2.0  # Minimum distance between dots
            
            for _ in range(count):
                attempts = 0
                while attempts < 20:  # Limit attempts to prevent infinite loop
                    dot_x = random.uniform(1, self.block_size-1)
                    dot_y = random.uniform(1, self.block_size-1)
                    
                    # Check if this position is far enough from other dots
                    if all(((x-dot_x)**2 + (y-dot_y)**2)**0.5 > min_distance 
                          for x, y in existing_positions):
                        existing_positions.append((dot_x, dot_y))
                        self.red_dots.append(CircleDot((dot_x, dot_y)))
                        break
                    
                    attempts += 1
                
                # If we couldn't find a good spot after max attempts, just place it
                if attempts >= 20 and len(self.red_dots) < count:
                    dot_x = random.uniform(1, self.block_size-1)
                    dot_y = random.uniform(1, self.block_size-1)
                    self.red_dots.append(CircleDot((dot_x, dot_y)))

    def add_red_dot(self):
        self.add_red_dots(1)
        return self.red_dots[0]

    def _generate_gold_dot(self, spawn_x, spawn_y, width, height):
        dot_x = random.randint(spawn_x, spawn_x + width - 1)
        dot_y = random.randint(spawn_y, spawn_y + height - 1)
        return CircleDot((dot_x + 0.5, dot_y + 0.5))

    def add_gold_dots(self, count=10):
        spawn_areas = [
            {"position": (1, 4), "width": 3, "height": 3},
            {"position": (1, 11), "width": 3, "height": 3},
            {"position": (7, 4), "width": 3, "height": 3},
            {"position": (7, 11), "width": 3, "height": 3}
        ]
        for area in spawn_areas:
            x0, y0 = area["position"]
            for _ in range(random.randint(1, 5)):
                self.gold_dots.append(self._generate_gold_dot(x0, y0, area["width"], area["height"]))

    def add_silver_dots(self):
        # Define the excluded spawn areas
        excluded_areas = [
            (range(1, 4), range(7, 10)),
            (range(4, 7), range(10, 14)),  # Area 2
            (range(7, 10), range(7, 10)),
            (range(4, 7), range(4, 7)),    # Area 4
        ]

        # Randomly spawn 1 to 5 silver dots in each excluded area
        for area in excluded_areas:
            num_silver_dots = random.randint(1, 5)
            for _ in range(num_silver_dots):
                x_range, y_range = area
                x = random.choice(x_range)
                y = random.choice(y_range)
                self.silver_dots.append(CircleDot((x + 0.5, y + 0.5)))

    def add_pond(self, position, height, width):
        self.pond = {"position": position, "height": height, "width": width}
