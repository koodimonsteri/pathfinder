import pygame
import pygame_gui
from pygame_gui import UIManager
from pygame_gui.core import UIWindow
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.elements import UIDropDownMenu, UITextEntryLine, UIButton, UITextBox

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MARGIN = 10
DROPDOWN_HEIGHT = 50
OFFSCREEN = 1000
CONTAINER_OFFSET = DROPDOWN_HEIGHT + (MARGIN * 2)
SIDEBAR_WIDTH = 200

SAVE_OFFSET = 300
SAVE_TEXT_WIDTH = SIDEBAR_WIDTH - (MARGIN * 2)
SAVE_TEXT_HEIGHT = 40
SAVE_BUTTON_WIDTH = (SIDEBAR_WIDTH - (MARGIN * 4)) / 2

modes = ["Editor", "Pathfinder", "Mazegenerator"]
solve_algos = ["Astar", "BFS", "DFS"]
maze_algos = ["Prim's", "Kruskal", "Divide & Conquer"]

# Editor window which contains essential information and save/load functionality
class EditorWindow(UIWindow):
    def __init__(self, rect, manager):
        editor_id = ["Editor"]
        super().__init__(rect, manager=manager, element_ids=editor_id)
        # Clearing button
        self.clear_button = UIButton(relative_rect=pygame.Rect(MARGIN, CONTAINER_OFFSET, SIDEBAR_WIDTH-20, DROPDOWN_HEIGHT),
                                    text="Clear", manager=manager, container=self.get_container())
        # Info text box
        self.info_text = "<font size=2>Keys 1-3 to change mode<br>'S' to place start cell<br>'E' to place end cell<br>Right click to add Wall<br>Left click to remove Wall"
        self.info_text_box1 = UITextBox(self.info_text, relative_rect=pygame.Rect(MARGIN, CONTAINER_OFFSET*2-MARGIN, SAVE_TEXT_WIDTH, 160),
                                        manager=manager, container=self.get_container())
        
        # Loading/saging related things
        load_rect = pygame.Rect(0, SAVE_OFFSET, SIDEBAR_WIDTH, 100)
        self.load_container = UIContainer(load_rect, manager=manager, container=self.get_container())
        self.fname_text_box = UITextEntryLine(relative_rect=pygame.Rect(MARGIN, 0, SIDEBAR_WIDTH - (MARGIN*2), SAVE_TEXT_HEIGHT + MARGIN),
                                            manager=manager, container=self.load_container)
        self.fname_text_box.set_text("File name.txt")
        # Save and load buttons
        self.save_button = UIButton(relative_rect=pygame.Rect(MARGIN, SAVE_TEXT_HEIGHT , SAVE_BUTTON_WIDTH, SAVE_TEXT_HEIGHT),
                                    text="Save", manager=manager, container=self.load_container)
        self.load_button = UIButton(relative_rect=pygame.Rect((MARGIN*2) + SAVE_BUTTON_WIDTH, SAVE_TEXT_HEIGHT , SAVE_BUTTON_WIDTH, SAVE_TEXT_HEIGHT),
                                    text="Load", manager=manager, container=self.load_container)


# Solver window to swap between different pathfinding algorithms
class SolverWindow(UIWindow):
    def __init__(self, rect, manager):
        editor_id = ["Solver"]
        super().__init__(rect, manager, element_ids=editor_id)
        self.pf_alg_drop_down = UIDropDownMenu(solve_algos, solve_algos[0],
                                            pygame.Rect((MARGIN, CONTAINER_OFFSET), (SIDEBAR_WIDTH - 20, DROPDOWN_HEIGHT)),
                                            manager=manager, container=self.get_container())
        
# Generator window to swap between different maze algorithms
class GeneratorWindow(UIWindow):
    def __init__(self, rect, manager):
        editor_id = ["Generator"]
        super().__init__(rect, manager, element_ids=editor_id)
        self.mg_alg_drop_down = UIDropDownMenu(maze_algos, maze_algos[0],
                                            pygame.Rect((MARGIN, CONTAINER_OFFSET), (SIDEBAR_WIDTH - 20, DROPDOWN_HEIGHT)),
                                            manager=manager, container=self.get_container())

# Simple gui class to handle different side windows
class MyGui():
    def __init__(self, manager):
        self.gui_manager = manager
        self.side_rect = pygame.Rect(400, 0, SIDEBAR_WIDTH, 400)
        self.sidebar_container = UIContainer(pygame.Rect((400, 0), (SIDEBAR_WIDTH, 400)), self.gui_manager)
        self.current_side_bar = EditorWindow(self.side_rect, manager)
        self.mode_text_box = UITextBox(self.current_side_bar.element_ids[0], pygame.Rect(MARGIN, MARGIN, SIDEBAR_WIDTH - (2*MARGIN), 50), manager = self.gui_manager, container=self.sidebar_container)
        
    # Set sidebar to newmode
    # Kills old sidebar and initializes new
    def set_sidebar(self, newmode):
        self.current_side_bar.kill()
        if newmode == 0:
            self.mode_text_box.html_text = modes[newmode]
            self.mode_text_box.rebuild()
            self.current_side_bar = EditorWindow(self.side_rect, self.gui_manager)
        elif newmode == 1:
            self.mode_text_box.html_text = modes[newmode]
            self.mode_text_box.rebuild()
            self.current_side_bar = SolverWindow(self.side_rect, self.gui_manager)
        elif newmode == 2:
            self.mode_text_box.html_text = modes[newmode]
            self.mode_text_box.rebuild()
            self.current_side_bar = GeneratorWindow(self.side_rect, self.gui_manager)
        
    def process_events(self, event):
        self.gui_manager.process_events(event)

    def update(self, time_delta):
        self.gui_manager.update(time_delta)

    def show(self, window):
        self.gui_manager.draw_ui(window)

    

