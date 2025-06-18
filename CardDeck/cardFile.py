from Container.imports_library import *
from CardDeck.cardAssets import *

# card types
class CardType(Enum):
    STANDARD = "Standard" # Normal playing card
    BONUS = "Bonus" # Adds to card's attributes
    CURSED = "Cursed" # Removes attributes or disables cards
    
class CardRarity(Enum):
    COMMON = ("gray", (128, 128, 128), 0.5)      # 50% chance
    UNCOMMON = ("green", (0, 128, 0), 0.25)      # 25% chance
    RARE = ("blue", (0, 0, 255), 0.15)           # 15% chance
    EPIC = ("purple", (128, 0, 128), 0.08)       # 8% chance
    LEGENDARY = ("gold", (255, 215, 0), 0.02)    # 2% chance
    
    def __init__(self, name: str, color: Tuple[int, int, int], probability: float):
        self.display_name = name
        self.color = color
        self.probability = probability
      
@dataclass
class CardStats:
    attack: int = 100
    health: int = 100
    defense: int = 50
    level: int = 1
    xp: int = 0
    max_xp: int = 100
    special_ability: str = ""
    
    def __post_init__(self):
        self.max_xp = self.calculate_xp_requirement(self.level)
    
    def calculate_xp_requirement(self, level: int) -> int:
        return int(100 * (1.5 ** (level - 1)))
    
# generate stats
def generate_stats_for_rarity(rarity: CardRarity) -> CardStats:
    if rarity == CardRarity.COMMON:
        return CardStats(
            attack=random.randint(5, 50),
            health=random.randint(30, 80),
            defense=random.randint(5, 30),
            level=1,
        )
    elif rarity == CardRarity.UNCOMMON:
        return CardStats(
            attack=random.randint(30, 70),
            health=random.randint(60, 120),
            defense=random.randint(20, 50),
            level=1
        )
    elif rarity == CardRarity.RARE:
        return CardStats(
            attack=random.randint(60, 100),
            health=random.randint(100, 160),
            defense=random.randint(30, 60),
            level=1
        )
    elif rarity == CardRarity.EPIC:
        return CardStats(
            attack=random.randint(90, 140),
            health=random.randint(140, 200),
            defense=random.randint(50, 80),
            level=1
        )
    elif rarity == CardRarity.LEGENDARY:
        return CardStats(
            attack=random.randint(120, 250),
            health=random.randint(180, 300),
            defense=random.randint(70, 100),
            level=1
        )
    else:
        return CardStats()

# Defines how stats grow when a card levels up
class StatGrowthPattern:
    def __init__(self, rarity: CardRarity):
        self.rarity = rarity
        self._set_growth_rates()
    
    def _set_growth_rates(self):
        """Set growth rates based on rarity"""
        growth_multipliers = {
            CardRarity.COMMON: 1.0,
            CardRarity.UNCOMMON: 1.2,
            CardRarity.RARE: 1.5,
            CardRarity.EPIC: 1.8,
            CardRarity.LEGENDARY: 2.2
        }
        
        base_multiplier = int(growth_multipliers.get(self.rarity, 1.0))
        # Growth per level (with some randomization)
        self.attack_growth = random.randint(3, 8) * base_multiplier
        self.health_growth = random.randint(5, 12) * base_multiplier
        self.defense_growth = random.randint(2, 6) * base_multiplier
        # Special ability unlock levels
        self.ability_unlock_levels = []
        if self.rarity in [CardRarity.RARE, CardRarity.EPIC, CardRarity.LEGENDARY]:
            self.ability_unlock_levels = [5, 10, 15, 20]
    
    def get_level_up_bonuses(self, current_level: int) -> dict:
        # Add some level-based scaling
        level_multiplier = 1 + (current_level * 0.1)
        return {
            'attack': int(self.attack_growth * level_multiplier),
            'health': int(self.health_growth * level_multiplier),
            'defense': int(self.defense_growth * level_multiplier)
        }
    
    def has_ability_unlock(self, level: int) -> bool:
        return level in self.ability_unlock_levels
    
    def get_ability_for_level(self, level: int) -> str:
        abilities = {
            5: "Minor Boost: +10% to all stats",
            10: "Shield: Reduce incoming damage by 20%",
            15: "Regeneration: Restore 5% health each turn",
            20: "Critical Strike: 25% chance for double damage"
        }
        return abilities.get(level, "")

