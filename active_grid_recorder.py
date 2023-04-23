import pygame
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
BLACK = (0, 0, 0)
COLORS = (WHITE, BLACK)
BACKGROUND_COLOR = (200, 200, 200)

def BACKGROUND():
    return [[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]]

WAITING = 0
RECORDING = 1
REVIEWING = 2

FOLDER = "records/"

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Grid Recorder")
clock = pygame.time.Clock()

def draw_grid(screen, grid):
    screen.fill(BACKGROUND_COLOR)
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = COLORS[grid[y][x]]
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

class GridRecorder():
    def __init__(self):
        self.grid = BACKGROUND()
        self.mode = WAITING
        self.start_time = None
        self.confirmed = False
        self.count = 0
        self.records = []
        self.filename = ""
        self.eeg_data_buffer = []

    def start_recording(self):
        self.grid = BACKGROUND()
        self.mode = RECORDING
        self.start_time = time.time()
        self.confirmed = False
        self.count = 0
        self.records = []
        self.filename = FOLDER + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.eeg_data_buffer = []
        print("Recording started. (Press space to stop.)")

    def stop_recording(self):
        self.mode = REVIEWING
        print(f"Recording stopped. Review the {self.count} patterns and press Enter to confirm.")

    def eeg_handler(self, address, *args):
        if self.mode == RECORDING:
            elapsed_time = (time.time() - self.start_time) * 1000
            eeg_data = list(args)
            self.eeg_data_buffer.append([elapsed_time] + eeg_data + [int(self.confirmed), self.count])

    def record_current_grid(self):
        print("Recorded grid:", self.grid)
        self.records.append([item for sublist in self.grid for item in sublist])
        self.grid = BACKGROUND()
        if len(self.records) >= self.count:
            print("All grids recorded. Saving data...")
            self.save_eeg_data()
            self.mode = WAITING

    def save_eeg_data(self):
        self.records.insert(0, [0]*GRID_SIZE**2)
        with open(self.filename + ".csv", mode='w') as file:
            writer = csv.writer(file)
            for eeg_data in self.eeg_data_buffer:
                writer.writerow(eeg_data + self.records[eeg_data[-1]])
        print("Data saved to " + self.filename + ".csv")
        self.eeg_data_buffer = []
        self.records = []


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
                    if grid_recorder.mode == WAITING:
                        grid_recorder.start_recording()
                    elif grid_recorder.mode == RECORDING:
                        grid_recorder.stop_recording()
                elif event.key == pygame.K_RETURN:
                    if grid_recorder.mode == REVIEWING:
                        grid_recorder.record_current_grid()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if grid_recorder.mode == REVIEWING:
                    if event.button == 1:
                        x, y = event.pos
                        grid_x = x // CELL_SIZE
                        grid_y = y // CELL_SIZE
                        grid_recorder.grid[grid_y][grid_x] = 1 - grid_recorder.grid[grid_y][grid_x]
                elif grid_recorder.mode == RECORDING:
                    if event.button == 1:
                        grid_recorder.confirmed = True
                        grid_recorder.count += 1
                    if event.button == 3:
                        grid_recorder.count += 1
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    grid_recorder.confirmed = False

        draw_grid(screen, grid_recorder.grid)
        pygame.display.flip()
        clock.tick(30)

    osc_handler.stop_server()
    pygame.quit()
