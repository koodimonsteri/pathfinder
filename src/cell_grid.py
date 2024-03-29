
from enum import Enum
from pathlib import Path

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import pygame

from camera import GridCamera

MAP_DIRECTORY = Path(__file__).parent.parent / 'maps'

class CellType(Enum):
    WALL = 0
    FLOOR = 1
    START = 2
    END = 3

CELL_COLORS = {
    CellType.WALL: (0, 0, 0),
    CellType.FLOOR: (50, 180, 180),
    CellType.START: (200, 40, 40),
    CellType.END: (40, 250, 40)
}


class Cell:
    def __init__(self, x, y, size, c_type=CellType.FLOOR):
        self.x = x
        self.y = y
        self.size = size
        self.type: CellType = c_type

        self.f = 0
        self.h = 0
        self.g = 1000000.0

        self.previous = None

    # Draw cell
    def show(self, surface, c_color=None):
        if c_color:
            color = c_color
        elif self.type in CELL_COLORS:
            color = CELL_COLORS[self.type]
        
        #logger.info("Cell (%f, %f) size: %f", mx, my, msz)
        pygame.draw.rect(surface, color, pygame.Rect(self.x * self.size, self.y*self.size, self.size, self.size))
        #g_str = "{0:.3f}".format(self.g)
        #mfont = pygame.font.Font(pygame.font.get_default_font(), 8)
        #text_surface = mfont.render(g_str, True, (0, 0, 0))
        #window.blit(text_surface, dest=(self.x*self.size,self.y*self.size))
    
    def __repr__(self):
        return "Cell (%d, %d), type: %s" % (self.x, self.y, self.type)

