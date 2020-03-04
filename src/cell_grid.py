
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
        self.w_x = x * size  # Window x and y for rendering
        self.w_y = y * size
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
        else:
            color = (0, 0, 0) if self.type == WALL else (50, 200, 200) if self.type == FLOOR else (40, 150, 40) if self.type == START else (20, 250, 20) if self.type == END else (200, 50, 50)
        msz = self.size
        mx = self.w_x
        my = self.w_y
        #logger.info("Cell (%f, %f) size: %f", mx, my, msz)
        pygame.draw.rect(window, color, pygame.Rect(mx, my, msz, msz))
        #g_str = "{0:.3f}".format(self.g)
        #mfont = pygame.font.Font(pygame.font.get_default_font(), 8)
        #text_surface = mfont.render(g_str, True, (0, 0, 0))
        #window.blit(text_surface, dest=(self.x*self.size,self.y*self.size))
    
    def __repr__(self):
        return "Cell (%d, %d), type: %s" % (self.x, self.y, cell_types[self.type])

class CellGrid:
    def __init__(self, window_size, c_size=5):
        self.cell_size = c_size
        self.size = int(window_size / self.cell_size)
        self.__cell_grid = [[Cell(x, y, self.cell_size, FLOOR) for x in range(0, self.size)] for y in range(0, self.size)]
        self.start_cell = self.get_cell(1, 1)
        self.start_cell.type = START
        self.end_cell = self.get_cell(self.size-2, self.size-2)
        self.end_cell.type = END
        self.camera = GridCamera(0, 0, window_size)
        

    # Iterator for CellGrid
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

    def drag_grid(self, drag):
        logger.info("Dragging! Mouse pos (%f %f) - rel (%f %f)", drag.mx, drag.my, drag.dx, drag.dy)
        cx = self.camera.x + drag.dx
        cy = self.camera.y + drag.dy
        self.camera.x = cx
        self.camera.y = cy

    # Update zoom level
    # Calculate new cell size and position
    def zoom_grid(self, zoom_in):
        #zoom = min(20.0, max(1.0, self.current_zoom + zoom_update))
        mx, my = pygame.mouse.get_pos()
        #self.camera.zoom(mx, my, zoom_in)
        #for c in self:
        #    c.size = int(self.cell_size * self.camera.current_zoom)
        #    c.w_x = c.x * c.size
        #    c.w_y = c.y * c.size
        logger.info("Mouse pos: (%d, %d), size: (%d), x_off: (%f), y_off: (%f) cur_zoom: (%f), zoom_upd (%f)", mx, my, self.camera.size, self.camera.x, self.camera.y, self.camera.current_zoom, zoom_in)

    # Notes
    # Modes:   1 = EDIT, 2 = SOLVE, 3 = GENERATE         <--- in pathfinder
    # Cells:   (EDITOR/SOLVER) ( w = WALL, f = FLOOR, s = START, e = END )    <--- in pathfinder
    # Updates:
    # (solve/generate in step mode)space = STEP SOLVE,
    # (all)scroll = ZOOM GRID,
    # (all)left click = DRAG GRID

    # Draw CellGrid cells
    def show(self, window):
        #logger.info("Zoom update: %f", self.zoom_update)
        #news = int(self.cell_size * self.current_zoom + self.cell_size * self.zoom_update)
        msurface = pygame.Surface((self.size * self.cell_size, self.size * self.cell_size))
        news = self.cell_size
        #neww = int(news * self.size * self.current_zoom)
        #newh = int(news * self.size * self.current_zoom)
        for cell in self:
            #cell.show(window, self.current_zoom)
            if cell.type == WALL:
                color = (0, 0, 0)
            elif cell.type == FLOOR:
                color = (50, 200, 200) 
            elif cell.type == START:
                color = (150, 20, 20)
            elif cell.type == END:
                color = (20, 250, 20) 
            else:
                color = (200, 50, 50)
            cell.show(window, color)
            #mx = cell.x * news + self.x_off
            #my = cell.y * news + self.y_off# * self.cell_size
            #pygame.draw.rect(msurface, color, pygame.Rect(cell.x, cell.y, 1.0, 1.0))
        #logger.info("neww: %d newh: %d", neww, newh)
        wsx, wsy = window.get_size()
        #window = pygame.transform.scale(msurface, (int(wsx * self.current_zoom), int(wsy * self.current_zoom)), window)

    # Check if x and y are in bounds of CellGrid
    # Optional in_off parameter for maze generation
    def in_bounds(self, x, y, in_off=0):
        if x >= 0 + in_off and x < self.size - in_off and y >= 0 + in_off and y < self.size - in_off:
            return True
        else:
            return False

    # Returns grid indices from mouse position
    def cell_index(self, m_x, m_y):
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
                    