
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import pygame

from camera import *

WALL = 0
FLOOR = 1
START = 2
END = 3

cell_types = ["Wall", "Floor", "Start", "End"]

class Cell:
    def __init__(self, x, y, size, c_type=FLOOR):
        self.x = x
        self.y = y
        self.size = size
        self.type = c_type
        self.f = 0
        self.h = 0
        self.g = 1000000.0
        self.previous = None

    # Draw cell
    def show(self, window, c_color=None):
        if c_color != None:
            color = c_color
        elif self.type == WALL:
            color = (0, 0, 0)
        elif self.type == FLOOR:
            color = (50, 180, 180)
        elif self.type == START:
            color = (200, 40, 40)
        elif self.type == END:
            color = (40, 250, 40)
        
        #logger.info("Cell (%f, %f) size: %f", mx, my, msz)
        pygame.draw.rect(window, color, pygame.Rect(self.x * self.size, self.y*self.size, self.size, self.size))
        #g_str = "{0:.3f}".format(self.g)
        #mfont = pygame.font.Font(pygame.font.get_default_font(), 8)
        #text_surface = mfont.render(g_str, True, (0, 0, 0))
        #window.blit(text_surface, dest=(self.x*self.size,self.y*self.size))
    
    def __repr__(self):
        return "Cell (%d, %d), type: %s" % (self.x, self.y, cell_types[self.type])

class CellGrid:
    def __init__(self, window_size, c_size=10):
        self.cell_size = c_size
        self.size = int(window_size / self.cell_size)
        self.__cell_grid = [[Cell(x, y, self.cell_size, FLOOR) for x in range(0, self.size)] for y in range(0, self.size)]
        self.start_cell = self.get_cell(1, 1)
        self.start_cell.type = START
        self.end_cell = self.get_cell(self.size-2, self.size-2)
        self.end_cell.type = END
        self.camera = GridCamera(0, 0, window_size)
        self.surface = pygame.Surface((self.size, self.size))

    def __iter__(self):
        for j in range(0, self.size):
            for i in range(0, self.size):
                yield self.__cell_grid[j][i]

    # Edit maze
    # Returns edited cell or None
    def edit(self):
        m_x, m_y = pygame.mouse.get_pos()
        c_x, c_y = self.cell_index(m_x, m_y)
        res = None
        if self.camera.in_bounds(m_x, m_y):
            #logger.info("m_xy (%d, %d) cxy (%d, %d)", m_x, m_y, c_x, c_y)
            keys_pressed = pygame.key.get_pressed()
            
            if keys_pressed[pygame.K_s]:
                self.set_cell_type(c_x, c_y, START)
                logger.debug("Set START cell to (%d, %d)", c_x, c_y)
                res = self.get_cell(c_x, c_y)
            elif keys_pressed[pygame.K_e]:
                self.set_cell_type(c_x, c_y, END)
                logger.debug("Set END cell to (%d, %d)", c_x, c_y)
                res = self.get_cell(c_x, c_y)
            elif keys_pressed[pygame.K_w]:
                self.set_cell_type(c_x, c_y, WALL)
                logger.debug("Edit cell (%d, %d) type to WALL", c_x, c_y)
                res = self.get_cell(c_x, c_y)
            elif keys_pressed[pygame.K_f]:
                self.set_cell_type(c_x, c_y, FLOOR)
                logger.debug("Edit cell (%d, %d) type to WALL", c_x, c_y)
                res = self.get_cell(c_x, c_y)
        
        return res

    # Should be called after every zoom/drag operation
    def __clip_camera(self):
        s = self.size * self.cell_size * self.camera.current_scale
        # TODO: variable width/height instead of constant
        newx = min(s - 400, max(0, self.camera.x))
        newy = min(s - 400, max(0, self.camera.y))
        self.camera.x = newx
        self.camera.y = newy

    def drag_grid(self):
        cx = self.camera.x - self.camera.drag_x
        cy = self.camera.y - self.camera.drag_y
        self.camera.x = cx
        self.camera.y = cy
        self.__clip_camera()
        logger.info("Dragging grid - nxy (%f, %f) dxy (%f, %f)", cx, cy, self.camera.drag_x, self.camera.drag_y)
        self.camera.drag_x = 0
        self.camera.drag_y = 0

    def zoom_grid(self, mx, my, zoom_in):
        self.camera.zoom(mx, my, zoom_in)
        self.__clip_camera()
        logger.debug("Zooming grid - Mouse pos: (%d, %d), size: (%d), x_off: (%f), y_off: (%f) cur_scale: (%f), zoom_upd (%f)",
                    mx, my, self.camera.width,
                    self.camera.x, self.camera.y,
                    self.camera.current_scale,
                    zoom_in)
    
    
    # Draw CellGrid cells
    def show(self, window):
        for cell in self:
            cell.show(window)

    # Check if x and y are in bounds of CellGrid
    # Optional in_off parameter for maze generation
    def in_bounds(self, x, y, in_off=0):
        if x >= 0 + in_off and x < self.size - in_off and y >= 0 + in_off and y < self.size - in_off:
            return True
        else:
            return False

    # Returns grid indices from mouse position
    def cell_index(self, m_x, m_y):
        m_x, m_y = self.camera.screen_to_grid(m_x, m_y)
        c_x = int(m_x / self.cell_size)
        c_y = int(m_y / self.cell_size)
        #logger.debug("Calling cell_index: mx, my (%f, %f) cx, cy (%d, %d)", m_x, m_y, c_x, c_y)
        return (c_x, c_y)

        # Helper function to reconstruct path from current cell
    def get_path(self, current_cell):
        res = []
        cur = current_cell
        while cur.previous != None:
            res.append(cur)
            cur = cur.previous
        res.append(cur)
        return res

    # Get adjacent neighbors
    def get_neighbors(self, cell_x, cell_y, offset = 1):
        res = []
        for dir_x, dir_y in [(1,0), (0,1), (-1,0), (0,-1)]:
            n_x = cell_x + (dir_x * offset)
            n_y = cell_y + (dir_y * offset)
            if(self.in_bounds(n_x, n_y)):
                res.append(self.get_cell(n_x, n_y))
        return res

    # Get all cells by type
    # Optional not operator parameter
    def get_cells(self, cell_type, not_op=True):
        res = []
        for cell in self:
            if not_op and cell.type == cell_type:
                res.append(cell)
            elif cell.type != cell_type:
                res.append(cell)
        return res

    # Set Cell
    def set_cell(self, x, y, cell):
        self.__cell_grid[y][x] = cell
    
    # Get Cell
    def get_cell(self, x, y):
        return self.__cell_grid[y][x]

    # Set cell type
    def set_cell_type(self, x, y, c_type):
        if c_type == START:
            s_x, s_y = (self.start_cell.x, self.start_cell.y)
            self.__cell_grid[s_y][s_x].type = FLOOR
            self.start_cell = self.get_cell(x, y)
            self.__cell_grid[y][x].type = START
        elif c_type == END:
            e_x, e_y = (self.end_cell.x, self.end_cell.y)
            self.__cell_grid[e_y][e_x].type = FLOOR
            self.end_cell = self.get_cell(x, y)
            self.__cell_grid[y][x].type = END
        else:
            self.__cell_grid[y][x].type = c_type
    
    # Get cell type
    def get_cell_type(self, x, y):
        return self.__cell_grid[y][x].type

    # Set cell type for all cells
    def set_cell_type_forall(self, c_type):
        for c_row in self.__cell_grid:
            for c in c_row:
                c.type = c_type
                    
    