from Container.imports_library import *

class CardRarity(Enum):
    COMMON = ("gray", (128, 128, 128), 0.909)    # 90.9% chance
    UNCOMMON = ("green", (0, 128, 0), 0.083)     # 8.3% chance
    RARE = ("blue", (0, 0, 255), 0.008)          # 0.8% chance
    EPIC = ("purple", (128, 0, 128), 0.0007)     # 0.07% chance
    LEGENDARY = ("gold", (255, 215, 0), 0.0006)  # 0.006% chance
    
    def __init__(self, name: str, color: Tuple[int, int, int], probability: float):
        self.display_name = name
        self.color = color
        self.probability = probability

# card types        
class Standard_Cards(pygame.sprite.Sprite):
    attack: int = 0
    health: int = 0
    defense: int = 0
    is_asleep: float = False
    
    _needs_redraw: float = False
    _cached_card_surface = None
    
    def __init__(self):
        super().__init__()
        pass
    
class Cards(Standard_Cards):
    _placeholder_cache = {}
    level: int = 1
    xp: int = 0
    max_xp: int = 100
    
    def __init__(self, position: Tuple[int, int], scale: Tuple[int, int], card_type: Optional[str] = None, face_image: Optional[str] = None):
        self.x, self.y = position
        self.width, self.height = scale
        self.original_position = position
        # Card properties
        self.card_type = card_type
        self.rarity = self._determine_rarity()
        # Visual properties
        self.border_thickness = 8
        self.border_color = self.rarity.color
        self.is_selected = False
        self.is_hovered = False
        # Animation system
        self.angle = 0.0
        # Initialize images and cache them
        self._init_images(face_image)
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
        
    def _determine_rarity(self):
        rand = random.random()
        cumulative_prob = 0.0
        # Check in order of probability (most common first)
        for rarity in [CardRarity.COMMON, CardRarity.UNCOMMON, CardRarity.RARE, CardRarity.EPIC, CardRarity.LEGENDARY]:
            cumulative_prob += rarity.probability
            if rand < cumulative_prob:
                return rarity
        return CardRarity.COMMON
    
    def _init_images(self, face_image):
        # Load or create face image
        if face_image:
            try:
                face = pygame.image.load(face_image).convert_alpha()
                face = pygame.transform.scale(face, (self.width - self.border_thickness * 2, self.height - self.border_thickness * 2))
            except pygame.error:
                face = self._get_placeholder_image()
        else:
            face = self._get_placeholder_image()
        self.face_image = face.convert_alpha()
    
    def _get_placeholder_image(self) -> pygame.Surface:
        cache_key = (self.width, self.height)
        if cache_key not in Cards._placeholder_cache:
            surface = pygame.Surface((self.width - self.border_thickness * 2, self.height - self.border_thickness * 2))
            surface.fill(pygame.Color('white'))
            pygame.draw.rect(surface, pygame.Color('brown'), (5, 5, self.width-24, self.height-24), 2)
            Cards._placeholder_cache[cache_key] = surface
        return Cards._placeholder_cache[cache_key]
    
    def _create_card_surface(self) -> pygame.Surface:
        card_canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Draw border
        pygame.draw.rect(card_canvas, self.border_color, card_canvas.get_rect(), self.border_thickness)
        # Draw face image with color overlay for card dyeing effect
        if self.face_image:
            face_rect = self.face_image.get_rect(center=(self.width // 2, self.height // 2))
            card_canvas.blit(self.face_image, face_rect)
        return card_canvas
    
    def draw(self, screen: pygame.Surface):
        # Only recreate surface if something changed
        if self._needs_redraw or self._cached_card_surface is None:
            self._cached_card_surface = self._create_card_surface()
            self._needs_redraw = False
        # Apply rotation if needed
        if abs(self.angle) > 0.1:
            rotated_surface = pygame.transform.rotate(self._cached_card_surface, self.angle)
            draw_rect = rotated_surface.get_rect(center=(int(self.x), int(self.y)))
        else:
            rotated_surface = self._cached_card_surface
            draw_rect = rotated_surface.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_surface, draw_rect)
        # Update collision rect
        self.rect.center = (int(self.x), int(self.y))
        
pygame.init()
clock = pygame.time.Clock()
screenWidth, screenHeight = 600, 600
screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)
card = Cards(position=(100, 100), scale=(100 ,125), face_image="Assets\cardFront.png")

running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
    
    screen.fill(pygame.Color('white'))
    card.draw(screen=screen)
    clock.tick(64)
    pygame.display.flip()
    pygame.display.update()