from abc import ABC, abstractclassmethod
import random

from cell_grid import *


class MazeGenerator:
    def __init__(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    def generate_step(self):
        raise NotImplementedError

class PrimGenerator(MazeGenerator):
    def __init__(self, grid):
        self.__grid = grid
        self.__maze_todo = set()

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

    def show(self, window):
        # Draw maze todo set
        for c in self.__maze_todo:
            c.show(window, (0,150, 40))

    def generate_step(self):
        logger.info("Generating one step of maze")
        
        if len(self.__maze_todo) > 0:
            # Get random cell from todo set
            cell = random.choice(list(self.__maze_todo))
            
            logger.info("Random Cell (%d, %d)", cell.x, cell.y)
            c_x, c_y = self.__grid.cell_index(cell.x, cell.y)
    
            nbrs = self.__grid.get_neighbors(c_x, c_y)
            wall_count = 0
            for n in nbrs:
                if n not in self.__maze_todo and n.type == WALL:
                    wall_count += 1
            if wall_count == 3:
                for n in nbrs:
                    if n not in self.__maze_todo:
                        self.__maze_todo.add(n)
                cell.type = FLOOR
            self.__maze_todo.remove(cell)

class DNQGenerator(MazeGenerator):
    def __init__(self):
        pass

    def show(self):
        pass

    def generate_step(self):
        pass

    def reset(self):
        pass