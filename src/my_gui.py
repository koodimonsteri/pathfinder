import pygame
import pygame_gui
from pygame_gui import UIManager
from pygame_gui.core import UIWindow
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.core.ui_element import UIElement
from pygame_gui.elements import UIDropDownMenu, UITextEntryLine, UIButton, UITextBox
from pygame import locals
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Sidebar global offsets
# Sidebar size
SIDEBAR_HEIGHT = 400
SIDEBAR_WIDTH = 200
# Margin size
MARGIN = 10
# Mode text box height
BOX_HEIGHT = 40
# Update mode box height

# Container y offset

modes = ["Editor", "Pathfinder", "Mazegenerator"]
mode_key_str = [" (1)", " (2)", " (3)"]
solve_algos = ["Astar", "Dijkstra", "DFS"]
maze_algos = ["Prim's", "RecursiveBackTrack", "Divide & Conquer"]
update_modes = ["Step", "Continous", "Instant"]

# Editor window which contains essential information and save/load functionality
class EditorWindow(UIWindow):
    def __init__(self, my_rect, manager):
        editor_id = ["Editor"]
        super().__init__(my_rect, manager=manager, element_ids=editor_id)
        # Clearing button
        self.clear_button = UIButton(relative_rect = pygame.Rect(0, 0, my_rect.width, BOX_HEIGHT),
                                    text="Clear",
                                    manager=manager,
                                    container=self.get_container())
        # Info text box
        info_offset_y = BOX_HEIGHT + MARGIN
        info_height = 120
        logger.info("myrect height %f", my_rect.height)
        self.info_text = "<font size=2>Keys 1-3 to change mode<br>'W' to place wall<br>'F' to place floor<br>'S' to place start<br>'E' to place end<br>'SPACE' to step"
        self.info_text_box1 = UITextBox(self.info_text,
                                        relative_rect = pygame.Rect(0, info_offset_y, my_rect.width, info_height),
                                        manager = manager,
                                        container = self.get_container())
        
        # Loading/saging related things
        load_height = (BOX_HEIGHT * 2) + MARGIN
        load_offset_y = my_rect.height - load_height
        load_rect = pygame.Rect(0, load_offset_y, my_rect.width, load_height)
        self.load_container = UIContainer(load_rect, manager=manager, container=self.get_container())
        self.fname_text_box = UITextEntryLine(relative_rect=pygame.Rect(0, 0, my_rect.width, BOX_HEIGHT),
                                            manager=manager,
                                            container=self.load_container)
        self.fname_text_box.set_text("File name.txt")
        # Save and load buttons
        button_offset_y = BOX_HEIGHT + MARGIN
        button_width = (my_rect.width / 2) - MARGIN
        self.save_button = UIButton(relative_rect=pygame.Rect(0, button_offset_y, button_width, BOX_HEIGHT),
                                    text = "Save",
                                    manager = manager,
                                    container = self.load_container)
        self.load_button = UIButton(relative_rect=pygame.Rect((MARGIN *2) + button_width, button_offset_y, button_width, BOX_HEIGHT),
                                    text = "Load",
                                    manager = manager,
                                    container = self.load_container)


# Solver window to swap between different pathfinding algorithms
class SolverWindow(UIWindow):
    def __init__(self, rect, manager, alg_idx):
        editor_id = ["Solver"]
        super().__init__(rect, manager, element_ids=editor_id)
        self.pf_alg_drop_down = UIDropDownMenu(solve_algos,
                                            solve_algos[alg_idx],
                                            pygame.Rect(0, 0, SIDEBAR_WIDTH - 20, BOX_HEIGHT),
                                            manager=manager,
                                            container=self.get_container())
        
    

# Generator window to swap between different maze algorithms
class GeneratorWindow(UIWindow):
    def __init__(self, rect, manager, alg_idx):
        editor_id = ["Generator"]
        super().__init__(rect, manager, element_ids=editor_id)
        self.mg_alg_drop_down = UIDropDownMenu(maze_algos,
                                            maze_algos[alg_idx],
                                            pygame.Rect(0, 0, SIDEBAR_WIDTH - 20, BOX_HEIGHT),
                                            manager=manager,
                                            container=self.get_container())

