# --- Class2.py ---
import random

class CircleDot:
    def __init__(self, position):
        self.position = list(position)
        # Add properties for task 2 - growing and slowing when interacting with silver dots
        self.original_size = 0.1  # Default size for red dots
        self.current_size = self.original_size
        self.speed_modifier = 1.0  # Default speed (normal)
        self.silver_interactions = 0  # Count interactions with silver dots
        self.max_size = 0.35  # Maximum size a dot can grow to (adjusted from 0.5)

    def interact_with_silver(self):
        """Called when this dot interacts with a silver dot."""
        self.silver_interactions += 1
        # Increase size by 50% per interaction, up to a maximum (adjusted from 70%)
        size_increase = min(1.5 ** self.silver_interactions, self.max_size / self.original_size)
        self.current_size = self.original_size * size_increase
        
        # Slow down by 25% per interaction, to a minimum of 25% speed
        self.speed_modifier = max(0.25, 1.0 - (0.25 * self.silver_interactions))
        
        return {
            "new_size": self.current_size,
            "new_speed": self.speed_modifier
        }

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
        
        # Log flower locations for debugging
        print("\n🌸 Flower areas where nectar can generate:")
        for i, area in enumerate(flower_areas):
            x0, y0 = area["position"]
            width, height = area["width"], area["height"]
            # Check for any overlap with forbidden zone
            has_overlap = False
            for check_x in range(x0, x0 + width + 1):
                for check_y in range(y0, y0 + height + 1):
                    if is_in_forbidden_zone(check_x, check_y):
                        has_overlap = True
                        break
                if has_overlap:
                    break
                
            overlap_status = "⚠️ WARNING: overlaps with forbidden zone" if has_overlap else "OK"
            print(f"  {i+1}. {area['name']} at position {area['position']} (width: {area['width']}, height: {area['height']}) - {overlap_status}")
        
        # Keep track of flowers that generated nectar
        flowers_with_nectar = []
        
        # Randomly select which flowers will have nectar
        # Shuffle the flower areas to add randomness
        random.shuffle(flower_areas)
        
        # Determine how many flowers will have nectar (at least 1, at most all)
        flowers_with_nectar_count = min(count, len(flower_areas))
        flowers_with_nectar_count = max(1, flowers_with_nectar_count)
        
        # Generate nectar at selected flower locations
        dots_to_generate = count
        flowers_used = flower_areas[:flowers_with_nectar_count]
        
        # First, ensure each selected flower has at least one nectar
        for area in flowers_used:
            x0, y0 = area["position"]
            width, height = area["width"], area["height"]
            
            # Try multiple times to find a valid position
            max_attempts = 10
            for attempt in range(max_attempts):
                # Generate a random position within the flower area
                dot_x = x0 + random.randint(0, width - 1) + 0.5
                dot_y = y0 + random.randint(0, height - 1) + 0.5
                
                # Check if this position is in the forbidden zone
                if not is_in_forbidden_zone(dot_x, dot_y):
                    # Valid position found
                    self.gold_dots.append(CircleDot((dot_x, dot_y)))
                    dots_to_generate -= 1
                    flowers_with_nectar.append(area["name"])
                    break
                
                if attempt == max_attempts - 1:
                    print(f"⚠️ WARNING: Could not find valid position for nectar in {area['name']} after {max_attempts} attempts")
        
        # Distribute remaining nectar among the selected flowers
        while dots_to_generate > 0:
            # Pick a random flower from the selected ones
            area = random.choice(flowers_used)
            x0, y0 = area["position"]
            width, height = area["width"], area["height"]
            
            # Try multiple times to find a valid position
            max_attempts = 10
            for attempt in range(max_attempts):
                # Generate a random position within the flower area
                dot_x = x0 + random.randint(0, width - 1) + 0.5
                dot_y = y0 + random.randint(0, height - 1) + 0.5
                
                # Check if this position is in the forbidden zone
                if not is_in_forbidden_zone(dot_x, dot_y):
                    # Valid position found
                    self.gold_dots.append(CircleDot((dot_x, dot_y)))
                    dots_to_generate -= 1
                    break
                
                if attempt == max_attempts - 1:
                    print(f"⚠️ WARNING: Could not find valid position for nectar in {area['name']} after {max_attempts} attempts")
                    # Skip this dot if we can't find a valid position
                    dots_to_generate -= 1
        
        # Log which flowers generated nectar and how many
        print("\n🍯 Nectar generation results:")
        nectar_counts = {}
        for dot in self.gold_dots:
            x, y = dot.position
            # Check that this dot is not in the forbidden zone
            if is_in_forbidden_zone(x, y):
                print(f"⚠️ ERROR: Nectar point at {dot.position} is in the forbidden zone!")
                continue
            
            for area in flower_areas:
                x0, y0 = area["position"]
                width, height = area["width"], area["height"]
                if (x0 <= x <= x0 + width) and (y0 <= y <= y0 + height):
                    if area["name"] not in nectar_counts:
                        nectar_counts[area["name"]] = 0
                    nectar_counts[area["name"]] += 1
                    break
        
        # Print results
        for name, count in nectar_counts.items():
            print(f"  - {name}: {count} nectar points")
        
        print(f"  Total: {len(self.gold_dots)} nectar points generated across {len(nectar_counts)} flower areas")
        
        return self.gold_dots

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
