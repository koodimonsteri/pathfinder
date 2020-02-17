from abc import ABC, abstractclassmethod
import random
from collections import deque

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

def get_nbrs_in_list(cell, c_list, diff):
    res = []
    for c in c_list:
        d_x = int(abs(cell.x - c.x))
        d_y = int(abs(cell.y - c.y))
        if d_x == diff * cell.size or d_y == diff * cell.size:
            res.append(c)
    return res

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
        cell = self.__grid.get_cell(random.randint(1, self.__grid.size-1), random.randint(1, self.__grid.size-1))
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
                    temp_x = int((rand_nbr.x - cell.x) / 2) # Grid position between current and new cell
                    temp_y = int((rand_nbr.y - cell.y) / 2)
                    self.__grid.get_cell(cell.x + temp_x, cell.y + temp_y).type = FLOOR
                    
            self.__maze_todo.remove(cell)

    # Dummy function to generate maze in one go
    def generate_maze(self):
        pass


class RecBackTrackGenerator(MazeGenerator):
    def __init__(self, grid):
        self.__grid = grid
        self.__stack = deque()
        self.__visited = set()
        self.__current_cell = self.__grid.start_cell
        self.__stack.append(self.__current_cell)
        self.__working_set = []
        for j in range(1, self.__grid.size-1, 2):
            for i in range(1, self.__grid.size-1, 2):
                self.__working_set.append(self.__grid.get_cell(i, j))
        self.__grid.set_cell_type_forall(WALL)
        self.__grid.start_cell.type = START
        self.__grid.end_cell.type = END

    def show(self, window):
        pass

    def generate_step(self):
        if len(self.__stack) > 0:
            logger.info("Generating with recursive backtracker!")
            cur = self.__stack.pop()
            cur.type = FLOOR
            self.__current_cell = cur
            nbrs = get_nbrs_in_list(cur, self.__working_set, 2)
            for nbr in nbrs:
                if nbr not in self.__visited:
                    self.__stack.append(nbr)
                    self.__visited.add(nbr)
                    nbr.type = FLOOR
                    break
            
    def reset(self, grid):
        self.__grid = grid
        self.__stack = deque()
        self.__visited = set()
        self.__current_cell = self.__grid.start_cell
        self.__stack.append(self.__current_cell)
        self.__working_set = []
        for j in range(1, self.__grid.size-1, 2):
            for i in range(1, self.__grid.size-1, 2):
                self.__working_set.append(self.__grid.get_cell(i, j))
        self.__grid.set_cell_type_forall(WALL)
        self.__grid.start_cell.type = START
        self.__grid.end_cell.type = END

# Dummy class for Divide and Conquer algorithm
class DNQGenerator(MazeGenerator):
    def __init__(self, grid):
        self.__grid = grid

    def show(self):
        pass

    def generate_step(self):
        pass

    def reset(self):
        pass


class WeirdPrimGenerator(MazeGenerator):

    def __init__(self, grid):
        self.__grid = grid
        self.__maze_todo = set()

    def show(self, window):
        for c in self.__maze_todo:
            c.show(window, (0,200, 40))

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