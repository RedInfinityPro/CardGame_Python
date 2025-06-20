from Container.imports_library import *
from CardDeck.cardAssets import *

class CardRarity(Enum):
    COMMON = ("gray", (128, 128, 128), 1.0)
    UNCOMMON = ("green", (0, 128, 0), 1 / 11)
    RARE = ("blue", (0, 0, 255), 1 / 121)
    EPIC = ("purple", (128, 0, 128), 1 / 1331)
    LEGENDARY = ("gold", (255, 215, 0), 1 / 14641)

    def __init__(self, name: str, color: Tuple[int, int, int], weight: float):
        self.display_name = name
        self.color = color
        self.weight = weight

class CardAnimator:
    def __init__(self):
        self.is_animating = False
        self.animation_type = None
        self.animation_progress = 0.0
        self.animation_duration = 1.0
        self.hover_phase = 0.0
    
    def start_flip_animation(self):
        """Start card flip animation"""
        self.is_animating = True
        self.animation_type = "flip"
        self.animation_progress = 0.0
    
    def start_hover_animation(self):
        """Start card hover animation"""
        self.is_animating = True
        self.animation_type = "hover"
        self.animation_progress = 0.0
        self.hover_phase = 0.0
    
    def update_animation(self, dt: float):
        """Update animation progress"""
        if self.is_animating:
            if self.animation_type == "hover":
                self.hover_phase += dt * 4.0  # Continuous hover animation
            else:
                self.animation_progress += dt / self.animation_duration
                if self.animation_progress >= 1.0:
                    self.animation_progress = 1.0
                    self.is_animating = False
    
    def get_animation_offset(self) -> Tuple[float, float]:
        """Get current animation offset"""
        if not self.is_animating:
            return 0.0, 0.0
        if self.animation_type == "hover":
            # Smooth hover animation using sine wave
            hover_height = math.sin(self.hover_phase) * 5
            return 0.0, hover_height
        return 0.0, 0.0

# Cache for colorized images to avoid repeated colorization
_colorize_cache = {}
def colorize(image, newColor):
    # Create cache key
    cache_key = (id(image), newColor)
    if cache_key in _colorize_cache:
        return _colorize_cache[cache_key]
    colorized = image.copy()
    colorized.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    colorized.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
    # Cache the result
    _colorize_cache[cache_key] = colorized
    return colorized

