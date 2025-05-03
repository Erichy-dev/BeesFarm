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
        self.red_dot = None
        self.gold_dots = []
        self.spawn = spawn
        self.pond = None

    def add_beehive(self, position=(5, 5), height=2, width=3):
        self.beehive = {"position": position, "height": height, "width": width}

    def add_red_dot(self):
        if self.beehive:
            hive_x, hive_y = self.beehive["position"]
            hive_width = self.beehive["width"]
            hive_height = self.beehive["height"]
            dot_x = hive_x + hive_width / 2
            dot_y = hive_y + hive_height / 2
        else:
            dot_x = random.uniform(0, self.block_size)
            dot_y = random.uniform(0, self.block_size)
        self.red_dot = CircleDot((dot_x, dot_y))

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