class CustomToggleBox(UIWindow):
    def __init__(self, side_cont, manager):
        side_rect = side_cont.rect
        my_rect = pygame.Rect(side_rect.x + MARGIN, side_rect.y + BOX_HEIGHT + (MARGIN * 2), side_rect.width - (MARGIN * 2), BOX_HEIGHT)
        super().__init__(my_rect, manager, element_ids=update_modes)
        self.current_mode = 1
        bw = (my_rect.width) / 3
        self.buttons = []
        self.step_button      = UIButton(pygame.Rect(0, 0, bw, BOX_HEIGHT),
                                        text = "STEP",
                                        manager = manager,
                                        container = self.get_container(),
                                        object_id = "StepButton",
                                        tool_tip_text = "Step by step updating")
        self.continous_button = UIButton(pygame.Rect(bw, 0, bw, BOX_HEIGHT),
                                        text = "CONT",
                                        manager = manager,
                                        container = self.get_container(),
                                        object_id = "ContinousButton",
                                        tool_tip_text = "Continous updating")
        self.instant_button   = UIButton(pygame.Rect(bw * 2, 0, bw, BOX_HEIGHT),
                                        text = "INST",
                                        manager = manager,
                                        container = self.get_container(),
                                        object_id = "InstantButton",
                                        tool_tip_text = "Realtime updating")
        self.buttons.append(self.step_button)
        self.buttons.append(self.continous_button)
        self.buttons.append(self.instant_button)
        self.set_mode(self.current_mode)
        #elf.continous_button.enable()
        manager.select_focus_element(self.continous_button)
        

    def set_mode(self, mode):
        #if self.current_mode != mode:
        logger.debug("Swapping update mode from %s (%d) -> %s (%d)", update_modes[self.current_mode], self.current_mode, update_modes[mode], mode)
        self.current_mode = mode
        for i, b in enumerate(self.buttons):
            if i != self.current_mode:
                b.unselect()
            else:
                b.select()

    def process_event(self, event):
        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element.text == "STEP":
                self.set_mode(0)
            elif event.ui_element.text == "CONT":
                self.set_mode(1)
            elif event.ui_element.text == "INST":
                self.set_mode(2)
            

# Simple gui class to handle different side windows
class MyGui:
    def __init__(self, manager, x, y, width, height):
        self.gui_manager = manager
        self.rect = pygame.Rect(x, y, width, height)
        #self.temp_rect = pygame.Rect(400, CONTAINER_OFFSET_Y, SIDEBAR_WIDTH, 400-CONTAINER_OFFSET_Y)
        self.sidebar_container = UIContainer(self.rect, self.gui_manager)
        self.update_mode_boxes = CustomToggleBox(self.sidebar_container, manager)
        self.mode_window_rect = pygame.Rect(x + MARGIN, y + (BOX_HEIGHT * 2) + (MARGIN * 3), width - (MARGIN * 2), height - (MARGIN * 4) - (BOX_HEIGHT * 2))
        self.current_side_bar = EditorWindow(self.mode_window_rect, self.gui_manager)
        self.mode_text_box = UITextBox(modes[0] + mode_key_str[0],
                                    pygame.Rect(MARGIN, MARGIN, width - (2 * MARGIN), BOX_HEIGHT),
                                    manager = self.gui_manager,
                                    container=self.sidebar_container)
        self.current_solve_alg = 0
        self.current_maze_alg = 0

    # Set sidebar to newmode
    # Kills old sidebar and initializes new
    def set_sidebar(self, newmode):
        self.current_side_bar.kill()
        if newmode == 0:
            self.mode_text_box.html_text = modes[newmode] + mode_key_str[newmode]
            self.mode_text_box.rebuild()
            self.current_side_bar = EditorWindow(self.mode_window_rect, self.gui_manager)
        elif newmode == 1:
            self.mode_text_box.html_text = modes[newmode] + mode_key_str[newmode]
            self.mode_text_box.rebuild()
            self.current_side_bar = SolverWindow(self.mode_window_rect, self.gui_manager, self.current_solve_alg)         
        elif newmode == 2:
            self.mode_text_box.html_text = modes[newmode] + mode_key_str[newmode]
            self.mode_text_box.rebuild()
            self.current_side_bar = GeneratorWindow(self.mode_window_rect, self.gui_manager, self.current_maze_alg)
        
    def process_events(self, event):
        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.text in solve_algos:
                self.current_solve_alg = solve_algos.index(event.text)
            elif event.text in maze_algos:
                self.current_maze_alg = maze_algos.index(event.text)
        self.gui_manager.process_events(event)

    def update(self, time_delta):
        self.gui_manager.update(time_delta)

    def show(self, window):
        self.gui_manager.draw_ui(window)

    # Crashes if called when not in editormode :)
    def get_fname_text(self):
        return self.current_side_bar.fname_text_box.get_text()


