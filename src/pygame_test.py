import pygame
import sys

def my_pixel_put(screen, x: int, y: int, color: tuple[int, int, int]):
    w, h = screen.get_size()
    if 0 <= x < w and 0 <= y < h:
        screen.set_at((x, y), color)

def main():
    pygame.init()

    width, height = 400, 400
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pac-man (MLX Style)")

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((0,0,0))

        my_pixel_put(screen, 200, 200, (255, 255, 255))

        my_pixel_put(screen, 0, 0, (255, 0, 0))
        my_pixel_put(screen, 204, 200, (0, 255, 0))
        my_pixel_put(screen, 206, 200, (0, 0, 255))
        my_pixel_put(screen, 208, 200, (255, 255, 0))

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