class CellGrid:
    def __init__(self, size, c_size=12):
        self.cell_size = c_size
        self.size = size
        self.__cell_grid = None
        self.start_cell: Cell = None
        self.end_cell: Cell = None
        self.reset_cells()

        self.camera = GridCamera(0, 0, self.size * self.cell_size)
        #self.surface = pygame.Surface((self.size, self.size))

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
        if not self.in_bounds(c_x, c_y, 1):
            return res
        #if not self.camera.in_bounds(m_x, m_y):
        #    return res
        
        #logger.info("m_xy (%d, %d) cxy (%d, %d)", m_x, m_y, c_x, c_y)
        keys_pressed = pygame.key.get_pressed()
        
        if keys_pressed[pygame.K_s]:
            self.set_cell_type(c_x, c_y, CellType.START)
            logger.debug("Set START cell to (%d, %d)", c_x, c_y)
            res = self.get_cell(c_x, c_y)
        elif keys_pressed[pygame.K_e]:
            self.set_cell_type(c_x, c_y, CellType.END)
            logger.debug("Set END cell to (%d, %d)", c_x, c_y)
            res = self.get_cell(c_x, c_y)
        elif keys_pressed[pygame.K_w]:
            if self.set_cell_type(c_x, c_y, CellType.WALL):
                logger.debug('Dont overwrite start or end!')
            else:
                logger.debug("Edit cell (%d, %d) type to WALL", c_x, c_y)
            res = self.get_cell(c_x, c_y)
        elif keys_pressed[pygame.K_f]:
            if self.set_cell_type(c_x, c_y, CellType.FLOOR):
                logger.debug('Dont overwrite start or end!')
            else:
                logger.debug("Edit cell (%d, %d) type to FLOOR", c_x, c_y)
            res = self.get_cell(c_x, c_y)
            self.set_cell_type(c_x, c_y, CellType.FLOOR)
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
    def show(self, surface, solver_cells):
        # Cull unvisible cells, ie. out of camera boundaries
        #count = 0
        for cell in self:
            #s = self.cell_size * self.camera.current_scale
            #cx = cell.x * s
            #cy = cell.y * s
            #cams = self.camera.width
            #if cx >= self.camera.x - s and cx < self.camera.x + cams \
            #    and cy >= self.camera.y - s and cy < self.camera.y + cams:
            cell.show(surface)
                #count += 1
        #logger.info("rendered %d cells", count)

    def reset_cells(self):
        self.__cell_grid = [[Cell(x, y, self.cell_size) for x in range(0, self.size)] for y in range(0, self.size)]
        for x in range(0, self.size):
            self.__cell_grid[0][x].type = CellType.WALL
            self.__cell_grid[self.size-1][x].type = CellType.WALL
            self.__cell_grid[x][0].type = CellType.WALL
            self.__cell_grid[x][self.size-1].type = CellType.WALL

        self.start_cell = self.get_cell(1, 1)
        self.start_cell.type = CellType.START

        self.end_cell = self.get_cell(self.size-2, self.size-2)
        self.end_cell.type = CellType.END

    # Check if x and y are in bounds of CellGrid
    # Optional in_off parameter for offset generation
    def in_bounds(self, x, y, in_off=0):
        return x >= 0 + in_off and x < self.size - in_off and y >= 0 + in_off and y < self.size - in_off


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
            if(self.in_bounds(n_x, n_y, 1)):
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
        res = None
        if c_type == CellType.START:
            s_x, s_y = (self.start_cell.x, self.start_cell.y)
            self.__cell_grid[s_y][s_x].type = CellType.FLOOR
            self.start_cell = self.get_cell(x, y)
            self.__cell_grid[y][x].type = CellType.START
            res = self.__cell_grid[y][x]
        elif c_type == CellType.END:
            e_x, e_y = (self.end_cell.x, self.end_cell.y)
            self.__cell_grid[e_y][e_x].type = CellType.FLOOR
            self.end_cell = self.get_cell(x, y)
            self.__cell_grid[y][x].type = CellType.END
            res = self.__cell_grid[y][x]
        else:
            cur_cell = self.get_cell(x, y)
            if cur_cell.type != CellType.START and cur_cell.type != CellType.END:
                cur_cell.type = c_type
                res = cur_cell
        return res

    # Get cell type
    def get_cell_type(self, x, y):
        return self.__cell_grid[y][x].type

    # Set cell type for all cells
    def set_cell_type_forall(self, c_type):
        for c_row in self.__cell_grid:
            for c in c_row:
                c.type = c_type
                    
    def find_free_cell(self, direction):
        area = 3
        x_start = 1 if direction == 1 else self.size - area
        x_end = area if direction == 1 else self.size - 1
        y_start = 1 if direction == 1 else self.size - area
        y_end = area if direction == 1 else self.size - 1
        res = None
        print(x_start, x_end, y_start, y_end)
        for y in range(y_start, y_end):
            for x in range(x_start, x_end):
                cell = self.get_cell(x, y)
                if any([c for c in self.get_neighbors(x, y) if c.type == CellType.FLOOR]):
                    res = cell
                    break
        return res

# Save grid as text file
def save_grid(file_name, grid: CellGrid):
    try:
        logger.info("Writing CellGrid to file %s", file_name)
        file_path = MAP_DIRECTORY / file_name
        if file_path.suffix != '.txt':
            logger.warning('Incorrect file type: %s', file_path.suffix)
            return
        f = open(MAP_DIRECTORY / file_name, "w")
        f.write("%d %d\n" % (grid.size, grid.cell_size))
        grid_str = ""
        for cell in grid:
            grid_str += str(cell.type.value)
        f.write(grid_str)
    except IOError as e:
        logger.error("Failed to open %s", file_name)
        logger.exception(e)
# Reads grid from text file

def load_grid(file_name):
    try:
        f = open(MAP_DIRECTORY / file_name, "r")
        logger.debug("Reading Cellgrid from file %s", file_name)
        size_parts = f.readline().strip().split(' ')
        g_size = int(size_parts[0])
        c_size = int(size_parts[1])
        logger.debug("Grid size: %d Cell size: %d", g_size, c_size)
        m_grid = CellGrid(g_size, c_size)
        x = 0
        y = 0
        for c in f.readline():
            cell = Cell(x, y, c_size, CellType(int(c)))
            m_grid.set_cell(x, y, cell)
            if cell.type == CellType.START:
                m_grid.start_cell = cell
            elif cell.type == CellType.END:
                m_grid.end_cell = cell
            x += 1
            if x == m_grid.size:
                y += 1
                x = 0
        return m_grid
    except IOError as e:
        logger.error("Failed to load file %s", file_name)
        logger.exception(e)
