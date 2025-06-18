from Container.imports_library import *

class BaseMenu:
    def __init__(self, screen: pygame.Surface, width: int, height: int):
        self.screen = screen
        self.width = width
        self.height = height
        self.settings = {
            'music_volume': 50,
            'sound_effects': 50,
            'frame_rate': 60,
            'brightness': 100
        }
    
    def create_settings_menu(self):
        settings_menu = pygame_menu.Menu('Settings', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        # Add sliders and store references
        settings_menu.add.range_slider('Music Volume', default=self.settings['music_volume'], range_values=(0, 100), increment=1, onchange=lambda value: self.update_setting('music_volume', value))
        settings_menu.add.range_slider('Sound Effects', default=self.settings['sound_effects'], range_values=(0, 100), increment=1,onchange=lambda value: self.update_setting('sound_effects', value))
        settings_menu.add.range_slider('Frame Rate', default=self.settings['frame_rate'], range_values=(30, 120), increment=1,onchange=lambda value: self.update_setting('frame_rate', value))
        settings_menu.add.range_slider('Brightness', default=self.settings['brightness'], range_values=(0, 100), increment=1,onchange=lambda value: self.update_setting('brightness', value))
        settings_menu.add.button('Return', pygame_menu.events.BACK)
        return settings_menu
    
    def update_setting(self, key: str, value: int):
        self.settings[key] = value
        print(f"Updated {key} to {value}")