class CardAnimator:
    def __init__(self):
        self.is_animating = False
        self.animation_type = None
        self.animation_progress = 0.0
        self.animation_duration = 1.0
    
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
    
    def update_animation(self, dt: float):
        """Update animation progress"""
        if self.is_animating:
            self.animation_progress += dt / self.animation_duration
            if self.animation_progress >= 1.0:
                self.animation_progress = 1.0
                self.is_animating = False
    
    def get_animation_offset(self) -> Tuple[float, float]:
        """Get current animation offset"""
        if not self.is_animating:
            return 0.0, 0.0
        if self.animation_type == "hover":
            # Smooth hover animation
            hover_height = math.sin(self.animation_progress * math.pi * 2) * 10
            return 0.0, hover_height
        return 0.0, 0.0
    
class Cards(pygame.sprite.Sprite):
    def __init__(self, position: Tuple[int, int], scale: Tuple[int, int], card_type: CardType, face_image: Optional[str] = None, stats: Optional[CardStats] = None, name: str = "Unknown Card"):
        super().__init__()
        self.x, self.y = position
        self.width, self.height = scale
        self.original_position = position
        # Card properties
        self.card_type = card_type
        self.name = name
        self.rarity = self._determine_rarity()
        self.stats = stats or generate_stats_for_rarity(self.rarity)
        self.growth_pattern = StatGrowthPattern(self.rarity)
        self.base_stats = CardStats(
            attack=self.stats.attack,
            health=self.stats.health,
            defense=self.stats.defense,
            level=1,
            xp=0
        )
        # Visual properties
        self.border_thickness = 8
        self.border_color = self.rarity.color
        self.is_selected = False
        self.is_hovered = False
        # level
        self.xp_gain_rate = 1.0
        self.level_color_timer = 0
        self.level_color_duration = 10
        self.level_original_color = pygame.Color('black')
        self.level_up_color = pygame.Color('orange')
        self.level_color = self.level_original_color
        # Animation system
        self.animator = CardAnimator()
        self.angle = 0
        self.target_angle = 0
        self.rotation_speed = 3.0
        # Movement
        self.target_x, self.target_y = position
        self.move_speed = 8.0
        self.smooth_movement = True
        # image
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, self.border_color, self.image.get_rect(), self.border_thickness)
        if face_image:
            try:
                face = pygame.image.load(face_image).convert_alpha()
                face = pygame.transform.scale(face, (self.width - self.border_thickness * 2, self.height - self.border_thickness * 2))
            except pygame.error:
                face = self._create_placeholder_image()
        else:
            face = self._create_placeholder_image()
        self.face_image = face
        face = pygame.transform.scale(face, (self.width - self.border_thickness * 2, self.height - self.border_thickness * 2))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def _determine_rarity(self):
        rand = random.random()
        cumulative_prob = 0.0
        sorted_rarities = sorted(CardRarity, key=lambda r: r.probability, reverse=True)
        for rarity in sorted_rarities:
            cumulative_prob += rarity.probability
            if rand < cumulative_prob:
                return rarity
        return CardRarity.COMMON
    
    def _create_placeholder_image(self) -> pygame.Surface:
        surface = pygame.Surface((self.width/1.15, self.height/1.15))
        surface.fill(pygame.Color('white'))
        pygame.draw.rect(surface, pygame.Color('brown'), (5, 5, self.width-24, self.height-24), 2)
        return surface
           
    def draw(self, screen: pygame.Surface):
        card_canvas = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        card_canvas.fill((0, 0, 0, 0))
        # Draw border
        pygame.draw.rect(card_canvas, self.border_color, card_canvas.get_rect(), self.border_thickness)
        # Draw face image centered inside inner area
        if self.face_image:
            inner_width = self.width - self.border_thickness * 2
            inner_height = self.height - self.border_thickness * 2
            scaled_face = pygame.transform.scale(self.face_image, (inner_width, inner_height))
            face_rect = scaled_face.get_rect(center=(self.width // 2, self.height // 2))
            card_canvas.blit(scaled_face, face_rect)
        # Draw icons
        self.load_icons = IconRenderer(font_size=[12, 12, 12])
        self.load_icons.draw_icon(icon_unicode='\uf004', icon_color=pygame.Color("red"), position=(15, 15), surface=card_canvas, value=self.stats.health)
        self.load_icons.draw_icon(icon_unicode='\uf6e3', icon_color=pygame.Color("blue"), position=(15, self.height - 40), surface=card_canvas, value=self.stats.attack)
        self.load_icons.draw_icon(icon_unicode='\uf132', icon_color=pygame.Color("green"), position=(self.width - 30, self.height - 40), surface=card_canvas, value=self.stats.defense)
        self.load_icons.draw_icon(icon_unicode='\uf062', icon_color=self.level_color, position=(self.width - 30, 15), surface=card_canvas, value=self.stats.level)
        # Rotate entire card
        self.rotated = pygame.transform.rotate(card_canvas, self.angle)
        self.rect = self.rotated.get_rect(center=(self.x, self.y))
        screen.blit(self.rotated, self.rect)
        
    
    def gain_xp(self, amount: int):
        self.stats.xp += amount
        if self.level_color_timer == 0 and self.stats.level < 999:
            if self.stats.xp >= self.stats.max_xp:
                self.level_up()
    
    def level_up(self):
        if self.stats.xp >= self.stats.max_xp:
            excess_xp = self.stats.xp - self.stats.max_xp
            self.stats.level += 1
            # Get stat bonuses
            bonuses = self.growth_pattern.get_level_up_bonuses(self.stats.level)
            # Apply stat increases
            self.stats.attack += bonuses['attack']
            self.stats.health += bonuses['health']
            self.stats.defense += bonuses['defense']
            # Update XP requirements
            self.stats.max_xp = self.stats.calculate_xp_requirement(self.stats.level)
            self.stats.xp = excess_xp  # Carry over excess XP
            # Check for special ability unlock
            if self.growth_pattern.has_ability_unlock(self.stats.level):
                new_ability = self.growth_pattern.get_ability_for_level(self.stats.level)
                self.stats.special_ability = new_ability
            # Visual effects
            self.level_color = self.level_up_color
            # Continue leveling if enough XP
            if self.stats.xp >= self.stats.max_xp:
                self.level_up()  # Recursive level up
        else:
            self.level_color = self.level_original_color
    
    def update(self, dt: float):
        self.animator.update_animation(dt)
        # Smooth movement towards target
        if self.smooth_movement:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            if abs(dx) > 1 or abs(dy) > 1:
                self.x += dx * self.move_speed * dt
                self.y += dy * self.move_speed * dt
        # Smooth rotation
        angle_diff = self.target_angle - self.angle
        if abs(angle_diff) > 1:
            self.angle += angle_diff * self.rotation_speed * dt
        # Update rect position with animation offset
        anim_x, anim_y = self.animator.get_animation_offset()
        self.x += anim_x
        self.y += anim_y
        
        # level up
        if self.level_color == self.level_up_color:
            self.level_color_timer += 1
            if self.level_color_timer >= self.level_color_duration:
                self.level_color = self.level_original_color
                self.level_color_timer = 0
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.animator.start_hover_animation()
            #print(self.rect)