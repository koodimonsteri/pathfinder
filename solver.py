from abc import ABC, abstractmethod
from cell_grid import *

import logging
logger = logging.getLogger("PathFinder")
logging.basicConfig(level=logging.INFO)

import math

import pygame

class PathFinder(ABC):
    def __init__(self):
        raise NotImplementedError

    def solve_step(self, parameter_list):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

# Manhattan heuristic
def manhattan_heur(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

# Euclidean heuristic
def euclidean_heur(x1, y1, x2, y2):
    x = abs(x1 - x2)
    y = abs(y1 - y2)
    return math.sqrt(x*x + y*y)

def diagonal_heur(x1, y1, x2, y2):
    x = abs(x1 - x2)
    y = abs(y1 - y2)
    mmin = min(x, y)
    mmax = max(x, y)
    d = mmax - mmin
    return math.sqrt(mmin*mmin + mmin*mmin) + d

class Astar(PathFinder):
    def __init__(self, grid):
        self.__grid = grid
        self.__openset = set()
        self.__openset.add(grid.start_cell)
        self.__closedset = set()
        self.solved = False
        self.__current_cell = grid.start_cell

    def solve_step(self):
        logger.info("Solving 1 step of astar, solved: %s", self.solved)
        if not self.solved and len(self.__openset) > 0:
            if self.__current_cell == self.__grid.end_cell:
                logger.info("Found shortest path!")
                solved = True
                return
            
            # End cell indices
            e_x, e_y = self.__grid.cell_index(self.__grid.end_cell.x, self.__grid.end_cell.y)

            # Get cell with lowest f value
            c_lowest = None
            f_lowest = 1000000
            d_lowest = 1000000
            for cell in self.__openset:
                temp_x, temp_y = self.__grid.cell_index(cell.x, cell.y)
                if cell.f < f_lowest:  # Pick cell with lowest f cost
                    d_lowest = diagonal_heur(temp_x, temp_y, e_x, e_y)
                    c_lowest = cell
                    f_lowest = cell.f
                elif cell.f == f_lowest:  # If f cost are same, pick the one with lower distance to goal
                    d = diagonal_heur(temp_x, temp_y, e_x, e_y)
                    if d < d_lowest:
                        d_lowest = d
                        f_lowest = cell.f
                        c_lowest = cell
            logger.info("Current Cell (%d %d), g %f, h %f, f %f", self.__current_cell.x, self.__current_cell.y, self.__current_cell.g, self.__current_cell.h, self.__current_cell.f)
            logger.info("Lowest Cell (%d %d), g %f, h %f, f %f", c_lowest.x, c_lowest.y, c_lowest.g, c_lowest.h, c_lowest.f)
            
            self.__current_cell = c_lowest
            self.__openset.remove(self.__current_cell)
            self.__closedset.add(self.__current_cell)

            #neighbors = []
            c_x, c_y = self.__grid.cell_index(self.__current_cell.x, self.__current_cell.y)
            #diag_dir = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
            for dir_x, dir_y in [(1,0), (0,1), (-1,0), (0,-1)]:
                n_x, n_y = (c_x + dir_x, c_y + dir_y)
                if self.__grid.in_bounds(n_x, n_y):
                    # Update neighbor heuristics
                    cell = self.__grid.get_cell(n_x, n_y)
                    if cell not in self.__closedset and cell.type != WALL:
                        self.__update_cell_heuristics(n_x, n_y, e_x, e_y)

                        # Check for diagonals adjacent to neighbor and update them
                        if dir_y == 0:
                            d_y1 = n_y - 1
                            d_y2 = n_y + 1
                            if self.__grid.in_bounds(n_x, d_y1):
                                self.__update_cell_heuristics(n_x, d_y1, e_x, e_y, cell)
                            if self.__grid.in_bounds(n_x, d_y2):
                                self.__update_cell_heuristics(n_x, d_y2, e_x, e_y, cell)
                        elif dir_x == 0:
                            d_x1 = n_x - 1
                            d_x2 = n_x + 1
                            if self.__grid.in_bounds(d_x1, n_y):
                                self.__update_cell_heuristics(d_x1, n_y, e_x, e_y, cell)
                            if self.__grid.in_bounds(d_x2, n_y):
                                self.__update_cell_heuristics(d_x2, n_y, e_x, e_y, cell)             
            logger.info("Processed a step of astar")

    def __update_cell_heuristics(self, x, y, end_x, end_y, diag_cell=None):
        cell = self.__grid.get_cell(x, y)
        if cell not in self.__closedset and cell.type != WALL:
            if diag_cell == None:
                g = self.__current_cell.g + 1.0
                h = diagonal_heur(x, y, end_x, end_y)
                f = g + h
                if g < cell.g:
                    cell.g = g
                    cell.h = h
                    cell.f = f
                    cell.previous = self.__current_cell
                    if cell not in self.__openset:
                        self.__openset.add(cell)
            else:
                g = self.__current_cell.g + 1.4
                h = diagonal_heur(x, y, end_x, end_y)
                f = g + h
                if g < cell.g:
                    cell.g = g
                    cell.h = h
                    cell.f = f
                    cell.previous = self.__current_cell
                    if cell not in self.__openset:
                        self.__openset.add(cell)

    def __reset_heuristics(self):
        for c in self.__grid:
            c.h = 0
            c.g = 100000
            c.f = 0
            c.previous = None

    def reset(self, maze):
        self.__grid = maze
        self.__openset = set()
        self.__openset.add(self.__grid.start_cell)
        self.__closedset = set()
        self.__current_cell = self.__grid.start_cell
        self.__reset_heuristics()
        self.__current_cell.g = 0
        self.solved = False

    # Reconstruc path from current cell
    def __get_path(self):
        res = []
        cur = self.__current_cell
        while cur.previous != None:
            res.append(cur)
            cur = cur.previous
        res.append(cur)
        return res

    def show(self, window):
        # First draw openset in light green
        for c in self.__openset:
            c.show(window, (0, 150, 50))
        # Then draw closedset in dark green
        for c in self.__closedset:
            c.show(window, (0, 100, 25))
        # And at last construct path and draw it in bright green
        path = self.__get_path()
        for c in path:
            c.show(window, (0, 250, 100))


class BFS(PathFinder):
    def __init__(self):
        pass

    def solve_step(self, parameter_list):
        pass

    def reset(self):
        pass

    def show(self):
        pass
