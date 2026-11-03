import pygame
import sys

def my_pixel_put(screen, x: int, y: int, color: tuple[int, int, int]):
    w, h = screen.get_size()
    if 0 <= x < w and 0 <= y < h:
        screen.set_at((x, y), color)

def draw_rect(screen, x: int, y: int, w: int, h: int, color: tuple[int, int, int]):
    for dy in range(h):
        for dx in range(w):
            my_pixel_put(screen, x + dx, y + dy, color)

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

        draw_rect(screen, 50, 50, 200, 20, (0, 0, 255))
        draw_rect(screen, 50, 50, 20, 150, (0, 0, 255))
        draw_rect(screen, 50, 200, 200, 20, (0, 0, 255))
        draw_rect(screen, 230, 50, 20, 150, (0, 0, 255))

        draw_rect(screen, 100, 100, 4, 4, (255, 255, 255))
        draw_rect(screen, 130, 100, 4, 4, (255, 255, 255))
        draw_rect(screen, 160, 100, 4, 4, (255, 255, 255))

        draw_rect(screen, 150, 150, 20, 20, (255, 255, 0))

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
