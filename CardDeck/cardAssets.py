from Container.imports_library import *
pygame.init()

LINK = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-solid-900.ttf"
def download_font_awesome():
    """Download Font Awesome font file"""
    response = requests.get(LINK)
    return io.BytesIO(response.content)

class IconRenderer:
    def __init__(self, font_size: Tuple[int, int, int]):
        self.size = font_size
        try:
            self.font_data = download_font_awesome()
            self.icon_font = pygame.font.Font(self.font_data, self.size[0])
        except:
            self.icon_font = pygame.font.SysFont('arial', self.size[0])
        self.small_font = pygame.font.SysFont('arial', self.size[1])
        self.text_font = pygame.font.SysFont('arial', self.size[2])
        
    def draw_Icon_and_Number(self, icon_unicode: str, icon_color: pygame.Color, surface: pygame.Surface, position: Tuple[int, int], value: int):
        icon_surface = self.icon_font.render(icon_unicode, True, icon_color)
        value_position = (position[0], position[1] + self.size[0])
        value_surface = self.small_font.render('{number}'.format(number=value), True, icon_color)
        
        surface.blit(icon_surface, position)
        surface.blit(value_surface, value_position)
        return icon_surface.get_rect(center=position)
    
    def draw_icon(self, icon_unicode: str, icon_color: pygame.Color, surface: pygame.Surface, position: Tuple[int, int]):
        icon_surface = self.icon_font.render(icon_unicode, True, icon_color)
        surface.blit(icon_surface, position)
        return icon_surface.get_rect(center=position)
    
    def draw_words(self, string_color: pygame.Color, surface: pygame.Surface, position: Tuple[int, int], string: str):
        string_position = position
        string_surface = self.small_font.render('{number}'.format(number=string), True, string_color)
        surface.blit(string_surface, string_position)