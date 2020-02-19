
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
REALTIME = 3


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
        
        if event.type == pygame.USEREVENT:
            # Check drop down changes
            if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                # Editor drop_down -> change mode
                if event.text == modes[EDITOR]:
                    self.set_mode(EDITOR)

                # Solver drop_down -> reset solver and change mode
                elif event.text == modes[PATHFINDER]:
                    self.set_mode(PATHFINDER)

                # Generator drop_down -> reset generator and change mode
                elif event.text == modes[MAZEGENERATOR]:
                    self.set_mode(MAZEGENERATOR)

                elif event.text == modes[REALTIME]:
                    self.set_mode(REALTIME)

                # Reset solver
                elif event.text in solve_algos:
                    self.reset_solver(event.text)
                
                # Reset maze generator
                elif event.text in maze_algos:
                    self.reset_maze_generator(event.text)

            # Set all cells to FLOOR
            elif event.ui_element.text == "Clear":
                self.cell_grid.set_cell_type_forall(FLOOR)
                self.cell_grid.start_cell.type = START
                self.cell_grid.end_cell.type = END

            # Write grid to text file
            elif event.ui_element.text == "Save":
                fname = self.my_gui.get_fname_text()
                save(fname, self.cell_grid)

            # Read grid from text file
            elif event.ui_element.text == "Load":
                fname = self.my_gui.get_fname_text()
                self.cell_grid = load(fname)

        self.my_gui.process_events(event)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            self.set_mode(EDITOR)
        elif keys[pygame.K_2]:
            self.set_mode(PATHFINDER)
        elif keys[pygame.K_3]:
            self.set_mode(MAZEGENERATOR)
        elif keys[pygame.K_4]:
            self.set_mode(REALTIME)
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

        elif self.current_mode == REALTIME:
            # If we updated anything, reset solver and solve path
            if self.cell_grid.edit_realtime():
                self.solver.reset(self.cell_grid)
                self.solver.solve()
        self.my_gui.update(time_delta)

    # Reset solver algorithm
    def reset_solver(self, alg):
        if alg == solve_algos[0]:
            self.solver = Astar(self.cell_grid)
            self.solver.reset(self.cell_grid)
        elif alg == solve_algos[1]:
            self.solver = Dijkstra(self.cell_grid)
            self.solver.reset(self.cell_grid)

    # Reset maze generator
    def reset_maze_generator(self, alg):
        if alg == maze_algos[0]:
            self.maze_generator = PrimGenerator(self.cell_grid)
            self.maze_generator.reset(self.cell_grid)
        if alg == maze_algos[1]:
            self.maze_generator = RecBackTrackGenerator(self.cell_grid)
            self.maze_generator.reset(self.cell_grid)

    # Reset solver/generator
    def set_mode(self, mode):
        if mode == EDITOR:
            # Set editor mode and update gui
            self.current_mode = EDITOR
            self.my_gui.set_sidebar(EDITOR)
        elif mode == PATHFINDER:
            # Set pathfinder mode, reset solver and update gui
            self.current_mode = PATHFINDER
            self.reset_solver(solve_algos[0])
            self.my_gui.set_sidebar(PATHFINDER)
    
        elif mode == MAZEGENERATOR:
            # Set mazegenerator mode, reset generator and update gui
            self.current_mode = MAZEGENERATOR
            self.maze_generator.reset(self.cell_grid)
            self.my_gui.set_sidebar(MAZEGENERATOR)
        elif mode == REALTIME:
            self.current_mode = REALTIME
            

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
        elif self.current_mode == REALTIME:
            self.solver.show(window)
        # At last draw gui and swap buffers
        self.my_gui.show(window)
        pygame.display.flip()
    
    def run(self):
        pygame.init()

        window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        clock = pygame.time.Clock()
        fps = 0
        dt = 0.0
        self.running = True
        while self.running:
            time_delta = clock.tick(60) / 1000.0
            dt += time_delta
            #logger.info("Time delta: %f seconds", time_delta)
            
            # Process events
            for event in pygame.event.get():
                self.process_events(event)

            # Handle input
            self.handle_input()

            # Update game
            self.update(time_delta)

            # Render game
            self.render(window)

            fps += 1
            if dt >= 1.0:
                dt -= 1.0
                logger.info("-----FPS %d-----", fps)
                fps = 0

        pygame.quit()

# Save grid as text file
def save(file_name, grid: CellGrid):
    try:
        logger.debug("Writing CellGrid to file %s", file_name)
        f = open(MAP_DIRECTORY + file_name, "w")
        f.write("%d %d\n" % (grid.size, grid.cell_size))
        grid_str = ""
        for c in grid:
            grid_str += str(c.type)
        f.write(grid_str)
    except IOError as e:
        logger.debug("Failed to open %s", file_name)
        
# Reads grid from text file
def load(file_name):
    try:
        f = open(MAP_DIRECTORY + file_name, "r")
        logger.debug("Reading Cellgrid from file %s", file_name)
        size_parts = f.readline().strip().split(' ')
        g_size = int(size_parts[0])
        c_size = int(size_parts[1])
        logger.debug("Grid size: %d Cell size: %d", g_size, c_size)
        m_grid = CellGrid(WINDOW_SIZE, c_size)
        x = 0
        y = 0
        for c in f.readline():
            m_grid.set_cell(x, y, Cell(x, y, c_size, int(c)))
            x += 1
            if x == m_grid.size:
                y += 1
                x = 0
        return m_grid
    except IOError as e:
        logger.debug("Failed to load file %s", file_name)

def main():
    my_game = MyGame()
    my_game.run()


if __name__ == "__main__":
    main()