import pygame
import random
import time
import csv
from datetime import datetime
from osc_handler import OSCHandler

# Constants
CELL_SIZE = 300
GRID_SIZE = 3
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE
WHITE = (255, 255, 255)
GREY = (220, 220, 220)
BLACK = (0, 0, 0)
COLORS = (WHITE, GREY, BLACK)
BACKGROUND_COLOR = (200, 200, 200)

FOLDER = "records/"

# Patterns
BACKGROUND = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
]

CENTER = [
    [0, 0, 0],
    [0, 1, 0],
    [0, 0, 0]
]

LEFT = [
    [0, 0, 0],
    [1, 0, 0],
    [0, 0, 0]
]

RIGHT = [
    [0, 0, 0],
    [0, 0, 1],
    [0, 0, 0]
]

UP = [
    [0, 1, 0],
    [0, 0, 0],
    [0, 0, 0]
]

DOWN = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 1, 0]
]

# PLUS = [
#     [0, 1, 0],
#     [1, 1, 1],
#     [0, 1, 0]
# ]
#
# CROSS = [
#     [1, 0, 1],
#     [0, 1, 0],
#     [1, 0, 1]
# ]

# SIDES = [
#     [0, 1, 0],
#     [1, 0, 1],
#     [0, 1, 0]
# ]
#
# CORNERS = [
#     [1, 0, 1],
#     [0, 0, 0],
#     [1, 0, 1]
# ]
#
# H = [
#     [1, 0, 1],
#     [1, 1, 1],
#     [1, 0, 1]
# ]
#
# T = [
#     [1, 1, 1],
#     [0, 1, 0],
#     [0, 1, 0]
# ]

PATTERNS = [CENTER, LEFT, RIGHT, UP, DOWN]

def sequenced_phase():
    def sequenced_phase_generator():
        yield BACKGROUND, 5000
        for pattern in PATTERNS:
            yield pattern, 5000
            yield BACKGROUND, 5000
    return sequenced_phase_generator()

def random_phase():
    def random_phase_generator():
        for _ in range(20):
            yield random.choice(PATTERNS), random.uniform(5, 8) * 1000
            yield BACKGROUND, random.uniform(4, 6) * 1000
    return random_phase_generator()

def from_center():
    def from_center_generator():
        DIRECTIONS = [UP, DOWN, LEFT, RIGHT]
        for _ in range(3):
            for direction in DIRECTIONS:
                yield CENTER, random.uniform(5, 8) * 1000
                yield direction, random.uniform(5, 8) * 1000
                yield BACKGROUND, random.uniform(4, 6) * 1000
        for _ in range(10):
            yield CENTER, random.uniform(5, 8) * 1000
            yield random.choice(DIRECTIONS), random.uniform(5, 8) * 1000
            yield BACKGROUND, random.uniform(4, 6) * 1000
    return from_center_generator()

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Grid Recorder")
clock = pygame.time.Clock()

def draw_grid(screen, grid, confirmed):
    screen.fill(BACKGROUND_COLOR)
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = COLORS[grid[y][x] + confirmed]
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)

class GridRecorder():
    def __init__(self):
        self.grid = BACKGROUND
        self.flatted_grid = [item for sublist in self.grid for item in sublist]
        self.recording = False
        self.start_time = None
        self.filename = ""
        self.last_update_time = None
        self.next_update_duration = None
        self.phases = [sequenced_phase, random_phase]
        self.phase_index = None
        self.current_phase = None
        self.confirmed = False
        self.consecutive = None
        self.buffer = []
        self.buffer_size = 500

    def start_new_recording(self):
        self.recording = True
        self.set_grid(BACKGROUND)
        self.start_time = time.time()
        self.filename = FOLDER + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
        self.last_update_time = 0
        self.next_update_duration = 5000
        self.phase_index = 0
        self.current_phase = self.phases[self.phase_index]()
        self.confirmed = False
        self.consecutive = 0
        self.buffer = []
        print("Recording started. (Press space to stop.)")

    def set_grid(self, grid):
        self.grid = grid
        self.flattened_grid = [item for sublist in grid for item in sublist]

    def stop_recording(self):
        self.recording = False
        self.write_buffer()
        print("Recording stopped.")

    def update_grid(self):
        elapsed_time = (time.time() - self.start_time) * 1000
        if elapsed_time - self.last_update_time >= self.next_update_duration:
            while self.phase_index < len(self.phases):
                try:
                    grid, self.next_update_duration = next(self.current_phase)
                    self.set_grid(grid)
                    break
                except StopIteration:
                    self.phase_index = self.phase_index + 1
                    if self.phase_index >= len(self.phases):
                        self.stop_recording()
                        return
                    self.current_phase = self.phases[self.phase_index]()

            self.last_update_time = elapsed_time

    def eeg_handler(self, address, *args):
        if self.recording:
            current_time = time.time()
            elapsed_time = (current_time - self.start_time) * 1000
            eeg_data = list(args)

            self.buffer.append([elapsed_time] + eeg_data + [int(self.confirmed), self.consecutive] + self.flattened_grid)

            if len(self.buffer) >= self.buffer_size:
                self.write_buffer()

    def write_buffer(self):
        temp_buffer = self.buffer
        self.buffer = []
        with open(self.filename, mode='a') as file:
            writer = csv.writer(file)
            writer.writerows(temp_buffer)

if __name__ == "__main__":
    grid_recorder = GridRecorder()
    osc_handler = OSCHandler()
    osc_handler.register_handler("/muse/eeg", grid_recorder.eeg_handler)
    osc_handler.start_server()

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if grid_recorder.recording:
                        grid_recorder.stop_recording()
                    else:
                        grid_recorder.start_new_recording()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if grid_recorder.recording and event.button == 1:
                    grid_recorder.confirmed = True
                # elif grid_recorder.recording and grid_recorder.confirmed and event.button == 3:
                #     grid_recorder.consecutive += 1
            if event.type == pygame.MOUSEBUTTONUP:
                if grid_recorder.recording and event.button == 1:
                    grid_recorder.confirmed = False

        if grid_recorder.recording:
            grid_recorder.update_grid()

        draw_grid(screen, grid_recorder.grid, grid_recorder.confirmed)
        pygame.display.flip()
        clock.tick()

    osc_handler.stop_server()
    pygame.quit()
