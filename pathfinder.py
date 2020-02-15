
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#import queue
import math

import pygame
import pygame_gui

WALL = 0
FLOOR = 1
START = 2
END = 3

MAP_DIRECTORY = "maps/"

WINDOW_SIZE = 400
GRID_SIZE = 400
SIDEBAR_WIDTH = 200
WINDOW_HEIGHT = GRID_SIZE
WINDOW_WIDTH = GRID_SIZE + SIDEBAR_WIDTH

class Cell():
    def __init__(self, x, y, size, c_type=FLOOR):
        self.x = x
        self.y = y
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
        pygame.draw.rect(window, color, pygame.Rect(self.x, self.y, self.size, self.size))

# Manhattan heuristic
def manhattan_heur(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

# Euclidean heuristic
def euclidean_heur(x1, y1, x2, y2):
    x = abs(x1 - x2)
    y = abs(y1 - y2)
    return math.sqrt(x*x + y*y)

class MGrid():
    def __init__(self):
        self.cell_size = 5
        self.size = int(WINDOW_SIZE / self.cell_size)
        self.__cell_grid = [[Cell(x*self.cell_size, y*self.cell_size, self.cell_size, FLOOR) for x in range(0, self.size)] for y in range(0, self.size)]        
        self.set_cell_type(0, 0, START)
        self.set_cell_type(self.size-1, self.size-1, END)
        self.start_cell = self.get_cell(0, 0)
        self.start_cell.g = 0
        self.end_cell = self.get_cell(self.size-1, self.size-1)
        self.start_cell.h = manhattan_heur(0,0, self.size-1, self.size-1)
        self.start_cell.f = self.start_cell.h
        self.openset = set()
        self.openset.add(self.start_cell)
        self.closedset = set()
        self.solved = False
        self.current = self.start_cell
        #self.path = []

    # Check if x and y are in grid bounds
    def in_bounds(self, x, y):
        if x >= 0 and x < self.size and y >= 0 and y < self.size:
            return True
        else:
            return False

    # Returns cell grid indices from screen-space coordinates
    def cell_index(self, m_x, m_y):
        return (int(m_x / self.cell_size), int(m_y / self.cell_size))

    # Update cell heuristics
    # x and y are position of cell to be updated
    # end_x and end_y are position of end cell used in heuristic calculation
    # neighbor_cell is optional parameter used in diagonal calculation
    def update_cell_heuristics(self, x, y, end_x, end_y, neighbor_cell=None):
        cell = self.get_cell(x, y)
        if cell not in self.closedset and cell.type != WALL:
            if neighbor_cell == None:
                g = self.current.g + 1.0
                h = euclidean_heur(x, y, end_x, end_y)
                f = g + h
                if g < cell.g:
                    cell.g = g
                    cell.h = h
                    cell.f = f
                    cell.previous = self.current
                    if cell not in self.openset:
                        self.openset.add(cell)
            else:
                g = self.current.g + 1.4
                h = euclidean_heur(x, y, end_x, end_y)
                f = g + h
                if f < neighbor_cell.f:
                    cell.g = g
                    cell.h = h
                    cell.f = f
                    cell.previous = self.current
                    if cell not in self.openset:
                        self.openset.add(cell)

    # Solve 1 step of astar
    def solve_step(self):
        logger.info("Solving 1 step of astar, solved: %s", self.solved)
        if not self.solved and len(self.openset) > 0:
    
            if self.current == self.end_cell:
                logger.info("Found shortest path!")
                solved = True
                return

            # Get cell with lowest f value
            c_lowest = None
            f_lowest = 1000000
            for cell in self.openset:
                if cell.f < f_lowest:
                    c_lowest = cell
                    f_lowest = cell.f
            
            self.current = c_lowest
            self.openset.remove(self.current)
            self.closedset.add(self.current)

            #neighbors = []
            c_x, c_y = self.cell_index(self.current.x, self.current.y)
            e_x, e_y = self.cell_index(self.end_cell.x, self.end_cell.y)
            #diag_dir = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
            for dir_x, dir_y in [(1,0), (0,1), (-1,0), (0,-1)]:
                n_x, n_y = (c_x + dir_x, c_y + dir_y)
                if self.in_bounds(n_x, n_y):
                    # Update neighbor heuristics
                    cell = self.get_cell(n_x, n_y)
                    if cell not in self.closedset and cell.type != WALL:
                        self.update_cell_heuristics(n_x, n_y, e_x, e_y)

                        # Check for diagonals adjacent to neighbor and update them
                        if dir_y == 0:
                            d_y1 = n_y - 1
                            d_y2 = n_y + 1
                            if self.in_bounds(n_x, d_y1):
                                self.update_cell_heuristics(n_x, d_y1, e_x, e_y, cell)
                            if self.in_bounds(n_x, d_y2):
                                self.update_cell_heuristics(n_x, d_y2, e_x, e_y, cell)
                        elif dir_x == 0:
                            d_x1 = n_x - 1
                            d_x2 = n_x + 1
                            if self.in_bounds(d_x1, n_y):
                                self.update_cell_heuristics(d_x1, n_y, e_x, e_y, cell)
                            if self.in_bounds(d_x2, n_y):
                                self.update_cell_heuristics(d_x2, n_y, e_x, e_y, cell)             
            logger.info("Processed a step of astar")

    # Build path from current cell
    def reconstruct_path(self):
        res = []
        cur = self.current
        while cur.previous != None:
            res.append(cur)
            cur = cur.previous
        res.append(cur)
        return res

    # Reset all cell heuristics
    def reset_heuristics(self):
        for c_row in self.__cell_grid:
            for c in c_row:
                c.h = 0
                c.g = 100000
                c.f = 0
        c_x, c_y = self.cell_index(self.start_cell.x, self.start_cell.y)
        e_x, e_y = self.cell_index(self.end_cell.x, self.end_cell.y)
        self.current.h = euclidean_heur(c_x, c_y, e_x, e_y)
        self.current.g = self.current.h

    # Reset variables used in solve
    def reset_solve(self):
        self.openset = set()
        self.openset.add(self.start_cell)
        self.closedset = set()
        self.current = self.start_cell
        self.current.previous = None
        self.reset_heuristics()
        self.solved = False

    # Edit grid cells
    def edit(self):
        m_x, m_y = pygame.mouse.get_pos()
        #logger.info("Mouse position (%f : %f)", m_x, m_y)
        if m_x >= 0 and m_x < WINDOW_SIZE and m_y >= 0 and m_y < WINDOW_SIZE:
            c_x, c_y = self.cell_index(m_x, m_y)
            #c_y = int(m_y/self.cell_size)
            logger.info("self size: %d m_x: %f m_y: %f Cell Position: (%d, %d)", self.size, m_x, m_y, c_x, c_y)
            keys_pressed = pygame.key.get_pressed()
            mouse_pressed = pygame.mouse.get_pressed()
            
            if mouse_pressed[0]:
                if keys_pressed[pygame.K_s]:
                    s_x, s_y = self.cell_index(self.start_cell.x, self.start_cell.y)
                    self.set_cell_type(s_x, s_y, FLOOR)
                    self.start_cell = self.get_cell(c_x, c_y)
                    self.set_cell_type(c_x, c_y, START)
                elif keys_pressed[pygame.K_e]:
                    e_x, e_y = self.cell_index(self.end_cell.x, self.end_cell.y)
                    self.set_cell_type(e_x, e_y, FLOOR)
                    self.end_cell = self.get_cell(c_x, c_y)
                    self.set_cell_type(c_x, c_y, END)
                else:
                    self.set_cell_type(c_x, c_y, WALL)
                self.reset_solve()
            elif mouse_pressed[2]:
                self.set_cell_type(c_x, c_y, FLOOR)
                self.reset_solve()

    # Draw grid cells
    def show(self, window):
        for cell_row in self.__cell_grid:
            for cell in cell_row:
                cell.show(window)
        for c in self.openset:
            c.show(window, (0, 150, 50))
        for c in self.closedset:
            c.show(window, (0, 100, 25))
        path = self.reconstruct_path()
        for c in path:
            c.show(window, (0, 250, 100))

    def set_cell(self, x, y, cell):
        self.__cell_grid[y][x] = cell
    
    def get_cell(self, x, y):
        return self.__cell_grid[y][x]

    def set_cell_type(self, x, y, c_type):
        self.__cell_grid[y][x].type = c_type
    
    def get_cell_type(self, x, y):
        return self.__cell_grid[y][x].type
        

    # Saves grid as text file
    # Write size to first line
    # Then write grid as 2d array
    '''def save(self, file_name):
        with open(file_name, "w") as f:
            f.write("%d\n" % (self.size))
            for row in self.__cell_grid:
                row_str = ""
                for cell in row:
                    row_str += str(cell.type)
                f.write(row_str + "\n")

    # Reads grid from text file
    # First read size
    # Then initialize grid and read values
   def load(self, file_name):
        with open(file_name, "r") as f:
            size = int(f.readline().strip())
            self.__cell_grid = [None] * size
            for i in range(0, size):
                self.__cell_grid[i] = [None] * size
                line = f.readline()
                for j, value in enumerate(line):
                    self.__cell_grid[i][j] = value # For now assume that all values are valid (written by save())'''


def main():
    
    # Modes, 0 = Edit, 1 = Solve
    current_mode = 0
    #window_size = 400
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    #cell_grid = Grid(WINDOW_SIZE)
    clock = pygame.time.Clock()
    
    test_grid = MGrid()
    
    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        logger.info("Time delta: %f seconds", time_delta)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]: current_mode = 0
        elif keys[pygame.K_2]: current_mode = 1
        elif keys[pygame.K_ESCAPE]: running = False

        if current_mode == 0:
            test_grid.edit()
        elif current_mode == 1:
            test_grid.solve_step()
        
        window.fill((250, 100, 0))
        test_grid.show(window)
        pygame.display.flip()
    #cell_grid.save(MAP_DIRECTORY + "my_test_grid.txt")

main()