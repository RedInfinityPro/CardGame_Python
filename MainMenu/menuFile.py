from Container.imports_library import *
from Container.imports_library import *


class BaseMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.settings = {
            'music_volume': 50,
            'sound_effects': 50,
            'frame_rate': 60,
            'brightness': 100
        }
    
    def create_settings_menu(self, parent_menu):
        settings_menu = pygame_menu.Menu('Settings', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        # Add sliders and store references
        settings_menu.add.range_slider('Music Volume', default=self.settings['music_volume'], range_values=(0, 100), increment=1, onchange=lambda value: self.update_setting('music_volume', value))
        settings_menu.add.range_slider('Sound Effects', default=self.settings['sound_effects'], range_values=(0, 100), increment=1,onchange=lambda value: self.update_setting('sound_effects', value))
        settings_menu.add.range_slider('Frame Rate', default=self.settings['frame_rate'], range_values=(30, 120), increment=1,onchange=lambda value: self.update_setting('frame_rate', value))
        settings_menu.add.range_slider('Brightness', default=self.settings['brightness'], range_values=(0, 100), increment=1,onchange=lambda value: self.update_setting('brightness', value))
        settings_menu.add.button('Return', pygame_menu.events.BACK)
        return settings_menu
    
    def update_setting(self, key, value):
        self.settings[key] = value
        print(f"Updated {key} to {value}")


class MainMenu(BaseMenu):
    def __init__(self, screen, width, height):
        super().__init__(screen, width, height)
        self.play = False
        self.selected_save_slot = None
        self.create_menus()
    
    def create_menus(self):
        # Main menu
        self.main_menu = pygame_menu.Menu('Welcome', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        # Add main menu buttons
        self.main_menu.add.button('Play Game', self.start_game)
        self.main_menu.add.button('Load Game', self.show_load_menu)
        self.main_menu.add.button('Settings', self.show_settings)
        self.main_menu.add.button('Quit', pygame_menu.events.EXIT)
        # Create sub-menus
        self.load_menu = self.create_load_menu()
        self.settings_menu = self.create_settings_menu(self.main_menu)
    
    def create_load_menu(self):
        load_menu = pygame_menu.Menu('Load Game', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        for i in range(1, 11):
            load_menu.add.button(f'Save Slot {i}', lambda slot=i: self.load_game(slot))
        load_menu.add.button('Return to Main Menu', pygame_menu.events.BACK)
        return load_menu
    
    def start_game(self):
        self.play = True
        print("Starting new game...")
    
    def load_game(self, slot_number):
        self.selected_save_slot = slot_number
        self.play = True
        print(f"Loading game from slot {slot_number}")
    
    def show_load_menu(self):
        self.main_menu._open(self.load_menu)
    
    def show_settings(self):
        self.main_menu._open(self.settings_menu)
    
    def get_main_menu(self):
        return self.main_menu


class PauseMenu(BaseMenu):
    def __init__(self, screen, width, height):
        super().__init__(screen, width, height)
        self.resume_game = False
        self.exit_to_main = False
        self.create_menus()
    
    def create_menus(self):
        # Pause menu
        self.pause_menu = pygame_menu.Menu('Game Paused', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        # Add pause menu buttons
        self.pause_menu.add.button('Resume Game', self.resume)
        self.pause_menu.add.button('Settings', self.show_settings)
        self.pause_menu.add.button('Save Game', self.save_game)
        self.pause_menu.add.button('Main Menu', self.return_to_main)
        # Create settings menu
        self.settings_menu = self.create_settings_menu(self.pause_menu)
    
    def resume(self):
        self.resume_game = True
        print("Resuming game...")
    
    def save_game(self):
        print("Game saved!")
    
    def return_to_main(self):
        self.exit_to_main = True
        self.resume_game = True
        print("Returning to main menu...")
    
    def show_settings(self):
        self.pause_menu._open(self.settings_menu)
    
    def get_pause_menu(self):
        return self.pause_menu
    
    def reset_flags(self):
        self.resume_game = False
        self.exit_to_main = False
        self.quit_game = False