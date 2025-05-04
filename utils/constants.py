# Constants used across the application

# Debug verbosity control
DEBUG_VERBOSE = False  # Set to True for verbose output

# Define constant parameters for the hexagon grid
HEX_SIZE = 1
COLS = 10
ROWS = 5
OFFSET_X = 1.5 * HEX_SIZE
OFFSET_Y = 1.732 * HEX_SIZE  # sqrt(3)

# Define simulation speed parameters
FPS = 5  # Frames per second (determines animation interval)
SIMULATION_SPEED = 1.0/FPS  # Seconds per frame - synchronized with FPS for real-time accuracy

# Define the waiting period between nectar cycles (in seconds)
WAIT_BETWEEN_CYCLES = 10.0  # Increased from 5 to 10 seconds 