from Container.imports_library import *
from MainMenu.menuFile import *
from MainMenu.pauseFile import *
from CardDeck.cardFile import *

def on_resize(screen, main_menu, pause_menu) -> None:
    window_size = screen.get_size()
    new_w, new_h = window_size[0], window_size[1]
    main_menu.main_menu.resize(new_w, new_h)
    main_menu.load_menu.resize(new_w, new_h)
    pause_menu.pause_menu.resize(new_w, new_h)
    
class Application:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("CardGame")
        self.screenWidth, self.screenHeight = 1280, 720
        self.clock = pygame.time.Clock()
        self.running = True
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight), pygame.RESIZABLE)
        self.background_surface = pygame.Surface((self.screenWidth, self.screenHeight)).convert()
        self.background_surface.fill(pygame.Color("black"))
        # menu
        self.main_menu = MainMenu(screen=self.screen, width=self.screenWidth, height=self.screenHeight)
        self.main_menu.get_main_menu()
        self.pause_menu = PauseMenu(screen=self.screen, width=self.screenWidth, height=self.screenHeight)
        self.pause_menu.get_pause_menu()
        # cards
        self.all_sprites = []
        self.card1 = Cards(position=(100, 100), scale=(100, 125), card_type='Standard', face_image="Assets\cardFront.png")
        self.card2 = Cards(position=(300, 100), scale=(100, 125), card_type='Bonus', face_image="Assets\cardFront.png")
        self.all_sprites.append(self.card1)
        self.all_sprites.append(self.card2)
        
    def run(self):
        while self.running:
            dt = self.clock.tick(64) / 100.0
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    self.screenWidth, self.screenHeight = event.w, event.h
                    self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight), pygame.RESIZABLE)
                    self.background_surface = pygame.transform.scale(self.background_surface, (self.screenWidth, self.screenHeight))
                    on_resize(screen=self.screen, main_menu=self.main_menu, pause_menu=self.pause_menu)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.main_menu.play:
                            self.pause_menu.resume_game = not(self.pause_menu.resume_game)
                # cards
                for cards in self.all_sprites:
                    cards.handle_event(event)
            # menu
            if not self.main_menu.play or self.pause_menu.exit_to_main:
                self.main_menu.play = False
                self.pause_menu.reset_flags()
                self.main_menu.main_menu.update(events)
                self.main_menu.main_menu.draw(self.screen)
            elif self.main_menu.play and not self.pause_menu.resume_game:
                self.pause_menu.pause_menu.update(events)
                self.pause_menu.pause_menu.draw(self.screen)
            else:
                self.screen.blit(self.background_surface, (0, 0))
                # self.all_sprites.update(dt)
                for cards in self.all_sprites:
                    cards.update(dt)
                    cards.draw(screen=self.screen)
                    
            self.clock.tick(64)
            pygame.display.flip()
            pygame.display.update()
        pygame.quit()
        sys.exit()
            
if __name__ == "__main__":
    app = Application()
    app.run()