# card types        
class Standard_Cards(pygame.sprite.Sprite):
    level: int = 1
    attack: int = 0
    health: int = 0
    defense: int = 0
    is_asleep: float = False
    
    icon_renderer = IconRenderer(font_size=[12, 12, 12])
    level_original_color = pygame.Color('black')
    level_up_color = pygame.Color('orange')
    level_color = level_original_color
    
    def __init__(self):
        super().__init__()
        pass
    
    def generate_stats_for_rarity(self, rarity: CardRarity):
        stat_ranges = {
            CardRarity.COMMON: ((5, 50), (30, 80), (5, 30), 1),
            CardRarity.UNCOMMON: ((30, 70), (60, 120), (20, 50), 1),
            CardRarity.RARE: ((60, 100), (100, 160), (30, 60), 1),
            CardRarity.EPIC: ((90, 140), (140, 200), (50, 80), 1),
            CardRarity.LEGENDARY: ((120, 250), (180, 300), (70, 100), 1)
        }
        attack_range, health_range, defense_range, level = stat_ranges.get(rarity, ((5, 50), (30, 80), (5, 30), 1))
        self.attack=random.randint(attack_range[0], attack_range[1])
        self.health=random.randint(health_range[0], health_range[1])
        self.defense=random.randint(defense_range[0], defense_range[1])
        self.level=level
        return self.attack, self.health, self.defense, self.level
    
    def Dye_Color(self, face_image, card_canvas):
        if face_image:
            face_rect = self.face_image.get_rect(center=(self.width // 2, self.height // 2))
            card_canvas.blit(self.face_image, face_rect)
            # Apply color overlay to dye the card area (not replace the image)
            dye_color = self.darken_color(self.border_color)
            overlay = pygame.Surface((self.face_image.get_width(), self.face_image.get_height()), pygame.SRCALPHA)
            overlay.fill((*dye_color, 80))  # Semi-transparent overlay (80/255 alpha)
            card_canvas.blit(overlay, face_rect, special_flags=pygame.BLEND_MULT)
        return card_canvas
    
    def darken_color(self, color):
        return tuple(int(c * 0.6) for c in color[:3])
    
    def Add_Icons(self, card_canvas, scale):
        self.width, self.height = scale
        self.icon_renderer.draw_Icon_and_Number(icon_unicode='\uf004', icon_color=pygame.Color("red"), position=(15, 15), surface=card_canvas, value=self.health)
        self.icon_renderer.draw_Icon_and_Number(icon_unicode='\uf6e3', icon_color=pygame.Color("blue"), position=(15, self.height - 40), surface=card_canvas, value=self.attack)
        self.icon_renderer.draw_Icon_and_Number(icon_unicode='\uf132', icon_color=pygame.Color("green"), position=(self.width - 30, self.height - 40), surface=card_canvas, value=self.defense)
        self.icon_renderer.draw_Icon_and_Number(icon_unicode='\uf062', icon_color=self.level_color, position=(self.width - 30, 15), surface=card_canvas, value=self.level)
    
class Cards(Standard_Cards):
    _placeholder_cache = {}
    xp: int = 0
    max_xp: int = 100
    _needs_redraw: float = False
    _cached_card_surface = None
    
    def __init__(self, position: Tuple[int, int], scale: Tuple[int, int], card_type: Optional[str] = None, face_image: Optional[str] = None):
        self.x, self.y = position
        self.width, self.height = scale
        self.original_position = position
        # Card properties
        self.card_type = card_type or random.choice(["Standard", "Bonus", "Cursed"])
        self.rarity = self._determine_rarity()
        self.max_xp = self.calculate_xp_requirement(self.level)
        self.generate_stats_for_rarity(rarity=self.rarity)
        # Visual properties
        self.border_thickness = 8
        self.border_color = self.rarity.color
        self.is_selected = False
        self.is_hovered = False
        # Animation system
        self.animator = CardAnimator()
        self.angle = 0.0
        self.target_angle = 0.0
        self.rotation_speed = 5.0
        # Movement with easing
        self.target_x, self.target_y = position
        self.move_speed = 10.0  # Increased for smoother movement
        self.smooth_movement = True
        # Initialize images and cache them
        self._init_images(face_image)
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
    
    def calculate_xp_requirement(self, level: int) -> int:
        return int(100 * (1.5 ** (level - 1)))
    
    def _determine_rarity(self):
        rarities = list(CardRarity)
        weights = [r.weight for r in rarities]
        total_weight = sum(weights)
        rand_val = random.uniform(0, total_weight)
        cumulative = 0.0
        for rarity, weight in zip(rarities, weights):
            cumulative += weight
            if rand_val < cumulative:
                return rarity
        return CardRarity.COMMON  # fallback
    
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
            if self.card_type == "Standard":
                self.Dye_Color(face_image=self.face_image, card_canvas=card_canvas)
                self.Add_Icons(card_canvas=card_canvas, scale=(self.width, self.height))
            else:
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
    
    def update(self, dt: float):
        moved = False
        # Smooth movement with easing
        if self.smooth_movement:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0.5:  # Only move if significant distance
                # Easing function for smoother movement
                move_factor = min(1.0, self.move_speed * dt)
                self.x += dx * move_factor
                self.y += dy * move_factor
                moved = True
        # Smooth rotation with easing
        angle_diff = self.target_angle - self.angle
        if abs(angle_diff) > 0.1:
            self.angle += angle_diff * self.rotation_speed * dt
            moved = True
        # Update animation
        self.animator.update_animation(dt)
        anim_x, anim_y = self.animator.get_animation_offset()
        if abs(anim_x) > 0.1 or abs(anim_y) > 0.1:
            self.x += anim_x * dt
            self.y += anim_y * dt
            moved = True
        # Mark for redraw if position changed significantly
        if moved:
            self._needs_redraw = True
            
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_over_card = self.rect.collidepoint(mouse_pos)
        # Handle mouse hover
        if mouse_over_card != self.is_hovered:
            self.is_hovered = mouse_over_card
            if self.is_hovered:
                self.animator.start_hover_animation()
            else:
                self.animator.is_animating = False
        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                was_selected = self.is_selected
                self.is_selected = mouse_over_card
                # Only update position if newly selected
                if self.is_selected and not was_selected:
                    self.target_x, self.target_y = mouse_pos
        # Handle dragging for selected cards
        elif event.type == pygame.MOUSEMOTION and self.is_selected:
            self.target_x, self.target_y = mouse_pos
        else:
            self.is_selected = False
            self.x, self.y = self.target_x, self.target_y
    
    def set_position(self, x: int, y: int, smooth: bool = True):
        if smooth:
            self.target_x, self.target_y = x, y
        else:
            self.x = self.target_x = x
            self.y = self.target_y = y
    
    def set_rotation(self, angle: float, smooth: bool = True):
        if smooth:
            self.target_angle = angle
        else:
            self.angle = self.target_angle = angle