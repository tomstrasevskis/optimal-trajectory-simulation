import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Default constants
default_bus_speed = 270  # Speed of the bus (B) in units/second
default_glider_speed = 110  # Speed of the glider (A) in units/second
default_target_x = 2000  # Target x-coordinate
default_target_y = -1500  # Target y-coordinate
default_num_angles = 200  # Number of angles to test
map_width = 5000  # Width of the map
map_height = 5000  # Height of the map
bus_start_x = 0  # Initial x-coordinate of the bus
bus_y = 0  # Y-coordinate of the bus (constant)
time_step = 0.1  # Simulation time step in seconds

# Get user inputs with defaults
try:
    bus_speed = float(input(f"Enter bus speed (default {default_bus_speed}): ") or default_bus_speed)
    glider_speed = float(input(f"Enter glider speed (default {default_glider_speed}): ") or default_glider_speed)
    target_x = float(input(f"Enter target x-coordinate (default {default_target_x}): ") or default_target_x)
    target_y = float(input(f"Enter target y-coordinate (default {default_target_y}): ") or default_target_y)
    num_angles = int(input(f"Enter number of angles to test (default {default_num_angles}): ") or default_num_angles)
except ValueError:
    print("Invalid input detected. Using default values.")
    bus_speed = default_bus_speed
    glider_speed = default_glider_speed
    target_x = default_target_x
    target_y = default_target_y
    num_angles = default_num_angles

# Entity class
class Entity:
    def __init__(self, angle, jump_time):
        self.angle = angle
        self.jump_time = jump_time
        self.x = 0
        self.y = bus_y
        self.state = "bus"
        self.time = 0
        self.reached_target = False

    def update(self, bus_x):
        if self.reached_target:
            return

        if self.time < self.jump_time:
            self.x = bus_x
            self.state = "bus"
        elif self.state == "bus":
            self.state = "glide"
        elif self.state == "glide":
            dir_x = target_x - self.x
            dir_y = target_y - self.y
            distance = np.hypot(dir_x, dir_y)
            if distance > 0:
                self.x += glider_speed * (dir_x / distance) * time_step
                self.y += glider_speed * (dir_y / distance) * time_step

        if self.distance_to_target() < 1.0:
            self.reached_target = True
            global first_to_target_time, optimal_angle
            if self.time < first_to_target_time:
                first_to_target_time = self.time
                optimal_angle = self.angle

        self.time += time_step

    def distance_to_target(self):
        return np.hypot(self.x - target_x, self.y - target_y)

# Simulation Variables
entities = []
optimal_angle = None
first_to_target_time = float('inf')

# Create entities for each angle
jump_angles = np.linspace(0, np.pi / 2, num_angles)
for angle in jump_angles:
    slope = np.cos(angle)
    jump_time = (target_x - bus_start_x) / bus_speed - slope * target_x / (bus_speed + glider_speed)
    jump_time = max(0, jump_time)
    entities.append(Entity(angle, jump_time))

# Real-time visualization
fig, ax = plt.subplots()
fig.patch.set_facecolor('#000000')  # Black window background
ax.set_xlim(0, map_width)
ax.set_ylim(-map_height // 2, map_height // 2)
ax.set_aspect('equal')
ax.plot(target_x, target_y, 'ro', label="Target", markersize=10)  # Target point
bus_marker, = ax.plot([], [], 'co', label="Bus", markersize=8)  # Cyan for bus
entity_markers = [ax.plot([], [], 'mo', markersize=4)[0] for _ in entities]  # Magenta for entities
time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=12, color='white')
optimal_text = ax.text(0.02, 0.90, '', transform=ax.transAxes, fontsize=12, color='white')
ax.grid(color='gray', linestyle='--', linewidth=0.5)
ax.set_facecolor('#202020')  # Dark background
ax.spines['bottom'].set_color('white')
ax.spines['left'].set_color('white')
ax.xaxis.label.set_color('white')
ax.yaxis.label.set_color('white')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.legend(facecolor='#404040', edgecolor='white', labelcolor='white')

# Update function for animation
bus_x = bus_start_x

def update(frame):
    global bus_x
    time = frame * time_step
    bus_x += bus_speed * time_step

    bus_marker.set_data([bus_x], [bus_y])

    for i, entity in enumerate(entities):
        entity.update(bus_x)
        entity_markers[i].set_data([entity.x], [entity.y])

    if optimal_angle is not None:
        optimal_text.set_text(f"Optimal Angle: {np.degrees(optimal_angle):.1f}°")
    time_text.set_text(f"Time: {time:.1f}s")

    return [bus_marker, *entity_markers, time_text, optimal_text]

# Run animation
ani = FuncAnimation(fig, update, frames=60, interval=100, blit=False)
plt.show()