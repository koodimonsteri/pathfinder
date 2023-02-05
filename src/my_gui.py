
import pygame
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_drop_down_menu import UIDropDownMenu
from pygame_gui.elements.ui_text_entry_box import UITextEntryBox
from pygame_gui.elements.ui_text_entry_line import UITextEntryLine

from solver import SOLVERS

def build_info_text(mode, path_text):
    res = (
        'Pathfinder<br>'
        f'Current mode: {mode}<br>'
        f'{path_text}<br>'
        'Keybinds<br>'
        'Key W: Add wall<br>'
        'Key F: Add floor<br>'
        'Key S: Move start<br>'
        'Key E: Move end<br>'
        'Key R: Reset grid<br>'
        'Key Space: Solve 1 step<br>'
        'Key Esc: Exit<br><br>'
        'Update modes:<br>'
        'Key 1: Editor<br>'
        'Key 3: Step<br>'
        'Key 4: Continous<br>'
        'Key 5: Instant<br>'
    )
    return res

class TitleBox():
    def __init__(self, gui_manager, x, y, width, height):
        self.gui_manager = gui_manager
        self.rect = pygame.Rect(x, y, width, height)
        self.text_box = UITextBox('Pathfinder', self.rect, manager=self.gui_manager)

class InfoPanel():
    
    def __init__(self, gui_manager, x, y, width, height, update_mode):
        self.gui_manager = gui_manager
        self.rect = pygame.Rect(x, y, width, height)
        self.current_mode = update_mode
        self.path_text = ''
        info_text = build_info_text(self.current_mode, self.path_text)
        self.text_box = UITextBox(info_text, self.rect, manager=self.gui_manager)

    def update_mode_text(self, mode):
        self.current_mode = mode
        info_text = build_info_text(self.current_mode, self.path_text)
        self.text_box.kill()
        self.text_box = UITextBox(info_text, self.rect, manager=self.gui_manager)

    def update_path_text(self, path_len):
        path_text = f'Path length: {path_len}' if path_len else ''
        self.path_text = path_text
        self.text_box.kill()
        info_text = build_info_text(self.current_mode, path_text)
        self.text_box = UITextBox(info_text, self.rect, manager=self.gui_manager)

class SolverDropDown():
    
    def __init__(self, gui_manager, x, y, width, height):
        self.gui_manager = gui_manager
        self.rect = pygame.Rect(x, y, width, height)
        self.dropdown = UIDropDownMenu(
            list(SOLVERS.keys()),
            list(SOLVERS.keys())[0],
            relative_rect=self.rect,
            manager=self.gui_manager
        )

class SaveLoad():

    def __init__(self, gui_manager, x, y, width, height):
        self.gui_manager = gui_manager
        self.rect = pygame.Rect(x, y, width, height)
        self.fname_text_box = UITextEntryLine(
            relative_rect=pygame.Rect(x, y, self.rect.width, self.rect.height / 2),
            manager=self.gui_manager,
        )
        self.fname_text_box.set_text("File name.txt")
        # Save and load buttons
        button_offset_y = self.rect.height / 2
        button_width = self.rect.width / 2
        self.save_button = UIButton(
            relative_rect=pygame.Rect(x, y + button_offset_y, button_width, self.rect.height / 2),
            text = "Save",
            manager = self.gui_manager
        )
        self.load_button = UIButton(
            relative_rect=pygame.Rect(x + button_width, y + button_offset_y, button_width, self.rect.height / 2),
            text = "Load",
            manager = self.gui_manager,
        )


class MyGui():
    def __init__(self, x, y, width, height, update_mode):
        self.gui_manager = UIManager((x + width, y + height), '../res/button_theme.json')
        self.rect = pygame.Rect(x, y, width, height)
        self.title_box = TitleBox(self.gui_manager, x, 0, width, 50)
        self.solver_drop_down = SolverDropDown(self.gui_manager, x, 50, width, 50)
        self.info_panel = InfoPanel(self.gui_manager, x, 100, width, height - 200, update_mode)
        self.save_load = SaveLoad(self.gui_manager, x, height-100, width, 100)

    def process_event(self, event):
        self.gui_manager.process_events(event)

    def update(self, time_delta, path_len):
        self.gui_manager.update(time_delta)
        if path_len:
            self.info_panel.update_path_text(path_len)

    def update_infobox_mode(self, text):
        self.info_panel.update_mode_text(text)

    def update_infobox_path(self, path_len):
        self.info_panel.update_path_text(path_len)

    def get_file_name(self):
        return self.save_load.fname_text_box.text

    def active_text_box(self) -> bool:
        return self.save_load.fname_text_box.is_focused

    def show(self, surface):
        pygame.draw.rect(surface, (50, 50, 50), self.rect)

        self.gui_manager.draw_ui(surface)