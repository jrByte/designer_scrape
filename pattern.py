import pygame


class window:
    def __init__(self, window_size, background_color, running):
        self.window_size = window_size
        self.background_color = background_color
        self.running = running

    def window(self):
        screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption('DEMO')
        screen.fill(self.background_color)
        pygame.display.flip()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

    def square(self):
        pygame.draw.rect()


class shapes(window):
    def __init__(self, window_size, background_color, running=True):
        super().__init__(window_size, background_color, running)


if __name__ == "__main__":
    demo = shapes(window_size=(500, 500), background_color=(255, 255, 255))
    demo.window()
