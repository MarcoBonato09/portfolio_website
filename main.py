import pygame
import asyncio


class PygameObject(pygame.sprite.Sprite):
    def __init__(self, surface_to_draw_on, path_to_asset, asset_size):
        self.master = surface_to_draw_on
        self.draw_flipped = False
        self.moving_right = False
        
        self.image = pygame.image.load(path_to_asset)
        self.image = pygame.transform.scale(self.image, asset_size)
        self.rect = self.image.get_rect()
        
        
    def set_coordinates(self, coordinates):
        self.rect.topleft = coordinates
        
        
    def draw(self):
        image = self.image
        if self.draw_flipped:
            image = pygame.transform.flip(image, flip_x=True, flip_y=False)
        self.master.blit(image, self.rect.topleft)


    def move(self, dx):
        self.rect.left += dx


class PygameVideo(pygame.sprite.Sprite):
    def __init__(self, surface_to_draw_on, path_to_frames, video_size):
        self.paused = False
        self.path = path_to_frames
        self.frame_size = video_size
        self.frame_index = 0
        self.master = surface_to_draw_on
        
        self.image = pygame.image.load(f"{self.path}/{self.frame_index}.png")
        self.image = pygame.transform.scale(self.image, self.frame_size)
        self.rect = self.image.get_rect()
   
   
    def set_coordinates(self, coordinates):
        self.rect.topleft = coordinates
         
        
    def get_next_frame(self):
        try:
            self.image = pygame.image.load(f"{self.path}/{self.frame_index}.png")
            self.image = pygame.transform.scale(self.image, self.frame_size)
        except FileNotFoundError: # End of video reached
            return
        self.frame_index += 1
    
    
    def draw(self): # Overrides the PygameObject's draw method
        if not self.paused:
            self.get_next_frame()
        self.master.blit(self.image, self.rect.topleft)
        
        
class Engine:
    def __init__(self):
        pygame.init()
        
        self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.window.get_size()
        self.clock = pygame.time.Clock()
        self.moved = False
        
        self.character = PygameObject(self.window, "./assets/pi_creature.png", (200, 200))
        self.character.set_coordinates((0, self.height-self.character.rect.height))
        
        self.scenes = [
            self.create_scene("./videos/intro"),
            self.create_scene("./videos/about_me"),
            self.create_scene("./videos/skills"),
            self.create_scene("./videos/ending")
        ]
        self.cur_scene = 0
             
        
    def create_scene(self, path_to_video_frames):
        scene = PygameVideo(self.window, path_to_video_frames, (self.height*16/9, self.height))
        scene.set_coordinates(((self.width-scene.rect.width)/2, 0))
        return scene
        
        
    async def main_loop(self):
        while True:
            self.check_events()
                
            self.window.fill("black")
            self.scenes[self.cur_scene].draw()
            self.character.draw()
                                
            pygame.display.update()
            await asyncio.sleep(0)
            self.clock.tick(60)

    
    def check_events(self):
        # Checks if the character is more than halfway across the screen
        if self.character.rect.left+self.character.rect.width//2 > self.width//2:
            self.character.draw_flipped = True
        else:
            self.character.draw_flipped = False
            
        if self.cur_scene == 0 and not self.moved and self.scenes[self.cur_scene].frame_index == 310:
            self.scenes[self.cur_scene].paused = True
        elif self.character.moving_right:
            self.character.move(5)
            if self.character.rect.left > self.width+self.character.rect.width//4:
                if self.cur_scene <= 2:
                    self.cur_scene += 1
                self.character.rect.left = 0
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN or event.type == pygame.KEYDOWN:
                if not self.moved:
                    self.moved = True
                    self.scenes[self.cur_scene].paused = False
                self.character.moving_right = True
            elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.FINGERUP or event.type == pygame.KEYUP:
                self.character.moving_right = False
   

app = Engine()
asyncio.run(app.main_loop())
