import matplotlib.pyplot as plt

class Spawn:
    def __init__(self, position=(1, 4), height=10, width=9):
        self.position = position
        self.height = height
        self.width = width

    def is_within_spawn(self, x, y):
        spawn_x, spawn_y = self.position
        return spawn_x <= x <= spawn_x + self.width and spawn_y <= y <= spawn_y + self.height

class House:
    def __init__(self, pos, height, width):
        self.pos = pos
        self.height = height
        self.width = width

    def get_square_patch(self):
        x, y = self.pos
        return plt.Rectangle((x, y), self.width, self.height, color='Blue')

    def get_triangle_marker(self):
        x, y = self.pos
        return x + self.width / 2, y + self.height / 2

class Fence:
    def __init__(self, vertical_start, vertical_end, horizontal_start, horizontal_end):
        self.vertical_start = vertical_start
        self.vertical_end = vertical_end
        self.horizontal_start = horizontal_start
        self.horizontal_end = horizontal_end

    def plot_fence(self, ax, label=None):
        x_v = [self.vertical_start[0], self.vertical_end[0]]
        y_v = [self.vertical_start[1], self.vertical_end[1]]
        ax.plot(x_v, y_v, marker='*', linestyle='--', color='chocolate', label=label or "_nolegend_")

        x_h = [self.horizontal_start[0], self.horizontal_end[0]]
        y_h = [self.horizontal_start[1], self.horizontal_end[1]]
        ax.plot(x_h, y_h, marker='*', linestyle='--', color='chocolate')

class Tree:
    def __init__(self, position, width, height):
        self.position = position
        self.width = width
        self.height = height

    def plot_trees(self, ax):
        start_x, start_y = self.position
        for x in range(start_x, start_x + self.width):
            for y in range(start_y, start_y + self.height):
                ax.text(x + 0.5, y + 0.5, '\u25BC', color='green', fontsize=15, ha='center', va='center') 
