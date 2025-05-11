import csv

def read_para_csv(file_name):
    defaults = {}
    try:
        with open(file_name, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) == 2:
                    key, value = row
                    defaults[key.strip()] = int(value.strip())
    except FileNotFoundError:
        print(f"")
    return(
        defaults.get("num_houses", 4),
        defaults.get("num_red_dots", 1)
    )

def read_map_csv(file_name):
    values = {}
    try:
        with open(file_name, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) == 2:
                    key, value = row
                    values[key.strip()] = int(value.strip())
    except FileNotFoundError:
        print(f".")
    return (
        values.get("num_drone_bees", 2),
        values.get("timesteps", 100)
    )

# Function for batch mode (automatically reading from CSV files)
def batch_mode(terrain_file, parameters_file):
    print("\033[95m Welcome to Beehive Batch Mode!!!\033[0m")
    print("Entering batch mode... Reading from", terrain_file, "and", parameters_file)
    num_houses, num_red_dots = read_para_csv(parameters_file)
    num_drone_bees, max_timesteps = read_map_csv(terrain_file)
    print(f"Batch Mode: Houses: {num_houses}, Worker Bees (Red Dots): {num_red_dots}, Drone Bees: {num_drone_bees}, Timesteps: {max_timesteps}")
    return num_houses, num_red_dots, num_drone_bees, max_timesteps  # Return these values

# Function for interactive mode (manual input)
def interactive_mode():
    print("\033[92m Welcome to Beehive Simulation Interactive Mode ! \033[0m ")
    # Read default parameters from CSV files
    num_houses, num_red_dots = read_para_csv("para1.csv")
    num_drone_bees, max_timesteps = read_map_csv("map1.csv")

    # Interactive input for houses
    while True:
        user_input = input(f"How many houses do you want (1 to 4)? (Batch Mode: {num_houses}): ")
        if user_input == "":
            print(f"Using default value for houses: {num_houses}")
            break
        try:
            num_houses = int(user_input)
            if 1 <= num_houses <= 4:
                print(f"You have chosen {num_houses} houses.")
                break
            else:
                print("Error: Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please try again.")

    # Interactive input for worker bees (red dots)
    while True:
        user_input = input(f"How many worker bees (red dots) do you want (1 to 4)? (Batch Mode: {num_red_dots}): ")
        if user_input == "":
            print(f"Using default value for worker bees: {num_red_dots}")
            break
        try:
            num_red_dots = int(user_input)
            if 1 <= num_red_dots <= 4:
                print(f"You have chosen {num_red_dots} red dots (worker bees).")
                break
            else:
                print("Error: Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please try again.")

    # Interactive input for drone bees (black dots)
    while True:
        user_input = input(f"How many drone bees (black dots) do you want (1 to 4)? (Batch Mode: {num_drone_bees}): ")
        if user_input == "":
            print(f"Using default value for drone bees: {num_drone_bees}")
            break
        try:
            num_drone_bees = int(user_input)
            if 1 <= num_drone_bees <= 4:
                print(f"You have chosen {num_drone_bees} black dots (drone bees).")
                break
            else:
                print("Error: Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please try again.")

    # Interactive input for simulation timesteps
    while True:
        user_input = input(f"How many simulation timesteps do you want (10-1000)? (Batch Mode: {max_timesteps}): ")
        if user_input == "":
            print(f"Using default value for timesteps: {max_timesteps}")
            break
        try:
            timesteps = int(user_input)
            if 10 <= timesteps <= 1000:
                max_timesteps = timesteps
                print(f"You have chosen {max_timesteps} timesteps.")
                break
            else:
                print("Error: Please enter a number between 10 and 1000.")
        except ValueError:
            print("Invalid input. Please try again.")
    return num_houses, num_red_dots, num_drone_bees, max_timesteps  # Return these values
    print(f"Interactive Mode: Houses: {num_houses}, Worker Bees (Red Dots): {num_red_dots}, Drone Bees: {num_drone_bees}, Timesteps: {max_timesteps}") 