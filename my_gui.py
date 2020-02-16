import pygame
import pygame_gui
from pygame_gui import UIManager
from pygame_gui.core import UIWindow
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.elements import UIDropDownMenu, UITextEntryLine, UIButton

DROPDOWN_MARGIN = 10
DROPDOWN_HEIGHT = 50
OFFSCREEN = 1000
CONTAINER_OFFSET = DROPDOWN_HEIGHT + (DROPDOWN_MARGIN * 2)
SAVE_OFFSET = 250

modes = ["Editor", "Pathfinder", "Mazegenerator"]
solve_algos = ["Astar", "BFS", "DFS"]
maze_algos = ["Prim's", "Kruskal", "Divide & Conquer"]

class MyGui():
    def __init__(self, width, height, offset):
        self.mode = 0
        self.gui_manager = UIManager((width, height))
        self.width = width
        self.height = height
        self.offset = offset
        self.sidebar_container = UIContainer(pygame.Rect((self.offset, 0), (self.width, self.height)), self.gui_manager)
        self.mode_drop_down = UIDropDownMenu(modes, modes[0],
                                            pygame.Rect((DROPDOWN_MARGIN, DROPDOWN_MARGIN), (self.width - (DROPDOWN_MARGIN*2), DROPDOWN_HEIGHT)),
                                            manager=self.gui_manager,
                                            container=self.sidebar_container)
        self.mode_containers = []
        editor_container    = UIContainer(pygame.Rect((DROPDOWN_MARGIN, CONTAINER_OFFSET), (self.width, self.height - CONTAINER_OFFSET)), self.gui_manager)
        solve_container     = UIContainer(pygame.Rect((DROPDOWN_MARGIN, CONTAINER_OFFSET), (self.width, self.height - CONTAINER_OFFSET)), self.gui_manager)
        generator_container = UIContainer(pygame.Rect((DROPDOWN_MARGIN, CONTAINER_OFFSET), (self.width, self.height - CONTAINER_OFFSET)), self.gui_manager)
        self.mode_containers.append(editor_container) # First is editor
        self.mode_containers.append(solve_container) # Second is solver
        self.mode_containers.append(generator_container) # Third is generator
        
        self.sidebar_container.add_element(editor_container)
        self.sidebar_container.add_element(solve_container)
        self.sidebar_container.add_element(generator_container)

        self.init_editor_container()
        self.pf_alg_drop_down = UIDropDownMenu(solve_algos, solve_algos[0],
                                            pygame.Rect((self.offset + DROPDOWN_MARGIN, CONTAINER_OFFSET), (self.width - 20, DROPDOWN_HEIGHT)),
                                            manager=self.gui_manager, container=solve_container)
        self.mg_alg_drop_down = UIDropDownMenu(maze_algos, maze_algos[0],
                                            pygame.Rect((self.offset + DROPDOWN_MARGIN, CONTAINER_OFFSET), (self.width - 20, DROPDOWN_HEIGHT)),
                                            manager=self.gui_manager, container=generator_container)
        self.mode_containers[0].set_position((0, 0))
        self.mode_containers[1].set_position((OFFSCREEN, OFFSCREEN))
        self.mode_containers[2].set_position((OFFSCREEN, OFFSCREEN))
        self.sidebar_container.update_containing_rect_position()
        
    def init_editor_container(self):
        fname_text_box = UITextEntryLine(pygame.Rect(self.offset + DROPDOWN_MARGIN, SAVE_OFFSET, self.width - 20, DROPDOWN_HEIGHT),
                                        manager=self.gui_manager, container=self.mode_containers[0])
        fname_text_box.set_text("FILUGO")
        
        save_button = UIButton(pygame.Rect(self.offset + DROPDOWN_MARGIN, SAVE_OFFSET + DROPDOWN_HEIGHT, (self.width - 40) / 2, DROPDOWN_HEIGHT),
                                        "Save", manager=self.gui_manager, container=self.mode_containers[0])
        load_button = UIButton(pygame.Rect(self.offset + DROPDOWN_MARGIN + (self.width) / 2, SAVE_OFFSET + DROPDOWN_HEIGHT, (self.width - 40) / 2, DROPDOWN_HEIGHT),
                                        "Load", manager=self.gui_manager, container=self.mode_containers[0])

    def init_solve_container(self):
        pf_alg_drop_down = UIDropDownMenu(solve_algos, solve_algos[0],
                                        pygame.Rect(self.offset + DROPDOWN_MARGIN, CONTAINER_OFFSET, self.width - 20, DROPDOWN_HEIGHT),
                                        manager=self.gui_manager, container=self.mode_containers[1])

    def init_maze_container(self):
        mg_alg_drop_down = UIDropDownMenu(maze_algos, maze_algos[0],
                                        pygame.Rect(self.offset + DROPDOWN_MARGIN, CONTAINER_OFFSET, self.width - 20, DROPDOWN_HEIGHT),
                                        manager=self.gui_manager, container=self.mode_containers[2])

    def set_sidebar(self, oldmode, newmode):
        self.mode_containers[oldmode].set_position((OFFSCREEN, OFFSCREEN))
        self.mode_containers[newmode].set_position((0, 0))
        self.sidebar_container.update_containing_rect_position()

    def process_events(self, event):
        self.gui_manager.process_events(event)

    def update(self, time_delta):
        self.gui_manager.update(time_delta)

    def show(self, window):
        self.gui_manager.draw_ui(window)