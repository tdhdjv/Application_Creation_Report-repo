import pygame
import sys
import time

from world import World

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption('physic engine')
        self.windowSize = (649, 480)
        self.tickPerSecond = 30
        self.subSteps = 10
        self.MAX_SUB_STEP = 10
        self.screen = pygame.display.set_mode(self.windowSize)

        self.clock = pygame.time.Clock()

        self.world = World(pygame.Vector2(self.windowSize))

    def run(self):
        while True:
            self.screen.fill((0,0,0))

            self.world.render(self.screen)
            previouseTime = time.time()
            self.world.step(self.tickPerSecond, self.subSteps)
            deltaTime = max(0.0001,(time.time()-previouseTime))
            self.subSteps = self.subSteps/(deltaTime*self.tickPerSecond)
            self.subSteps = int(min(max(1, self.subSteps), self.MAX_SUB_STEP))
            self.world.player_input(self.tickPerSecond)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
            self.clock.tick(self.tickPerSecond)
            
if __name__ == "__main__":
    Game().run()