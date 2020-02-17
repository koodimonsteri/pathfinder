
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import pygame

WALL = 0
FLOOR = 1
START = 2
END = 3

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
        self.g = 1000000
        self.previous = None

    # Draw cell
    def show(self, window, c_color=None):
        if c_color != None:
            color = c_color
        else:
            color = (0, 0, 0) if self.type == WALL else (50, 200, 200) if self.type == FLOOR else (40, 150, 40) if self.type == START else (20, 250, 20) if self.type == END else (200, 50, 50)
        pygame.draw.rect(window, color, pygame.Rect(self.w_x, self.w_y, self.size, self.size))

class CellGrid:
    def __init__(self, window_size):
        self.cell_size = 10
        self.size = int(window_size / self.cell_size)
        self.__cell_grid = [[Cell(x, y, self.cell_size, FLOOR) for x in range(0, self.size)] for y in range(0, self.size)]
        self.start_cell = self.get_cell(1, 1)
        self.start_cell.type = START
        self.end_cell = self.get_cell(self.size-2, self.size-2)
        self.end_cell.type = END

    # Iterator for CellGrid
    def __iter__(self):
        for j in range(0, self.size):
            for i in range(0, self.size):
                yield self.__cell_grid[j][i]

    # Edit maze
    # Returns boolean indicating if we updated anything
    def edit(self):
        m_x, m_y = pygame.mouse.get_pos()
        c_x, c_y = self.cell_index(m_x, m_y)
        res = False
        if self.in_bounds(c_x, c_y):
            
            logger.info("self size: %d m_x: %f m_y: %f Cell Position: (%d, %d)", self.size, m_x, m_y, c_x, c_y)
            keys_pressed = pygame.key.get_pressed()
            mouse_pressed = pygame.mouse.get_pressed()
            
            if mouse_pressed[0]:
                if keys_pressed[pygame.K_s]:
                    s_x, s_y = (self.start_cell.x, self.start_cell.y)
                    self.set_cell_type(s_x, s_y, FLOOR)
                    self.start_cell = self.get_cell(c_x, c_y)
                    self.set_cell_type(c_x, c_y, START)
                elif keys_pressed[pygame.K_e]:
                    e_x, e_y = (self.end_cell.x, self.end_cell.y)
                    self.set_cell_type(e_x, e_y, FLOOR)
                    self.end_cell = self.get_cell(c_x, c_y)
                    self.set_cell_type(c_x, c_y, END)
                else:
                    self.set_cell_type(c_x, c_y, WALL)
                res = True
            elif mouse_pressed[2]:
                self.set_cell_type(c_x, c_y, FLOOR)
                res = True
        return res

    # Draw CellGrid cells
    def show(self, window):
        for cell_row in self.__cell_grid:
            for cell in cell_row:
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
        return (int(m_x / self.cell_size), int(m_y / self.cell_size))

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
        self.__cell_grid[y][x].type = c_type
    
    # Get cell type
    def get_cell_type(self, x, y):
        return self.__cell_grid[y][x].type

    # Set cell type for all cells
    def set_cell_type_forall(self, c_type):
        for c_row in self.__cell_grid:
            for c in c_row:
                c.type = c_type      

    # Saves grid as text file
    def save(self, file_name):
        with open(file_name, "w") as f:
            f.write("%d %d\n" % (self.size, self.size))
            for row in self.__cell_grid:
                row_str = ""
                for cell in row:
                    row_str += str(cell.type)
                f.write(row_str + "\n")

    # Reads grid from text file
    def load(self, file_name):
        with open(file_name, "r") as f:
            size_parts = f.readline().strip().split(' ')
            size_x = int(size_parts[0])
            size_y = int(size_parts[1])
            self.__cell_grid = [None] * size_y
            for j in range(0, size_y):
                self.__cell_grid[j] = [None] * size_x
                line = f.readline()
                for i, value in enumerate(line):
                    self.__cell_grid[j][i].type = int(value) # For now assume that all values are valid (written by save())
                    