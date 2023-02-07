import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from abc import ABC, abstractmethod
import math
import heapq
from collections import deque
import random

from cell_grid import CellGrid, Cell, CellType, CELL_COLORS


class Solver(ABC):

    def __init__(self, name, grid: CellGrid):
        self.name = name
        self._grid = grid
        self.solved = False
        self.no_path = False

    def reset(self, grid: CellGrid):
        self._grid = grid
        self.solved = False
        self.no_path = False

    def show(self, surface):
        raise NotImplementedError

    def solve_step(self):
        raise NotImplementedError
    
    def solve_all(self):
        if self.solved or self.no_path:
            return
        while not self.solved and not self.no_path:
            self.solve_step()

    # Check if cell is being used by solver
    def cell_in_use(self, cell: Cell):
        raise NotImplementedError

    def get_path(self):
        raise NotImplementedError

    def get_cells_in_use(self):
        raise NotImplementedError


###############################################################
#####               PATHFINDING SOLVERS                   #####
###############################################################


def manhattan_heur(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


def euclidean_heur(x1, y1, x2, y2):
    x = abs(x1 - x2)
    y = abs(y1 - y2)
    return math.sqrt(x*x + y*y)


def octile_heur(x1, y1, x2, y2):
    x = abs(x1 - x2)
    y = abs(y1 - y2)
    mmin = min(x, y)
    mmax = max(x, y)
    d = mmax - mmin
    return math.sqrt(mmin*mmin + mmin*mmin) + d


# A* (A-star) path finding algorithm
class Astar(Solver):
    def __init__(self, name, grid: CellGrid):
        super().__init__(name, grid)
        self.__openset = set()
        self.__closedset = set()
        self.__current_cell = None
        #self.no_path = False
        #self.reset(self._grid)

    # Solve 1 step of astar
    def solve_step(self):
        #logger.info("Solving 1 step of astar")
        if self.solved or self.no_path:
            return
        
        if len(self.__openset) == 0:
            self.no_path = True
            logger.info('No possible path!')
            return

        if self.__current_cell == self._grid.end_cell:
            logger.info("Found shortest path with Astar! length: %d", len(self._grid.get_path(self.__current_cell)))
            self.solved = True
            return

        #logger.info("Solving 1 step of astar")
        # End cell indices
        e_x, e_y = (self._grid.end_cell.x, self._grid.end_cell.y)

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
            if not self._grid.in_bounds(n_x, n_y):
                continue
            
            # Update adjacent neighbor heuristics
            cell = self._grid.get_cell(n_x, n_y)
            if cell not in self.__closedset and cell.type != CellType.WALL:
                self.__update_cell_heuristics(n_x, n_y, 1)

                diag_g = 1.414213
                # Check for diagonals adjacent to neighbor and update them
                if dir_y == 0:
                    d_y1 = n_y - 1
                    d_y2 = n_y + 1
                    if self._grid.in_bounds(n_x, d_y1):
                        self.__update_cell_heuristics(n_x, d_y1, diag_g)
                    if self._grid.in_bounds(n_x, d_y2):
                        self.__update_cell_heuristics(n_x, d_y2, diag_g)
                elif dir_x == 0:
                    d_x1 = n_x - 1
                    d_x2 = n_x + 1
                    if self._grid.in_bounds(d_x1, n_y):
                        self.__update_cell_heuristics(d_x1, n_y, diag_g)
                    if self._grid.in_bounds(d_x2, n_y):
                        self.__update_cell_heuristics(d_x2, n_y, diag_g)

    def cell_in_use(self, cell):
        return cell == self.__current_cell or cell in self.__openset or cell in self.__closedset or cell == self._grid.start_cell or cell == self._grid.end_cell

    def get_cells_in_use(self):
        return list(self.__openset) + list(self.__closedset)

    # Parameters x and y are position of cell to be updated, g is g-cost from previous cell
    def __update_cell_heuristics(self, x, y, g):
        cell = self._grid.get_cell(x, y)
        if cell not in self.__closedset and cell.type != CellType.WALL:
            g = self.__current_cell.g + g
            h = octile_heur(cell.x, cell.y, self._grid.end_cell.x, self._grid.end_cell.y)
            if g < cell.g:
                cell.g = g
                cell.h = h
                cell.f = g + h
                cell.previous = self.__current_cell
                if cell not in self.__openset:
                    self.__openset.add(cell)

    # Reset cell heuristics in grid
    def __reset_heuristics(self):
        for c in self._grid:
            c.h = 0
            c.g = 1000000
            c.f = 0
            c.previous = None

    # Reset astar solving
    def reset(self, grid):
        self._grid = grid
        self.__openset = set()
        self.__openset.add(self._grid.start_cell)
        self.__closedset = set()
        self.__current_cell = self._grid.start_cell
        self.__reset_heuristics()
        self.__current_cell.g = 0
        self.solved = False
        self.no_path = False

    # Draw openset, closedset and path
    def show(self, surface):
        # First draw openset in light green
        for c in self.__openset:
            c.show(surface, (0, 150, 50))
        # Then draw closedset in dark green
        for c in self.__closedset:
            c.show(surface, (0, 100, 25))
        # And at last construct path and draw it in bright green
        if self.solved or len(self.__openset) > 0:
            path = self._grid.get_path(self.__current_cell)
            for c in path:
                c.show(surface, (0, 220, 100))
            self.__current_cell.show(surface, (100, 250, 150))
        self._grid.start_cell.show(surface)
        self._grid.end_cell.show(surface)

    def get_path(self):
        return self._grid.get_path(self.__current_cell)


class Dijkstra(Solver):
    def __init__(self, name, grid: CellGrid):
        super().__init__(name, grid)
        self.__visited = set()
        self.__unvisited = []
        self.__current_cell = None
        self.no_path = False
        self.reset(self._grid)
    
    def solve_step(self):
        #if len(self.__unvisited) > 0 and not self.solved:
        if self.solved or self.no_path:
            return
        if len(self.__unvisited) == 0:
            self.no_path = True
            logger.info('No possible path!')
            return

        if self.__current_cell == self._grid.end_cell:
            logger.info("Found path with %s! length: %d", self.name, len(self._grid.get_path(self.__current_cell)))
            self.solved = True
            return
        
        logger.debug('Solving one step of Dijkstra!')
        cur_g, cur_cell = heapq.heappop(self.__unvisited)
        self.__visited.add(cur_cell)
        tempnbrs = []
        for dir_x, dir_y in [(1,0), (0,1), (-1,0), (0,-1)]:
            n_x, n_y = (cur_cell.x + dir_x, cur_cell.y + dir_y)
            
            if not self._grid.in_bounds(n_x, n_y):
                continue

            nc = self._grid.get_cell(n_x, n_y)
            if nc not in self.__visited and nc.type != CellType.WALL:
                # Update neighbor
                self.__update_cell_heuristics(n_x, n_y, cur_g + 1.0, cur_cell)
                tempnbrs.append(nc)

                # Update adjacent diagonals
                diag_g = 1.414213
                if dir_x == 0:
                    x1 = n_x - 1
                    x2 = n_x + 1
                    if self._grid.in_bounds(x1, n_y):
                        self.__update_cell_heuristics(x1, n_y, cur_g + diag_g, cur_cell)
                        c = self._grid.get_cell(x1, n_y)
                        if c not in tempnbrs and c not in self.__visited and c.type != CellType.WALL:
                            tempnbrs.append(c)
                    if self._grid.in_bounds(x2, n_y):
                        self.__update_cell_heuristics(x2, n_y, cur_g + diag_g, cur_cell)
                        c = self._grid.get_cell(x2, n_y)
                        if c not in tempnbrs and c not in self.__visited and c.type != CellType.WALL:
                            tempnbrs.append(c)
                elif dir_y == 0:
                    y1 = n_y - 1
                    y2 = n_y + 1
                    if self._grid.in_bounds(n_x, y1):
                        self.__update_cell_heuristics(n_x, y1, cur_g + diag_g, cur_cell)
                        c = self._grid.get_cell(n_x, y1)
                        if c not in tempnbrs and c not in self.__visited and c.type != CellType.WALL:
                            tempnbrs.append(c)
                    if self._grid.in_bounds(n_x, y2):
                        self.__update_cell_heuristics(n_x, y2, cur_g + diag_g, cur_cell)
                        c = self._grid.get_cell(n_x, y2)
                        if c not in tempnbrs and c not in self.__visited and c.type != CellType.WALL:
                            tempnbrs.append(c)

        # Update current cell and sort unvisited cells
        self.__current_cell = cur_cell
        for nbr in tempnbrs:
            self.__unvisited.append((nbr.g, nbr))
        self.__sort_unvisited()
    
    #def solve_all(self):
    #    logger.info('Solving %s!', self.name)
    #    while not self.solved and len(self.__unvisited) > 0:
    #        self.solve_step()

    def cell_in_use(self, cell):
        return cell == self.__current_cell or cell in self.__unvisited or cell in self.__visited or cell == self._grid.start_cell or cell == self._grid.end_cell

    def get_cells_in_use(self):
        return list(self.__unvisited) + list(self.__visited)

    def __update_cell_heuristics(self, x, y, g, cur_cell):
        c = self._grid.get_cell(x, y)
        if g < c.g and c not in self.__visited and c.type != CellType.WALL:
            c.g = g
            c.previous = cur_cell

    # Function to heapify unvisited cells
    def __sort_unvisited(self):
        #cells = [(cell.g, cell) for c_g, cell in self.__unvisited if cell not in self.__visited]
        self.__unvisited = [(cell.g, cell) for c_g, cell in self.__unvisited if cell not in self.__visited]
        setattr(Cell, "__lt__", lambda self, other: self.g < other.g)
        heapq.heapify(self.__unvisited)
    
    def __reset_heuristics(self):
        for c in self._grid:
            c.g = 100000
            c.previous = None
        self.__current_cell.g = 0

    def reset(self, grid):
        self._grid = grid
        self.__current_cell = grid.start_cell
        self.__visited = set()
        self.__unvisited = []
        self.__reset_heuristics()
        self.__unvisited.append((self.__current_cell.g, self.__current_cell))
        self.__sort_unvisited()
        self.solved = False
        self.no_path = False
        
    def show(self, surface):
        for c in self.__visited:
            c.show(surface, (0, 150, 40))
        if self.solved or len(self.__unvisited) > 0:
            path = self._grid.get_path(self.__current_cell)        
            for c in path:
                c.show(surface, (0, 200, 100))
        self._grid.start_cell.show(surface)
        self._grid.end_cell.show(surface)

    def get_path(self):
        return self._grid.get_path(self.__current_cell)

# Depth First Search
class DFS(Solver):
    def __init__(self, name, grid: CellGrid):
        super().__init__(name, grid)
        self.__stack = deque()
        self.__visited = set()
        self.__current_cell = None
        #self.reset(self._grid)
        self.no_path = False

    def solve_step(self):
        if len(self.__stack) == 0 or self.no_path:
            return
            
        c = self.__stack.pop()
        self.__visited.add(c)
        self.__current_cell = c
        nbrs = self._grid.get_neighbors(c.x, c.y)
        nbrs = [x for x in nbrs if x not in self.__visited and x.type != CellType.WALL]
        for nbr in nbrs:
            self.__stack.append(nbr)
            nbr.previous = self.__current_cell

        if self.__current_cell == self._grid.end_cell:
            logger.info("Found path with %s! length: %d", self.name, len(self._grid.get_path(self.__current_cell)))
            self.solved = True
        elif len(self.__stack) == 0:
            logger.info('No valid path!')
            #self.solved = True  # TODO Fix when no path
            self.no_path = True

    def cell_in_use(self, cell):
        return cell == self.__current_cell or cell in self.__visited or cell in self.__stack or cell == self._grid.start_cell or cell == self._grid.end_cell

    def get_cells_in_use(self):
        return list(self.__stack) + list(self.__visited)
    
    def reset(self, grid):
        self._grid = grid
        for c in self._grid:
            c.previous = None
        self.__visited = set()
        self.__stack = deque()
        self.__current_cell: Cell = None
        self.__stack.append(self._grid.start_cell)
        self.solved = False
        self._no_path = False

    def show(self, surface):
        for c in self.__visited:
            c.show(surface, (0, 100, 30))
        for c in self.__stack:
            c.show(surface, (0, 150, 40))
        if self.__current_cell != None and self.__current_cell.previous != None:
            path = self._grid.get_path(self.__current_cell.previous)
            for c in path:
                c.show(surface, (0, 200, 100))
        self._grid.start_cell.show(surface)
        self._grid.end_cell.show(surface)

    def get_path(self):
        return self._grid.get_path(self.__current_cell)


###############################################################
#####              MAZEGENERATOR SOLVERS                  #####
###############################################################


def get_cell_in_between(grid: CellGrid, c1, c2):
    x_off = int((c1.x - c2.x) / 2)
    y_off = int((c1.y - c2.y) / 2)
    return grid.get_cell(c2.x + x_off, c2.y + y_off)


# Prim's algorithm
class PrimGenerator(Solver):
    def __init__(self, name, grid: CellGrid):
        super().__init__(name, grid)
        self.__maze_todo = set()
        self.__visited = set()

    # Reset maze generating
    def reset(self, grid):
        self._grid = grid
        self.__maze_todo = set()
        self.__visited = set()
        self._grid.set_cell_type_forall(CellType.WALL)
        # Get first cell by random
        cell = self._grid.start_cell
        cell.type = CellType.FLOOR
        self.__visited.add(cell)
        # Get neighbors of the first cell and add them to todo set
        c_x, c_y = (cell.x, cell.y)
        for c in self._grid.get_neighbors(c_x, c_y, 2):
            self.__maze_todo.add(c)
        self.solved = False

    def show(self, surface):
        # Draw maze todo set
        for c in self.__maze_todo:
            c.show(surface, (0,200, 40))

    def solve_step(self):
        if self.solved and len(self.__maze_todo) == 0:
            return

        #if len(self.__maze_todo) > 0:
        # Get random cell from todo set
        cell = random.choice(list(self.__maze_todo))
        self.__visited.add(cell)

        # Get neighbors around our current cell
        nbrs = self._grid.get_neighbors(cell.x, cell.y, 2)
        nbrs = [x for x in nbrs if self._grid.in_bounds(x.x, x.y, 1) and x.type != CellType.WALL]
        
        if len(nbrs) > 0:
            rand_nbr = nbrs[random.randint(0, len(nbrs)-1)]
            if self._grid.in_bounds(cell.x, cell.y, 1):
                nbr_nbrs = self._grid.get_neighbors(cell.x, cell.y, 2)
                for nbr in nbr_nbrs:
                    if self._grid.in_bounds(nbr.x, nbr.y, 1) and nbr not in self.__maze_todo and nbr not in self.__visited:
                        self.__maze_todo.add(nbr)
                cell.type = CellType.FLOOR
                # Set cell in between to floor
                get_cell_in_between(self._grid, cell, rand_nbr).type = CellType.FLOOR
                
        self.__maze_todo.remove(cell)

        if not self.__maze_todo:
            self.solved = True
    
    def cell_in_use(self, cell):
        return cell in self.__maze_todo or cell in self.__visited

    def get_cells_in_use(self):
        return []

    def get_path(self):
        pass


class BackTrackGenerator(Solver):
    def __init__(self, name, grid: CellGrid):
        super().__init__(name, grid)
        self.__stack = deque()
        self.__stack_cib = deque()  # Only for rendering, holds cells in between
        self.__current_cell = None

    def show(self, surface):
        for c in self.__stack:
            c.show(surface,  (0, 150, 50))
        for c in self.__stack_cib:
            c.show(surface, (0, 150, 50))
        if self.__current_cell:
            self.__current_cell.show(surface, (0, 200, 50))

    def solve_step(self):
        if len(self.__stack) == 0:
            self.solved = True
            return
        
        nbrs = self._grid.get_neighbors(self.__current_cell.x, self.__current_cell.y, 2)
        nbrs = [x for x in nbrs if self._grid.in_bounds(x.x, x.y, 1) and x.type == CellType.WALL]
        if len(nbrs) > 0:
            nbr = nbrs[random.randint(0, len(nbrs)-1)]
            nbr.type = CellType.FLOOR
            cib = get_cell_in_between(self._grid, nbr, self.__current_cell)
            cib.type = CellType.FLOOR
            self.__current_cell = nbr
            self.__stack.append(self.__current_cell)
            self.__stack_cib.append(cib)
        else:
            self.__current_cell = self.__stack.pop()
            if len(self.__stack_cib) > 0:
                self.__stack_cib.pop()

    def reset(self, grid):
        self._grid = grid
        self.__stack = deque()
        self.__stack_cib = deque()
        self.__current_cell = self._grid.start_cell
        self.__stack.append(self.__current_cell)
        self._grid.set_cell_type_forall(CellType.WALL)
        self.__current_cell.type = CellType.FLOOR
        self.solved = False

    def cell_in_use(self, cell):
        return cell in self.__stack

    def get_path(self):
        pass

    def get_cells_in_use(self):
        return []

# Divide and Conquer algorithm
class DNQGenerator(Solver):
    def __init__(self, name, grid: CellGrid):
        super().__init__(name, grid)
        self.__que = deque()
        self.__current_pos = None

    def show(self, surface):
        if not self.solved and self.__current_pos:
            for c in self.__get_cells(self.__current_pos[0], self.__current_pos[1]):
                c.show(surface, (0, 150, 40))

    def __get_cells(self, pos1, pos2):
        res = []
        if pos1[0] == pos2[0]:
            for i in range(pos1[1], pos2[1]):
                res.append(self._grid.get_cell(pos1[0], i))
        else:
            for i in range(pos1[0], pos2[0]):
                res.append(self._grid.get_cell(i, pos1[1]))
        return res

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
            self._grid.get_cell(mx, my).type = CellType.WALL
            mx += dx
            my += dy
        self._grid.get_cell(fx, fy).type = CellType.FLOOR

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
            self.solved = True
            self.__current_pos = None
        else:
            self.__current_pos = (first, (mx, my))

    def solve_step(self):
        if self.solved and len(self.__que) == 0:
            return

        x, y, w, h = self.__que.pop()
        horizontal = True if w < h else False if w > h else random.choice([True, False])
        self.__divide(x, y, w, h, horizontal)

    def reset(self, grid):
        self._grid = grid
        self.__que = deque()
        self._grid.set_cell_type_forall(CellType.FLOOR)
        # Set edges to WALL
        for i in range(0, self._grid.size):
            self._grid.set_cell_type(i, 0, CellType.WALL)
            self._grid.set_cell_type(0, i, CellType.WALL)
            self._grid.set_cell_type(self._grid.size - 1, i, CellType.WALL)
            self._grid.set_cell_type(i, self._grid.size - 1, CellType.WALL)
        self.__que.append((1, 1, self._grid.size-2, self._grid.size-2))
        self.solved = False
        self.__current_pos = None

    def cell_in_use(self, cell):
        return cell in self.__que

    def get_path(self):
        pass

    def get_cells_in_use(self):
        return []


class HuntAndKill(Solver):
    def __init__(self, name, grid: CellGrid):
        super().__init__(name, grid)
        self.__visited = set()
        self.__current_cell = None
        self.__cur_y = 1

    def reset(self, grid):
        self._grid = grid
        self.__visited = set()
        self.__current_cell = self._grid.get_cell(1, 1)
        self._grid.set_cell_type_forall(CellType.WALL)
        self.__current_cell.type = CellType.FLOOR
        self.__cur_y = 1
        self.solved = False

    def show(self, surface):
        if not self.solved and self.__current_cell == None:
            for i in range(1, self._grid.size-2):
                c = self._grid.get_cell(i, self.__cur_y)
                c.show(surface, (0, 180, 50))
        if self.__current_cell != None:
            self.__current_cell.show(surface, (20, 250, 40))

    def __hunt_new_current(self):
        for j in range(self.__cur_y, self._grid.size-1, 2):
            for i in range(1, self._grid.size-1, 2):
                c = self._grid.get_cell(i, j)
                if c in self.__visited:
                    continue

                nbrs = self._grid.get_neighbors(i, j, 2)
                nbrs = [c for c in nbrs if c in self.__visited]
                if len(nbrs) == 0:
                    continue
                
                r_nbr = nbrs[random.randint(0, len(nbrs)-1)]
                c.type = CellType.FLOOR
                get_cell_in_between(self._grid, r_nbr, c).type = CellType.FLOOR
                self.__current_cell = c
                self.__cur_y = j
                return c
        return None

    # Random walk
    # or Hunt next spot
    def solve_step(self):
        if self.__current_cell != None:
            nbrs = self._grid.get_neighbors(self.__current_cell.x, self.__current_cell.y, 2)
            nbrs = [c for c in nbrs if c not in self.__visited and c.type == CellType.WALL and self._grid.in_bounds(c.x, c.y, 1)]

            if len(nbrs) > 0:
                # Random walk
                r_nbr = nbrs[random.randint(0, len(nbrs)-1)]
                r_nbr.type = CellType.FLOOR
                get_cell_in_between(self._grid, self.__current_cell, r_nbr).type = CellType.FLOOR
                self.__visited.add(self.__current_cell)
                self.__current_cell = r_nbr
            else:
                self.__visited.add(self.__current_cell)
                self.__current_cell = None

        elif not self.solved:
            c = self.__hunt_new_current()
            if c == None:
                logger.info("Generated maze with Hunt and Kill!")
                self.solved = True

    def cell_in_use(self, cell):
        return cell in self.__visited or cell == self.__current_cell

    def get_path(self):
        pass

    def get_cells_in_use(self):
        return []


class BinaryTree(Solver):
    def __init__(self, name, grid: CellGrid):
        super().__init__(name, grid)
        self.__current_cell = None
        self.__dirs = [(1, -1), (1, 1), (-1, 1), (-1, -1)] # NE, SE, SW, NW
        self.__cd_idx = 0 # Current index in __dirs
        self.__visited = []

    def reset(self, grid):
        self._grid = grid
        self._grid.set_cell_type_forall(CellType.WALL)
        self.__current_cell = self._grid.get_cell(1, 1)
        self.solved = False

    def show(self, surface):
        if self.__current_cell:
            self.__current_cell.show(surface, (0, 250, 50))

    def solve_step(self):
        if self.solved:
            return

        nx = self.__current_cell.x + 2
        ny = self.__current_cell.y
        if nx > self._grid.size - 2:
            nx = 1
            ny += 2
        if ny > self._grid.size - 2:
            logger.info("Generated maze with %s!", self.name)
            self.__current_cell = None
            self.solved = True
            return
            
        c = self._grid.get_cell(nx, ny)

        dirs = [(self.__dirs[self.__cd_idx][0], 0), (0, self.__dirs[self.__cd_idx][1])]
        cells = [self._grid.get_cell(nx + x[0], ny + x[1]) for x in dirs if self._grid.in_bounds(nx + x[0], ny + x[1], 1)]

        if len(cells) > 0:
            rc = cells[random.randint(0, len(cells) - 1)]
            rc.type = CellType.FLOOR
            get_cell_in_between(self._grid, rc, c).type = CellType.FLOOR

        self.__current_cell = c

    def cell_in_use(self, cell):
        return cell == self.__current_cell

    # Set
    def set_direction(self, dir):
        self.__cd_idx = dir
        self.reset(self._grid)

    def get_path(self):
        pass

    def get_cells_in_use(self):
        return []

PATHFINDERS = [
    'Astar',
    'Dijkstra',
    'DFS'
]

SOLVERS = {
    # Path finders
    'Astar': Astar,
    'Dijkstra': Dijkstra,
    'DFS': DFS,

    # Maze generators
    'Prim': PrimGenerator,
    'BackTrack': BackTrackGenerator,
    'DivideAndConquer': DNQGenerator,
    'HuntAndKill': HuntAndKill,
    'BinaryTree': BinaryTree
}