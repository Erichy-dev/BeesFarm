import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from entities.object_manager import ObjectManager
from entities.environment import Spawn, House, Fence, Tree

class Landscape:
    def __init__(self, block_size=15, max_gold_collected=5, num_houses=1):
        self.block_size = block_size
        self.grid = np.ones((block_size, block_size)) * 5
        self.max_gold_collected = max_gold_collected
        self.spawn = Spawn(position=(1, 4), height=10, width=9)

        # Initialize the objects
        self.objects = ObjectManager(block_size, self.spawn)

        self.movement = None
        self.house = [House(pos=(0.5 + 2*i, 0.5), height=1, width=1) for i in range(num_houses)]
        self.fence_1 = Fence((11.5, 4.5), (11.5, 15.5), (11.5, 4.5), (15.5, 4.5))
        self.fence_2 = Fence((8.5, 2.5), (8.5, 0), (8.5, 2.5), (0, 2.5))
        self.tree_area = Tree(position=(12, 11), width=3, height=4)

    def is_inside_forbidden_zone(self, x, y):
        # Circle-based forbidden zone check
        forbidden_center_x, forbidden_center_y = 5.5, 8.5
        forbidden_radius = 1.5
        distance_from_center = np.hypot(x - forbidden_center_x, y - forbidden_center_y)
        return distance_from_center <= forbidden_radius

    def is_in_excluded_spawn_area(self, x, y):
        excluded_areas = [
            (range(1, 4), range(7, 10)),
            (range(4, 7), range(10, 14)),
            (range(7, 10), range(7, 10)),
            (range(4, 7), range(4, 7)),
            (range(4, 7), range(7, 10)),  # flower zone
        ]
        return any(x in xr and y in yr for xr, yr in excluded_areas)

    def display(self, fig=None, subplot_spec=None, title=None):
        if fig is None and subplot_spec is None:
            fig, ax = plt.subplots(figsize=(8, 8))
        else:
            ax = fig.add_subplot(subplot_spec)
            
        extent = [0, self.block_size, 0, self.block_size]
        ax.imshow(self.grid.T, cmap="Dark2", extent=extent)
        ax.set_aspect('equal')
        ax.grid(True, which='both', color='white', linestyle='--', linewidth=0.5, alpha=0.6)
        ax.set_xticks(np.arange(0, self.block_size + 1, 1))
        ax.set_yticks(np.arange(0, self.block_size + 1, 1))

        # Spawn area
        spawn_x, spawn_y = self.spawn.position
        for x in range(spawn_x, spawn_x + self.spawn.width):
            for y in range(spawn_y, spawn_y + self.spawn.height):
                if not self.is_inside_forbidden_zone(x, y) and not self.is_in_excluded_spawn_area(x, y):
                    ax.text(x + 0.5, y + 0.5, '\u2605', color='pink', fontsize=30, ha='center', va='center')

        self.tree_area.plot_trees(ax)

        if self.objects.beehive:
            bx, by = self.objects.beehive["position"]
            bw = self.objects.beehive["width"]
            bh = self.objects.beehive["height"]
            ax.add_patch(plt.Rectangle((bx, by), bw, bh, color='brown', label="Beehive"))

        if self.objects.pond:
            px, py = self.objects.pond["position"]
            pw = self.objects.pond["width"]
            ph = self.objects.pond["height"]
            ax.add_patch(plt.Rectangle((px, py), pw, ph, color='cornflowerblue', label="Pond"))

        # Forbidden zone as a circle
        forbidden_circle = plt.Circle((5.5, 8.5), 1.5, color='lightgreen', label='Forbidden Zone')
        ax.add_patch(forbidden_circle)

        # Create red dots (worker bees)
        red_circles = []
        for i, red_dot in enumerate(self.objects.red_dots):
            label = "Worker Bee" if i == 0 else "_nolegend_"
            red_circle = plt.Circle(red_dot.position, radius=0.1, color='red', label=label)
            ax.add_patch(red_circle)
            red_circles.append(red_circle)

        # Fix silver dots - only add label to the first one
        for i, silver_dot in enumerate(self.objects.silver_dots):
            label = "Silver Dot" if i == 0 else "_nolegend_"
            ax.plot(silver_dot.position[0], silver_dot.position[1], 'o', color='silver', markersize=5, label=label)

        gold_circles = []
        for i, gold_dot in enumerate(self.objects.gold_dots):
            x, y = gold_dot.position
            label = "Nectar" if i == 0 else "_nolegend_"
            circle = plt.Circle((x, y), radius=0.2, color='gold', label=label)
            ax.add_patch(circle)
            gold_circles.append(circle)

        for i, house in enumerate(self.house):
            square = house.get_square_patch()
            triangle_x, triangle_y = house.get_triangle_marker()
            ax.add_patch(square)
            ax.plot(triangle_x, triangle_y, 'r^', markersize=10, label="House Roof" if i == 0 else "_nolegend_")

        self.fence_1.plot_fence(ax, label="Fence")
        self.fence_2.plot_fence(ax)

        gold_text = ax.text(0.02, 0.95, f'Nectar Collected: 0/{self.max_gold_collected}', transform=ax.transAxes)

        def update(frame):
            if self.movement and self.movement.completed:
                # Don't call stop() - it can cause animation errors
                # Just return the artists without updating
                return *red_circles, *gold_circles, gold_text

            if self.movement:
                self.movement.update_state()
                
                # Update all red dot positions
                for i, red_dot in enumerate(self.objects.red_dots):
                    if i < len(red_circles):
                        red_circles[i].center = red_dot.position
                
                # Update gold dot positions
                for i, gold_dot in enumerate(self.objects.gold_dots):
                    if i < len(gold_circles):
                        gold_circles[i].center = gold_dot.position
                
                gold_text.set_text(f'Nectar Collected: {self.movement.gold_collected}/{self.max_gold_collected}')
                return *red_circles, *gold_circles, gold_text

        ani = animation.FuncAnimation(fig, update, frames=1000, blit=True, interval=200)
        # Store animation reference to prevent garbage collection
        self._animation = ani
        
        ax.plot(7.5, 4.5, 's', color='pink', markersize=10, label="Flower")
        if title:
            ax.set_title(title)
        ax.set_xlim(0, self.block_size)
        ax.set_ylim(0, self.block_size)
        ax.set_xlabel("X Position")
        ax.set_ylabel("Y Position")
        ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
        
        if fig is None:
            plt.show() 