import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from abc import ABC, abstractmethod
import math
import heapq
from collections import deque

from cell_grid import *

import pygame

# TODO: Optional diagonals
# TODO: modifiable DFS search directions

# Base abstract class for different path finding algorithms
class PathFinder(ABC):
    def __init__(self):
        raise NotImplementedError

    def solve_step(self):
        raise NotImplementedError

    def solve(self):
        raise NotImplementedError

    def reset(self, grid):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    def cell_in_use(self):
        raise NotImplementedError
    

# Manhattan heuristic
def manhattan_heur(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

# Euclidean heuristic
def euclidean_heur(x1, y1, x2, y2):
    x = abs(x1 - x2)
    y = abs(y1 - y2)
    return math.sqrt(x*x + y*y)

# Diagonal heuristic
def octile_heur(x1, y1, x2, y2):
    x = abs(x1 - x2)
    y = abs(y1 - y2)
    mmin = min(x, y)
    mmax = max(x, y)
    d = mmax - mmin
    return math.sqrt(mmin*mmin + mmin*mmin) + d

# A* (A-star) path finding algorithm
class Astar(PathFinder):
    def __init__(self):
        self.__grid = None
        self.__openset = set()
        self.__closedset = set()
        self.solved = False
        self.__current_cell = None

    # Solve 1 step of astar
    def solve_step(self):
        #logger.info("Solving 1 step of astar, solved: %s", self.solved)
        if not self.solved and len(self.__openset) > 0:
            if self.__current_cell == self.__grid.end_cell:
                logger.info("Found shortest path with Astar! length: %d", len(self.__grid.get_path(self.__current_cell)))
                self.solved = True
                return
            
            # End cell indices
            e_x, e_y = (self.__grid.end_cell.x, self.__grid.end_cell.y)

            # Get cell with lowest f value
            c_lowest = None
            f_lowest = 1000000
            d_lowest = 1000000
            for cell in self.__openset:
                if cell.f < f_lowest:  # Pick cell with lowest f cost
                    d_lowest = octile_heur(cell.x, cell.y, e_x, e_y)
                    c_lowest = cell
                    f_lowest = cell.f
                elif cell.f == f_lowest:  # If f cost are same, pick the one with lower distance to goal
                    d = octile_heur(cell.x, cell.y, e_x, e_y)
                    if d < d_lowest:
                        d_lowest = d
                        f_lowest = cell.f
                        c_lowest = cell

            logger.debug("Current Cell (%d %d), g %f, h %f, f %f", self.__current_cell.x, self.__current_cell.y, self.__current_cell.g, self.__current_cell.h, self.__current_cell.f)
            logger.debug("Lowest Cell  (%d %d), g %f, h %f, f %f", c_lowest.x, c_lowest.y, c_lowest.g, c_lowest.h, c_lowest.f)
            
            self.__current_cell = c_lowest
            self.__openset.remove(self.__current_cell)
            self.__closedset.add(self.__current_cell)

            c_x, c_y = (self.__current_cell.x, self.__current_cell.y)
            # Loop adjacent cells and update them
            for dir_x, dir_y in [(1,0), (0,1), (-1,0), (0,-1)]:
                n_x, n_y = (c_x + dir_x, c_y + dir_y)
                if self.__grid.in_bounds(n_x, n_y):
                    # Update adjacent neighbor heuristics
                    cell = self.__grid.get_cell(n_x, n_y)
                    if cell not in self.__closedset and cell.type != WALL:
                        self.__update_cell_heuristics(n_x, n_y, 1)

                        diag_g = 1.414213
                        # Check for diagonals adjacent to neighbor and update them
                        if dir_y == 0:
                            d_y1 = n_y - 1
                            d_y2 = n_y + 1
                            if self.__grid.in_bounds(n_x, d_y1):
                                self.__update_cell_heuristics(n_x, d_y1, diag_g)
                            if self.__grid.in_bounds(n_x, d_y2):
                                self.__update_cell_heuristics(n_x, d_y2, diag_g)
                        elif dir_x == 0:
                            d_x1 = n_x - 1
                            d_x2 = n_x + 1
                            if self.__grid.in_bounds(d_x1, n_y):
                                self.__update_cell_heuristics(d_x1, n_y, diag_g)
                            if self.__grid.in_bounds(d_x2, n_y):
                                self.__update_cell_heuristics(d_x2, n_y, diag_g)

    # Solve Astar in one go
    def solve(self):
        while not self.solved and len(self.__openset) > 0:
            self.solve_step()

    def cell_in_use(self, cell):
        return cell == self.__current_cell or cell in self.__openset or cell in self.__closedset or cell == self.__grid.start_cell or cell == self.__grid.end_cell

    # Updates cell heuristics
    # Parameters x and y are position of cell to be updated, g is g-cost from previous cell
    def __update_cell_heuristics(self, x, y, g):
        cell = self.__grid.get_cell(x, y)
        if cell not in self.__closedset and cell.type != WALL:
            g = self.__current_cell.g + g
            h = octile_heur(cell.x, cell.y, self.__grid.end_cell.x, self.__grid.end_cell.y)
            if g < cell.g:
                cell.g = g
                cell.h = h
                cell.f = g + h
                cell.previous = self.__current_cell
                if cell not in self.__openset:
                    self.__openset.add(cell)

    # Reset cell heuristics in grid
    def __reset_heuristics(self):
        for c in self.__grid:
            c.h = 0
            c.g = 1000000
            c.f = 0
            c.previous = None

    # Reset astar solving
    def reset(self, grid):
        self.__grid = grid
        self.__openset = set()
        self.__openset.add(self.__grid.start_cell)
        self.__closedset = set()
        self.__current_cell = self.__grid.start_cell
        self.__reset_heuristics()
        self.__current_cell.g = 0
        self.solved = False

    # Draw openset, closedset and path
    def show(self, window):
        # First draw openset in light green
        for c in self.__openset:
            c.show(window, (0, 150, 50))
        # Then draw closedset in dark green
        for c in self.__closedset:
            c.show(window, (0, 100, 25))
        # And at last construct path and draw it in bright green
        if self.solved or len(self.__openset) > 0:
            path = self.__grid.get_path(self.__current_cell)
            for c in path:
                c.show(window, (0, 200, 100))
            self.__current_cell.show(window, (100, 250, 150))


class Dijkstra(PathFinder):
    def __init__(self):
        self.__grid = None
        self.__visited = set()
        self.__unvisited = []
        self.__current_cell = None
        self.solved = False
    
    def solve_step(self):
        if len(self.__unvisited) > 0 and not self.solved:
            if self.__current_cell == self.__grid.end_cell:
                logger.info("Found path with Dijkstra! length: %d", len(self.__grid.get_path(self.__current_cell)))
                self.solved = True
                return
            cur_g, cur_cell = heapq.heappop(self.__unvisited)
            self.__visited.add(cur_cell)
            tempnbrs = []
            for dir_x, dir_y in [(1,0), (0,1), (-1,0), (0,-1)]:
                n_x, n_y = (cur_cell.x + dir_x, cur_cell.y + dir_y)
                if self.__grid.in_bounds(n_x, n_y):
                    nc = self.__grid.get_cell(n_x, n_y)
                    if nc not in self.__visited and nc.type != WALL:
                        # Update neighbor
                        self.__update_cell_heuristics(n_x, n_y, cur_g + 1.0, cur_cell)
                        tempnbrs.append(nc)

                        # Update adjacent diagonals
                        diag_g = 1.414213
                        if dir_x == 0:
                            x1 = n_x - 1
                            x2 = n_x + 1
                            if self.__grid.in_bounds(x1, n_y):
                                self.__update_cell_heuristics(x1, n_y, cur_g + diag_g, cur_cell)
                                c = self.__grid.get_cell(x1, n_y)
                                if c not in tempnbrs and c not in self.__visited and c.type != WALL:
                                    tempnbrs.append(c)
                            if self.__grid.in_bounds(x2, n_y):
                                self.__update_cell_heuristics(x2, n_y, cur_g + diag_g, cur_cell)
                                c = self.__grid.get_cell(x2, n_y)
                                if c not in tempnbrs and c not in self.__visited and c.type != WALL:
                                    tempnbrs.append(c)
                        elif dir_y == 0:
                            y1 = n_y - 1
                            y2 = n_y + 1
                            if self.__grid.in_bounds(n_x, y1):
                                self.__update_cell_heuristics(n_x, y1, cur_g + diag_g, cur_cell)
                                c = self.__grid.get_cell(n_x, y1)
                                if c not in tempnbrs and c not in self.__visited and c.type != WALL:
                                    tempnbrs.append(c)
                            if self.__grid.in_bounds(n_x, y2):
                                self.__update_cell_heuristics(n_x, y2, cur_g + diag_g, cur_cell)
                                c = self.__grid.get_cell(n_x, y2)
                                if c not in tempnbrs and c not in self.__visited and c.type != WALL:
                                    tempnbrs.append(c)
            # Update current cell and sort unvisited cells
            self.__current_cell = cur_cell
            for nbr in tempnbrs:
                self.__unvisited.append((nbr.g, nbr))
            self.__heapify_unvisited()
    
    def solve(self):
        while not self.solved and len(self.__unvisited) > 0:
            self.solve_step()

    def cell_in_use(self, cell):
        return cell == self.__current_cell or cell in self.__unvisited or cell in self.__visited or cell == self.__grid.start_cell or cell == self.__grid.end_cell

    def __update_cell_heuristics(self, x, y, g, cur_cell):
        c = self.__grid.get_cell(x, y)
        if g < c.g and c not in self.__visited and c.type != WALL:
            c.g = g
            c.previous = cur_cell

    # Function to just heapify unvisited cells
    def __heapify_unvisited(self):
        cells = [(cell.g, cell) for c_g, cell in self.__unvisited if cell not in self.__visited]
        self.__unvisited = [(cell.g, cell) for c_g, cell in self.__unvisited if cell not in self.__visited]
        setattr(Cell, "__lt__", lambda self, other: self.g < other.g)
        heapq.heapify(self.__unvisited)
    
    def __reset_heuristics(self):
        for c in self.__grid:
            c.g = 100000
            c.previous = None
        self.__current_cell.g = 0

    def reset(self, grid):
        self.__grid = grid
        self.__current_cell = grid.start_cell
        self.__visited = set()
        self.__unvisited = []
        self.__reset_heuristics()
        self.__unvisited.append((self.__current_cell.g, self.__current_cell))
        self.__heapify_unvisited()
        self.solved = False
        
    def show(self, window):
        for c in self.__visited:
            c.show(window, (0, 150, 40))
        if self.solved or len(self.__unvisited) > 0:
            path = self.__grid.get_path(self.__current_cell)        
            for c in path:
                c.show(window, (0, 200, 100))

# Depth First Search
class DFS(PathFinder):
    def __init__(self):
        self.__grid = None
        self.__stack = deque()
        self.__visited = set()
        self.__current_cell = None
        self.solved = False

    def solve_step(self):
        if not self.solved and len(self.__stack) > 0:
            
            c = self.__stack.pop()
            self.__visited.add(c)
            self.__current_cell = c
            nbrs = self.__grid.get_neighbors(c.x, c.y)
            nbrs = [x for x in nbrs if x not in self.__visited and x.type != WALL]
            for nbr in nbrs:
                self.__stack.append(nbr)
                nbr.previous = self.__current_cell

            if self.__current_cell == self.__grid.end_cell:
                logger.info("Found path with Depth First Search! length: %d", len(self.__grid.get_path(self.__current_cell)))
                self.solved = True
            
    def solve(self):
        while not self.solved and len(self.__stack) > 0:
            self.solve_step()

    def cell_in_use(self, cell):
        return cell == self.__current_cell or cell in self.__visited or cell in self.__stack or cell == self.__grid.start_cell or cell == self.__grid.end_cell

    def reset(self, grid):
        self.__grid = grid
        for c in grid:
            c.previous = None
        self.__visited = set()
        self.__stack = deque()
        self.__current_cell = None
        self.__stack.append(self.__grid.start_cell)
        self.solved = False

    def show(self, window):
        for c in self.__visited:
            c.show(window, (0, 100, 30))
        for c in self.__stack:
            c.show(window, (0, 150, 40))
        if self.__current_cell != None:
            path = self.__grid.get_path(self.__current_cell)
            for c in path:
                c.show(window, (0, 200, 100))