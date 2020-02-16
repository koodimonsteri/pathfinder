
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import pygame
import pygame_gui

from cell_grid import *
from solver import *
from maze_generator import *
from my_gui import *

MAP_DIRECTORY = "maps/"

WINDOW_SIZE = 400
GRID_SIZE = 400
SIDEBAR_WIDTH = 200
WINDOW_HEIGHT = GRID_SIZE
WINDOW_WIDTH = GRID_SIZE + SIDEBAR_WIDTH

EDITOR = 0
PATHFINDER = 1
MAZEGENERATOR = 2

class MyGame:
    def __init__(self):
        pygame.init()
        self.gui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.cell_grid = CellGrid(WINDOW_SIZE)
        self.solver = Astar(self.cell_grid)
        self.maze_generator = PrimGenerator(self.cell_grid)
        self.my_gui = MyGui(self.gui_manager)
        self.current_mode = EDITOR
        self.running = False
        
    def process_events(self, event):
        if event.type == pygame.QUIT:
                self.running = False
        self.my_gui.process_events(event)

        if event.type == pygame.USEREVENT:
            # Check drop down changes
            if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                # Editor drop_down -> change mode
                if event.text == modes[EDITOR]:
                    self.reset_mode(EDITOR)

                # Solver drop_down -> reset solver and change mode
                elif event.text == modes[PATHFINDER]:
                    self.reset_mode(PATHFINDER)

                # Generator drop_down -> reset generator and change mode
                elif event.text == modes[MAZEGENERATOR]:
                    self.reset_mode(MAZEGENERATOR)
                    
            elif event.ui_element.text == "Clear":
                # Set all cells to FLOOR
                self.cell_grid.set_cell_type_forall(FLOOR)
                self.cell_grid.start_cell.type = START
                self.cell_grid.end_cell.type = END
            elif event.ui_element.text == "Save":
                # Save grid to file, TODO save grid
                logger.info("SAVING")

            elif event.ui_element.text == "Load":
                # Load grid from file TODO load grid
                logger.info("LOADING")

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            self.reset_mode(EDITOR)
        elif keys[pygame.K_2]:
            self.reset_mode(PATHFINDER)
        elif keys[pygame.K_3]:
            self.reset_mode(MAZEGENERATOR)
        elif keys[pygame.K_ESCAPE]:
            # If escaping set running to false
            self.running = False

    # Update game based on mode
    def update(self, time_delta):
        if self.current_mode == EDITOR:
            self.cell_grid.edit()
        elif self.current_mode == PATHFINDER:
            self.solver.solve_step()
        elif self.current_mode == MAZEGENERATOR:
            self.maze_generator.generate_step()
        self.my_gui.update(time_delta)

    # Reset solver/generator
    def reset_mode(self, mode):
        if mode == EDITOR:
            # Set editor mode and update gui
            self.current_mode = EDITOR
            self.my_gui.set_sidebar(EDITOR)
        elif mode == PATHFINDER:
            # Set pathfinder mode, reset solver and update gui
            self.current_mode = PATHFINDER
            self.solver.reset(self.cell_grid)
            self.my_gui.set_sidebar(PATHFINDER)
        elif mode == MAZEGENERATOR:
            # Set mazegenerator mode, reset generator and update gui
            self.current_mode = MAZEGENERATOR
            self.maze_generator.reset(self.cell_grid)
            self.my_gui.set_sidebar(MAZEGENERATOR)

    # Draw game
    def render(self, window):
        window.fill((50, 50, 50))
        # Always draw grid
        self.cell_grid.show(window)
        # Draw solver/generator based on mode
        if self.current_mode == PATHFINDER:
            self.solver.show(window)
        elif self.current_mode == MAZEGENERATOR:
            self.maze_generator.show(window)
        # At last draw gui and flip buffers
        self.my_gui.show(window)
        pygame.display.flip()
    
    def run(self):
        pygame.init()

        window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        clock = pygame.time.Clock()

        self.running = True
        while self.running:
            time_delta = clock.tick(60) / 1000.0
            logger.info("Time delta: %f seconds", time_delta)
            
            # Process events
            for event in pygame.event.get():
                self.process_events(event)

            # Handle input
            self.handle_input()

            # Update game
            self.update(time_delta)

            # Render game
            self.render(window)
        pygame.quit()

def main():
    my_game = MyGame()
    my_game.run()

if __name__ == "__main__":
    main()