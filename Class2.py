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
            
            # Calculate spawn regions within beehive
            regions = []
            if count <= 4:
                # Divide beehive into regions based on count
                region_width = hive_width / (count ** 0.5)
                region_height = hive_height / (count ** 0.5)
                
                for i in range(min(2, count)):
                    for j in range((count+1)//2):
                        if len(regions) < count:
                            region_x = hive_x + i * region_width
                            region_y = hive_y + j * region_height
                            regions.append((region_x, region_y, region_width, region_height))
            
            # If we couldn't create regions (shouldn't happen), fall back to default
            if not regions:
                regions = [(hive_x, hive_y, hive_width, hive_height)] * count
                
            # Place dots in different regions with some randomness
            for i in range(count):
                region_x, region_y, region_w, region_h = regions[i % len(regions)]
                
                # Add randomness within the region
                offset_x = random.uniform(0.2, 0.8) * region_w
                offset_y = random.uniform(0.2, 0.8) * region_h
                
                dot_x = region_x + offset_x
                dot_y = region_y + offset_y
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
