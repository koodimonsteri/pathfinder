import time
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import pygame
import pygame_gui

from cell_grid import CellGrid, CellType, save_grid, load_grid
import solver as slvr
from my_gui import MyGui


UPDATE_MODES = [
    'Edit',
    'Step',
    'Continous',
    'Instant'
]


WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
GRID_SIZE = 768
GUI_WIDTH = 256

class MainApp():
    def __init__(self):
        pygame.init()
        
        self.clock = pygame.time.Clock()
        self.root_window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.background_surface = pygame.Surface((1024, 768)).convert()
        self.background_surface.fill(pygame.Color((50, 150, 50)))

        self.current_update_mode = 'Edit'
        self.gui = MyGui(GRID_SIZE, 0, GUI_WIDTH, WINDOW_HEIGHT, self.current_update_mode)
        self.running = False

        self.cell_grid = CellGrid(64, 12)
        self.solver: slvr.Solver = slvr.SOLVERS['Astar']('Astar', self.cell_grid)
        self.solver.reset(self.cell_grid)

        self.edit = False
        self.__step = False

    def run(self):
        fps = 0
        dt = 0.0
        self.running = True
        event_time = 0.0
        update_time = 0.0
        render_time = 0.0
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            dt += time_delta
            #logger.info("Time delta: %f seconds", time_delta)
            c1 = time.time()
            for event in pygame.event.get():
                self.process_event(event)
            c2 = time.time()
            event_time += c2-c1
            #print('events:', c2 - c1)
            self.update(time_delta)
            c3 = time.time()
            update_time += c3 - c2
            #print('update:', c3 - c2)
            self.show()
            c4 = time.time()
            render_time += c4 - c3
            #print('render:', c4 - c3)
            fps += 1
            if dt >= 1.0:
                dt -= 1.0
                logger.info("-----FPS %d-----", fps)
                fps = 0
                logger.info('event: %.2f, update: %.2f, render: %.2f', event_time, update_time, render_time)
                event_time = 0.0
                update_time = 0.0
                render_time = 0.0
        pygame.quit()

    def process_event(self, event):

        if event.type == pygame.QUIT:
            self.running = False
        
        # Keyboard events
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False

            elif event.key == pygame.K_SPACE:
                self.__step = True

            elif event.key == pygame.K_r:
                self.cell_grid.reset_cells()
                self.solver.reset(self.cell_grid)

            elif event.key == pygame.K_1:
                self.set_update_mode('Edit')
                self.gui.update_infobox_mode('Edit')
                self.gui.update_infobox_path(0)

            elif event.key == pygame.K_3:
                self.set_update_mode('Step')
                self.gui.update_infobox_mode('Step')
                self.gui.update_infobox_path(0)

            elif event.key == pygame.K_4:
                self.set_update_mode('Continous')
                self.gui.update_infobox_mode('Continous')
                self.gui.update_infobox_path(0)

            elif event.key == pygame.K_5:
                self.set_update_mode('Instant')
                self.gui.update_infobox_mode('Instant')
                self.gui.update_infobox_path(0)

        # Pygame userevents
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            # Drop down changes
            #if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            print('Resetting solver to: ', event.text)
            self.reset_solver(event.text)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Write grid to text file
            if event.ui_element.text == "Save":
                fname = self.gui.get_file_name()
                save_grid(fname, self.cell_grid)

            # Read grid from text file
            elif event.ui_element.text == "Load":
                fname = self.gui.get_file_name()
                cg = load_grid(fname)
                if cg != None:
                    self.cell_grid = cg
                    self.solver.reset(self.cell_grid)
                else:
                    logger.warn("Failed to load cell grid from file %s", fname)

        self.gui.process_event(event)

    def update(self, time_delta):
        #if self.cell_grid.camera.dragging:
        #    self.cell_grid.drag_grid()
        if self.gui.active_text_box():
            pass

        elif self.current_update_mode == 'Edit':
            self.cell_grid.edit()

        elif self.current_update_mode == 'Step':
            ed_cell = self.cell_grid.edit()
            if ed_cell != None and self.solver.cell_in_use(ed_cell):
                self.solver.reset(self.cell_grid)
                self.gui.update_infobox_path(0)

            if self.__step:
                if not self.solver.solved:
                    self.solver.solve_step()
                    self.__step = False

        elif self.current_update_mode == 'Continous':
            ed_cell = self.cell_grid.edit()
            if ed_cell != None and self.solver.cell_in_use(ed_cell):
                self.solver.reset(self.cell_grid)
                self.gui.update_infobox_path(0)
            
            if not self.solver.solved:
                self.solver.solve_step()

        elif self.current_update_mode == 'Instant':
            ed_cell = self.cell_grid.edit()
            if ed_cell != None and self.solver.cell_in_use(ed_cell):
                self.solver.reset(self.cell_grid)
                self.gui.update_infobox_path(0)
            
            if not self.solver.solved:
                self.solver.solve_all()
        else:
            logger.info('Unrecognized mode: %s', self.current_update_mode)

        path_len = 0
        if self.solver.name in slvr.PATHFINDERS and self.solver.solved:
            path_len = len(self.solver.get_path())

        self.gui.update(time_delta, path_len)

    def show(self):
        self.root_window.blit(self.background_surface, (0, 0))
        #c1 = time.time()
        self.cell_grid.show(self.root_window, self.solver.get_cells_in_use())
        #c2 = time.time()
        #grid_time = c2 - c1
        if self.current_update_mode != 'Edit':
            self.solver.show(self.root_window)
        #c3 = time.time()
        #solver_time = c3 - c2
        self.gui.show(self.root_window)
        #c4 = time.time()
        #gui_time = c4 - c3
        #logger.info('grid: %.4f, solver: %.4f, gui: %.4f', grid_time, solver_time, gui_time)
        pygame.display.update()

    def set_update_mode(self, u_mode):
        self.current_update_mode = u_mode
        self.solver.reset(self.cell_grid)

    def reset_solver(self, solver_name):
        if solver_name not in slvr.SOLVERS:
            return
        self.solver = slvr.SOLVERS[solver_name](solver_name, self.cell_grid)
        if solver_name in slvr.PATHFINDERS:
            c1 = self.cell_grid.find_free_cell(1)
            c2 = self.cell_grid.find_free_cell(-1)
            self.cell_grid.set_cell_type(c1.x, c1.y, CellType.START)
            self.cell_grid.set_cell_type(c2.x, c2.y, CellType.END)
        self.solver.reset(self.cell_grid)


def main():
    my_app = MainApp()
    my_app.run()


if __name__ == "__main__":
    main()