import random
import matplotlib.pyplot as plt
import math
import os


class QueenBeeDot:
    def __init__(self, position_x=None, position_y=None):
        self.position_x = position_x if position_x is not None else random.uniform(0, 15)
        self.position_y = position_y if position_y is not None else random.uniform(0, 15)

    def move_randomly(self, max_delta=0.2):
        delta_x = random.uniform(-max_delta, max_delta)
        delta_y = random.uniform(-max_delta, max_delta)
        self.position_x += delta_x
        self.position_y += delta_y
        self.position_x = max(0, min(self.position_x, 15))
        self.position_y = max(0, min(self.position_y, 15))

    def get_position(self):
        return self.position_x, self.position_y

    def __repr__(self):
        return f"QueenBeeDot(x={self.position_x:.2f}, y={self.position_y:.2f})"


class DroneDot:
    def __init__(self, position_x=None, position_y=None):
        self.position_x = position_x if position_x is not None else random.uniform(0, 15)
        self.position_y = position_y if position_y is not None else random.uniform(0, 15)
        self.queen_reference = None
        self.target_distance = 5.0
        self.state = "approaching"

    def approach_queen(self, queen_position, max_delta=0.7):
        queen_x, queen_y = queen_position
        direction_x = queen_x - self.position_x
        direction_y = queen_y - self.position_y
        distance = math.sqrt(direction_x**2 + direction_y**2)

        if distance > 0:
            direction_x /= distance
            direction_y /= distance

        self.position_x += direction_x * max_delta
        self.position_y += direction_y * max_delta
        self.position_x = max(0, min(self.position_x, 15))
        self.position_y = max(0, min(self.position_y, 15))

    def move_away_from_queen(self, max_delta=0.7):
        if not self.queen_reference:
            return
        queen_x, queen_y = self.queen_reference
        direction_x = self.position_x - queen_x
        direction_y = self.position_y - queen_y
        distance = math.sqrt(direction_x**2 + direction_y**2)

        if distance < self.target_distance:
            if distance == 0:
                direction_x, direction_y = 1, 0
            else:
                direction_x /= distance
                direction_y /= distance
            self.position_x += direction_x * max_delta
            self.position_y += direction_y * max_delta
            self.position_x = max(0, min(self.position_x, 15))
            self.position_y = max(0, min(self.position_y, 15))
        else:
            self.state = "waiting"

    def move_randomly(self, max_delta=0.3):
        delta_x = random.uniform(-max_delta, max_delta)
        delta_y = random.uniform(-max_delta, max_delta)
        self.position_x += delta_x
        self.position_y += delta_y
        self.position_x = max(0, min(self.position_x, 15))
        self.position_y = max(0, min(self.position_y, 15))

    def get_position(self):
        return self.position_x, self.position_y

    def __repr__(self):
        return f"DroneDot(x={self.position_x:.2f}, y={self.position_y:.2f}, state={self.state})"


class GoldDot:
    def __init__(self, position):
        self.position = position

    def get_position(self):
        return self.position

    def __repr__(self):
        x, y = self.position
        return f"GoldDot(x={x:.2f}, y={y:.2f})"


def distance_between(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


class Timestep:
    def __init__(self, interval=0.5, total_steps=60, save_dir="timesteps"):
        self.interval = interval
        self.total_steps = total_steps
        self.save_dir = save_dir

        # Create directory for saving images if it doesn't exist
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def simulate(self, queen_bee, drones):
        plt.ion()
        fig, ax = plt.subplots()
        queen_scatter = ax.scatter(*queen_bee.get_position(), color="blue", label="Queen Bee")
        drone_scatters = [
            ax.scatter(*drone.get_position(), color="black", label="Drone" if i == 0 else None)
            for i, drone in enumerate(drones)
        ]
        gold_scatters = []
        ax.set_xlim(0, 15)
        ax.set_ylim(0, 15)
        ax.set_title("Queen Bee and Drones (Gold Loop)")
        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        ax.legend()

        interaction_radius = 1.5
        random_move_timer = 0

        for step in range(self.total_steps):
            queen_bee.move_randomly(max_delta=0.2)
            queen_scatter.set_offsets([queen_bee.get_position()])

            for i, drone in enumerate(drones):
                scatter = drone_scatters[i]

                if drone.state == "approaching":
                    drone.approach_queen(queen_bee.get_position(), max_delta=0.6)
                    if distance_between(drone.get_position(), queen_bee.get_position()) <= interaction_radius:
                        drone.state = "ready_for_gold"

                elif drone.state == "moving_away":
                    drone.move_away_from_queen(max_delta=0.7)

                elif drone.state == "waiting":
                    drone.move_randomly(max_delta=0.3)

                scatter.set_offsets([drone.get_position()])

            if all(drone.state == "ready_for_gold" for drone in drones):
                gold_scatter = ax.scatter(*queen_bee.get_position(), color="gold", marker="o", s=20, label="Gold Dot")
                gold_scatters.append(gold_scatter)
                print(f"\n🎉 Gold Dot Generated at: {queen_bee.get_position()}")
                for drone in drones:
                    drone.queen_reference = queen_bee.get_position()
                    drone.state = "moving_away"

            if all(drone.state == "waiting" for drone in drones):
                random_move_timer += 1
                if random_move_timer >= 5:
                    for drone in drones:
                        drone.state = "approaching"
                    random_move_timer = 0

            print(f"\nStep {step + 1}: Queen Bee: {queen_bee}")
            for i, drone in enumerate(drones):
                print(f"Drone {i + 1}: {drone}")

            # Save the current figure as a PNG file after each step
            step_filename = f"{self.save_dir}/timestep_{step + 1}.png"
            plt.savefig(step_filename)

            plt.pause(self.interval)

        plt.ioff()
        plt.show()


def run_simulation():
    queen_bee = QueenBeeDot()
    print(f"Initial Position: {queen_bee}")

    drones = [DroneDot() for _ in range(4)]
    print("Initial Drone Positions:")
    for i, drone in enumerate(drones):
        print(f"Drone {i + 1}: {drone}")

    timestep = Timestep(interval=0.5, total_steps=60)
    timestep.simulate(queen_bee, drones)


if __name__ == "__main__":
    run_simulation() 