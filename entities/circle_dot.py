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