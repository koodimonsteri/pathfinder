
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
SIDEBAR_OFFSET = GRID_SIZE
WINDOW_HEIGHT = GRID_SIZE
WINDOW_WIDTH = GRID_SIZE + SIDEBAR_WIDTH

EDITOR = 0
PATHFINDER = 1
MAZEGENERATOR = 2

def main():
    pygame.init()
    
    current_mode = EDITOR
    
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    
    my_gui = MyGui(SIDEBAR_WIDTH, WINDOW_HEIGHT, GRID_SIZE)

    # Init grid
    cell_grid = CellGrid(GRID_SIZE)
    # Init solver and generator
    solver = Astar(cell_grid)
    maze_generator = PrimGenerator(cell_grid)

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        oldmode = current_mode

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.text == modes[EDITOR]:
                        current_mode = EDITOR
                    elif event.text == modes[PATHFINDER]:
                        solver.reset(cell_grid)
                        current_mode = PATHFINDER
                    elif event.text == modes[MAZEGENERATOR]:
                        maze_generator.reset(cell_grid)
                        current_mode = MAZEGENERATOR
            my_gui.process_events(event)

        logger.info("Time delta: %f seconds", time_delta)
        
        # Check some inputs
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            current_mode = EDITOR
        elif keys[pygame.K_2]:
            solver.reset(cell_grid)
            current_mode = PATHFINDER
        elif keys[pygame.K_3]:
            maze_generator.reset(cell_grid)
            current_mode = MAZEGENERATOR
        elif keys[pygame.K_ESCAPE]: running = False
        
        if oldmode != current_mode:
            my_gui.set_sidebar(oldmode, current_mode)

        # Update
        if current_mode == EDITOR:
            # If we updated something in grid, reset solver
            if cell_grid.edit():
                solver.reset(cell_grid)
        elif current_mode == PATHFINDER:
            solver.solve_step()
        elif current_mode == MAZEGENERATOR:
            maze_generator.generate_step()
            
        my_gui.update(time_delta)
        
        # Render
        window.fill((250, 100, 0))
        
        cell_grid.show(window)
        if current_mode == 1:
            solver.show(window)
        elif current_mode == 2:
            maze_generator.show(window)

        my_gui.show(window)
        pygame.display.flip()

    pygame.quit()
    #cell_grid.save(MAP_DIRECTORY + "my_test_grid.txt")

main()