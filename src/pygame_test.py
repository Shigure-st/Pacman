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

def check_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    if x1 + w1 < x2:
        return False
    if x2 + w2 < x1:
        return False
    if y1 + h1 < y2:
        return False
    if y2 + h2 < y1:
        return False
    return True


def main():
    pygame.init()

    width, height = 400, 400
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pac-man (MLX Style)")

    clock = pygame.time.Clock()

    pacman_x = 200
    pacman_y = 200
    pacman_size = 20
    speed = 4

    target_x = 100
    target_y = 100
    target_size = 20

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            pacman_x -= speed
        if keys[pygame.K_RIGHT]:
            pacman_x += speed
        if keys[pygame.K_UP]:
            pacman_y -= speed
        if keys[pygame.K_DOWN]:
            pacman_y += speed

        screen.fill((0,0,0))

        draw_rect(screen, 50, 50, 200, 20, (0, 0, 255))
        draw_rect(screen, 50, 50, 20, 150, (0, 0, 255))
        draw_rect(screen, 50, 200, 200, 20, (0, 0, 255))
        draw_rect(screen, 230, 50, 20, 150, (0, 0, 255))
        is_hit = check_collision(
            pacman_x, pacman_y, pacman_size, pacman_size,
            target_x, target_y, target_size, target_size
        )
        if is_hit:
            pacman_color = (255, 255, 255)
        else:
            pacman_color = (255, 255, 0)

        draw_rect(screen, target_x, target_y, target_size, target_size, (255, 0, 0))
        # draw_rect(screen, 100, 100, 4, 4, (255, 255, 255))
        # draw_rect(screen, 130, 100, 4, 4, (255, 255, 255))
        # draw_rect(screen, 160, 100, 4, 4, (255, 255, 255))
        #
        # draw_rect(screen, 150, 150, 20, 20, (255, 255, 0))
        draw_rect(screen, pacman_x, pacman_y, pacman_size, pacman_size, pacman_color)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
