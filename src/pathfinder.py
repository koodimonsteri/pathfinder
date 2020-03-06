
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import pygame
import pygame_gui

from cell_grid import *
from solver import *
from maze_generator import *
from my_gui import *

MAP_DIRECTORY = "../maps/"
RES_DIRECTORY = "../res/"

# TODO: grid zooming and dragging
# TODO: scalable window (?)

GRID_SIZE = 400
SIDEBAR_WIDTH = 200
WINDOW_HEIGHT = GRID_SIZE
WINDOW_WIDTH = GRID_SIZE + SIDEBAR_WIDTH

# Update modes
EDITOR = 0
PATHFINDER = 1
MAZEGENERATOR = 2

# update_modes = ["Step", "Continous", "Instant"]
STEP = 0
CONTINOUS = 1
INSTANT = 2

class MyGame:
    def __init__(self):
        pygame.init()
        self.gui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), RES_DIRECTORY + "button_theme.json")
        self.grid_surface = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.grid_surface.set_clip(pygame.Rect(0, 0, 400, 400))
        self.cell_grid = CellGrid(GRID_SIZE)
        self.solver = Astar(self.cell_grid)
        self.maze_generator = PrimGenerator(self.cell_grid)
        self.my_gui = MyGui(self.gui_manager, GRID_SIZE, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
        self.current_mode = EDITOR
        self.current_update_mode = CONTINOUS
        self.running = False
        self.__step = False

    def process_events(self, event):
        if event.type == pygame.QUIT:
            self.running = False

        # Mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                if self.cell_grid.camera.in_bounds(event.pos[0], event.pos[1]):
                    self.cell_grid.camera.dragging = True

            elif event.button == pygame.BUTTON_WHEELDOWN:
                self.cell_grid.zoom_grid(False)

            elif event.button == pygame.BUTTON_WHEELUP:
                self.cell_grid.zoom_grid(True)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                self.cell_grid.camera.dragging = False
                self.cell_grid.update_drag(0.0, 0.0, 0.0, 0.0)

        elif event.type == pygame.MOUSEMOTION:
            if self.cell_grid.camera.dragging:
                self.cell_grid.update_drag(event.pos[0], event.pos[1], event.rel[0], event.rel[1])

        # Keyboard events
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_1:
                self.set_mode(EDITOR)
            elif event.key == pygame.K_2:
                self.set_mode(PATHFINDER)
            elif event.key == pygame.K_3:
                self.set_mode(MAZEGENERATOR)
            elif event.key == pygame.K_SPACE:
                self.__step = True

        # Pygame userevents
        elif event.type == pygame.USEREVENT:
            # Drop down changes
            if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:

                # Reset solver
                if event.text in solve_algos:
                    self.reset_solver(event.text)
                
                # Reset maze generator
                elif event.text in maze_algos:
                    self.reset_maze_generator(event.text)
            
            elif event.ui_element.text == "STEP":
                self.set_update_mode(STEP)
                
            elif event.ui_element.text == "CONT":
                self.set_update_mode(CONTINOUS)

            elif event.ui_element.text == "INST":
                self.set_update_mode(INSTANT)

            # Set all cells to FLOOR, retain start and end
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
                cg = load(fname)
                if cg != None:
                    self.cell_grid = cg
                else:
                    logger.warn("Failed to load cell grid from file %s", fname)
        self.my_gui.process_events(event)

    # Update game based on mode
    def update(self, time_delta):
        if self.cell_grid.camera.dragging:
            self.cell_grid.drag_grid()
            self.cell_grid.update_drag(self.cell_grid.camera.c_drag.mx,
                                        self.cell_grid.camera.c_drag.my,
                                        0.0, 0.0)

        elif self.current_mode == EDITOR:
            self.cell_grid.edit()

        elif self.current_mode == PATHFINDER:
            # Step by step mode -> check for step and solve 1 step
            if self.current_update_mode == STEP:
                ed_cell = self.cell_grid.edit()
                if ed_cell != None and self.solver.cell_in_use(ed_cell):
                    self.solver.reset(self.cell_grid)
                if self.__step:
                    self.solver.solve_step()
                    self.__step = False
                
            # Continous mode -> solve 1 step
            elif self.current_update_mode == CONTINOUS:
                ed_cell = self.cell_grid.edit()
                if ed_cell != None and self.solver.cell_in_use(ed_cell):
                    self.solver.reset(self.cell_grid)
                if not self.solver.solved:
                    self.solver.solve_step()
            
            # Instant mode -> try to edit grid and reset and solve if true
            elif self.current_update_mode == INSTANT:
                ed_cell = self.cell_grid.edit()
                if ed_cell != None and self.solver.cell_in_use(ed_cell):
                    self.solver.reset(self.cell_grid)
                if not self.solver.solved:
                    self.solver.solve()
            
        elif self.current_mode == MAZEGENERATOR:
            # Step by step mode -> check for step and generate 1 step
            if self.current_update_mode == STEP and self.__step:
                self.maze_generator.generate_step()
                self.__step = False

            # Continous mode -> generate 1 step of maze
            elif self.current_update_mode == CONTINOUS:
                self.maze_generator.generate_step()

            # Instant mode -> generate maze in one go
            elif self.current_update_mode == INSTANT:
                self.maze_generator.generate_maze()

        self.my_gui.update(time_delta)

    # Reset solver algorithm
    def reset_solver(self, alg):
        if alg == solve_algos[0]:
            self.solver = Astar(self.cell_grid)
            self.solver.reset(self.cell_grid)
        elif alg == solve_algos[1]:
            self.solver = Dijkstra(self.cell_grid)
            self.solver.reset(self.cell_grid)
        elif alg == solve_algos[2]:
            self.solver = DFS(self.cell_grid)
            self.solver.reset(self.cell_grid)

    # Reset maze generator
    def reset_maze_generator(self, alg):
        if alg == maze_algos[0]:
            self.maze_generator = PrimGenerator(self.cell_grid)
            self.maze_generator.reset(self.cell_grid)
        if alg == maze_algos[1]:
            self.maze_generator = RecBackTrackGenerator(self.cell_grid)
            self.maze_generator.reset(self.cell_grid)

    # Set game mode EDITOR/SOLVER/GENERATOR
    def set_mode(self, mode):
        if mode == EDITOR:
            # Set editor mode and update gui
            self.current_mode = EDITOR
            self.my_gui.set_sidebar(EDITOR)
            
        elif mode == PATHFINDER:
            # Set pathfinder mode, reset solver and update gui
            self.current_mode = PATHFINDER
            self.reset_solver(solve_algos[self.my_gui.current_solve_alg])
            self.my_gui.set_sidebar(PATHFINDER)
    
        elif mode == MAZEGENERATOR:
            # Set mazegenerator mode, reset generator and update gui
            self.current_mode = MAZEGENERATOR
            self.reset_maze_generator(maze_algos[self.my_gui.current_maze_alg])
            self.my_gui.set_sidebar(MAZEGENERATOR)
        
    # Set update mode STEP/CONT/INST
    # Reset solver/generator if needed
    def set_update_mode(self, u_mode):
        self.current_update_mode = u_mode
        if self.current_mode == PATHFINDER:
            self.solver.reset(self.cell_grid)
        elif self.current_mode == MAZEGENERATOR:
            self.maze_generator.reset(self.cell_grid)

    # Draw game
    def show(self, window):
        window.fill((50, 50, 50))
        # Always draw grid
        grid_surf = pygame.Surface((self.cell_grid.size, self.cell_grid.size))
        self.cell_grid.show(grid_surf)##
        # Draw solver/generator based on mode
        if self.current_mode == PATHFINDER:
            self.solver.show(grid_surf)
            self.cell_grid.start_cell.show(grid_surf)
            self.cell_grid.end_cell.show(grid_surf)
        elif self.current_mode == MAZEGENERATOR:
            self.maze_generator.show(grid_surf)

        # Scale and blit to window size
        pygame.transform.scale(grid_surf, (GRID_SIZE, GRID_SIZE), self.grid_surface)
        window.blit(self.grid_surface, (0, 0))

        # Scale and blit by zoom

        window.blit(self.grid_surface, (self.cell_grid.camera.x, self.cell_grid.camera.y))
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

            # Update game
            self.update(time_delta)

            # Render game
            self.show(window)

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
        m_grid = CellGrid(GRID_SIZE, c_size)
        x = 0
        y = 0
        for c in f.readline():
            cell = Cell(x, y, c_size, int(c))
            m_grid.set_cell(x, y, cell)
            if cell.type == START:
                m_grid.start_cell = cell
            elif cell.type == END:
                m_grid.end_cell = cell
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