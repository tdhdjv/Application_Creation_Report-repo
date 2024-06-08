import pygame
import sys

from world import World

class Game:
    def __init__(self) -> None:
        pygame.init()

        pygame.display.set_caption('physic engine')
        self.windowSize = (649, 480)
        self.tickPerSecond = 60
        self.screen = pygame.display.set_mode(self.windowSize)

        self.clock = pygame.time.Clock()

        self.world = World(pygame.Vector2(self.windowSize))

    def run(self):
        while True:
            self.screen.fill((0,0,0))

            self.world.render(self.screen)
            self.world.step(self.tickPerSecond, 5)
            self.world.player_input(self.tickPerSecond)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
            self.clock.tick(self.tickPerSecond)
            
if __name__ == "__main__":
    Game().run()