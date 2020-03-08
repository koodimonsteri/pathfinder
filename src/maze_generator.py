from abc import ABC, abstractclassmethod
import random
from collections import deque
from queue import Queue

from cell_grid import *

# Base abstact class for different generators
class MazeGenerator:
    def __init__(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    def generate_step(self):
        raise NotImplementedError
    
    def generate_maze(self):
        raise NotImplementedError


def get_cell_in_between(grid: CellGrid, c1, c2):
    x_off = int((c1.x - c2.x) / 2)
    y_off = int((c1.y - c2.y) / 2)
    return grid.get_cell(c2.x + x_off, c2.y + y_off)


# Prim's algorithm
class PrimGenerator(MazeGenerator):
    def __init__(self, grid):
        self.__grid = grid
        self.__maze_todo = set()
        self.__visited = set()

    # Reset maze generating
    def reset(self, grid):
        self.__grid = grid
        self.__maze_todo = set()
        self.__visited = set()
        self.__grid.set_cell_type_forall(WALL)
        # Get first cell by random
        cell = self.__grid.start_cell
        cell.type = FLOOR
        self.__visited.add(cell)
        # Get neighbors of the first cell and add them to todo set
        c_x, c_y = (cell.x, cell.y)
        for c in self.__grid.get_neighbors(c_x, c_y, 2):
            self.__maze_todo.add(c)

    def show(self, window):
        # Draw maze todo set
        for c in self.__maze_todo:
            c.show(window, (0,200, 40))

    def generate_step(self):
        
        if len(self.__maze_todo) > 0:
            # Get random cell from todo set
            cell = random.choice(list(self.__maze_todo))
            self.__visited.add(cell)

            # Get neighbors around our current cell
            nbrs = self.__grid.get_neighbors(cell.x, cell.y, 2)
            nbrs = [x for x in nbrs if self.__grid.in_bounds(x.x, x.y, 1) and x.type != WALL]
            
            if len(nbrs) > 0:
                rand_nbr = nbrs[random.randint(0, len(nbrs)-1)]
                if self.__grid.in_bounds(cell.x, cell.y, 1):
                    nbr_nbrs = self.__grid.get_neighbors(cell.x, cell.y, 2)
                    for nbr in nbr_nbrs:
                        if self.__grid.in_bounds(nbr.x, nbr.y, 1) and nbr not in self.__maze_todo and nbr not in self.__visited:
                            self.__maze_todo.add(nbr)
                    cell.type = FLOOR
                    # Set cell in between to floor
                    get_cell_in_between(self.__grid, cell, rand_nbr).type = FLOOR
                    
            self.__maze_todo.remove(cell)

    # Generate maze in one go
    def generate_maze(self):
        if len(self.__maze_todo) > 0:
            logger.info("Generating maze with Prim")
            while len(self.__maze_todo) > 0:
                self.generate_step()


class BackTrackGenerator(MazeGenerator):
    def __init__(self, grid):
        self.__grid = grid
        self.__stack = deque()
        self.__stack_cib = deque()  # Only for rendering, holds cells in between
        self.__current_cell = self.__grid.start_cell

    def show(self, window):
        for c in self.__stack:
            c.show(window,  (0, 150, 50))
        for c in self.__stack_cib:
            c.show(window, (0, 150, 50))
        self.__current_cell.show(window, (0, 200, 50))

    def generate_step(self):
        if len(self.__stack) > 0:
            nbrs = self.__grid.get_neighbors(self.__current_cell.x, self.__current_cell.y, 2)
            nbrs = [x for x in nbrs if self.__grid.in_bounds(x.x, x.y, 1) and x.type == WALL]
            if len(nbrs) > 0:
                nbr = nbrs[random.randint(0, len(nbrs)-1)]
                nbr.type = FLOOR
                cib = get_cell_in_between(self.__grid, nbr, self.__current_cell)
                cib.type = FLOOR
                self.__current_cell = nbr
                self.__stack.append(self.__current_cell)
                self.__stack_cib.append(cib)
            else:
                self.__current_cell = self.__stack.pop()
                if len(self.__stack_cib) > 0:
                    self.__stack_cib.pop()

    def generate_maze(self):
        if len(self.__stack) > 0:
            logger.info("Generating maze with Recursive Backtracking")
            while len(self.__stack) > 0:
                self.generate_step()

    def reset(self, grid):
        self.__grid = grid
        self.__stack = deque()
        self.__stack_cib = deque()
        self.__visited = set()
        self.__current_cell = self.__grid.start_cell
        self.__stack.append(self.__current_cell)
        self.__grid.set_cell_type_forall(WALL)
        self.__current_cell.type = FLOOR

# Divide and Conquer algorithm
class DNQGenerator(MazeGenerator):
    def __init__(self, grid):
        self.__grid = grid
        self.__que = deque()
        self.__generated = False
        self.__current_pos = None

    def show(self, surface):
        if not self.__generated and self.__current_pos:
            for c in self.__get_cells(self.__current_pos[0], self.__current_pos[1]):
                c.show(surface, (0, 150, 40))

    def __get_cells(self, pos1, pos2):
        res = []
        if pos1[0] == pos2[0]:
            for i in range(pos1[1], pos2[1]):
                res.append(self.__grid.get_cell(pos1[0], i))
        else:
            for i in range(pos1[0], pos2[0]):
                res.append(self.__grid.get_cell(i, pos1[1]))
        return res

    # Returns 2 areas
    def __divide(self, x, y, w, h, horizontal):

        mx = x + (0 if horizontal else random.randint(1, w - 2))
        my = y + (random.randint(1, h - 2) if horizontal else 0)

        if not horizontal:
            mx -= mx % 2
        else:
            my -= my % 2
        first = (mx, my)

        dx = 1 if horizontal else 0
        dy = 0 if horizontal else 1
        n = w if horizontal else h

        fx = mx + (random.randrange(0, w, 2) if horizontal else 0)
        fy = my + (0 if horizontal else random.randrange(0, h, 2))

        for i in range(0, n):
            self.__grid.get_cell(mx, my).type = WALL
            mx += dx
            my += dy
        self.__grid.get_cell(fx, fy).type = FLOOR

        nx, ny = (x, my + 1) if horizontal else (mx + 1, y)
        nw, nh = (w, y + h - my - 1) if horizontal else (x + w - mx - 1, h)
        if nw > 2 and nh > 2:
            self.__que.append((nx, ny, nw, nh))
        logger.debug("nxy2 (%d, %d) nwh(%d, %d)", nx, ny, nw, nh)

        nx, ny = (x, y)
        nw, nh = (w, my - y) if horizontal else (mx - x , h)
        if nw > 2 and nh > 2:
            self.__que.append((nx, ny, nw, nh))
        logger.debug("nxy1 (%d, %d) nwh(%d, %d)", nx, ny, nw, nh)

        if len(self.__que) == 0:
            logger.info("Generated maze!")
            self.__generated = True
            self.__current_pos = None
        else:
            self.__current_pos = (first, (mx, my))

    def generate_step(self):
        if not self.__generated and len(self.__que) > 0:
            x, y, w, h = self.__que.pop()
            horizontal = True if w < h else False if w > h else random.choice([True, False])
            
            self.__divide(x, y, w, h, horizontal)

    def generate_maze(self):
        while not self.__generated and len(self.__que) > 0:
            self.generate_step() 

    def reset(self, grid):
        self.__grid = grid
        self.__que = deque()
        self.__grid.set_cell_type_forall(FLOOR)
        # Set edges to WALL
        for i in range(0, self.__grid.size):
            self.__grid.set_cell_type(i, 0, WALL)
            self.__grid.set_cell_type(0, i, WALL)
            self.__grid.set_cell_type(self.__grid.size - 1, i, WALL)
            self.__grid.set_cell_type(i, self.__grid.size - 1, WALL)
        self.__que.append((1, 1, self.__grid.size-2, self.__grid.size-2))
        self.__generated = False
        self.__current_pos = None

class WeirdPrimGenerator(MazeGenerator):

    def __init__(self, grid):
        self.__grid = grid
        self.__maze_todo = set()

    def show(self, window):
        for c in self.__maze_todo:
            c.show(window, 1.0, (0,200, 40))

    def generate_step(self):
        if len(self.__maze_todo) > 0:
            # Get random cell from todo set
            cell = random.choice(list(self.__maze_todo))
            #logger.info("Random Cell (%d, %d)", cell.x, cell.y)
            c_x, c_y = (cell.x, cell.y)

            # Get neighbors around our current cell
            nbrs = self.__grid.get_neighbors(c_x, c_y)
            wall_count = 0
            for n in nbrs:
                if n not in self.__maze_todo and n.type == WALL:
                    wall_count += 1
            # If there is exactly 3 walls, add neighbors to todo set and clear current
            if wall_count == 3:
                for n in nbrs:
                    if n not in self.__maze_todo:
                        self.__maze_todo.add(n)
                cell.type = FLOOR
            self.__maze_todo.remove(cell)


    def reset(self, grid):
        self.__grid = grid
        self.__maze_todo = set()
        self.__grid.set_cell_type_forall(WALL)
        # Get first cell by random
        cell = self.__grid.get_cell(random.randint(1, self.__grid.size-1), random.randint(1, self.__grid.size-1))
        cell.type = FLOOR
        # Get neighbors of the first cell and add them to todo set
        c_x, c_y = self.__grid.cell_index(cell.x, cell.y)
        for c in self.__grid.get_neighbors(c_x, c_y):
            self.__maze_todo.add(c)