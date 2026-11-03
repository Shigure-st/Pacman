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

def check_food_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    if x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1:
        return False
    return True

def check_wall_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    if x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1:
        return False
    return True


def main():
    # ★ 1. テキストで迷路マップをデザイン！
    # 1:壁, .:パックガム, P:パックマン, 空白:通路
    MAZE_MAP = [
        "11111111111111111111",
        "1........11........1",
        "1.111.11.11.11.111.1",
        "1.111.11.11.11.111.1",
        "1..................1",
        "1.111.111111.111.1.1",
        "1.....111111.....1.1",
        "11111.111111.11111.1",
        "11111.111111.11111.1",
        "11111.111111.11111.1",
        "1.........P........1",
        "1.111.111111.111.1.1",
        "1...1..........1...1",
        "111.1.11.11.11.1.111",
        "1........11........1",
        "11111111111111111111",
    ]

    TILE_SIZE = 20  # 1マスのピクセル数 (20x20)

    pygame.init()

    win_w = len(MAZE_MAP[0]) * TILE_SIZE
    win_h = len(MAZE_MAP) * TILE_SIZE
    screen = pygame.display.set_mode((win_w, win_h))
    pygame.display.set_caption("Pac-man (MLX Style)")

    clock = pygame.time.Clock()

    walls = []
    foods = []
    pacman_x = 0
    pacman_y = 0
    pacman_size = 16
    speed = 2

    for row, line in enumerate(MAZE_MAP):
        for col, char in enumerate(line):
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            if char == "1":
                walls.append((x, y, TILE_SIZE, TILE_SIZE))
            elif char == ".":
                foods.append((x + 7, y + 7))
            elif char == "P":
                pacman_x = x + 2
                pacman_y = y + 2

    food_size = 6
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT]:
            dx -= speed
        if keys[pygame.K_RIGHT]:
            dx += speed
        if keys[pygame.K_UP]:
            dy -= speed
        if keys[pygame.K_DOWN]:
            dy += speed

        # x方向の移動と衝突判定
        pacman_x += dx
        for wx, wy, ww, wh in walls:
            if check_wall_collision(pacman_x, pacman_y, pacman_size, pacman_size, wx, wy, ww, wh):
                pacman_x -= dx
                break
        # x方向の移動と衝突判定
        pacman_y += dy
        for wx, wy, ww, wh in walls:
            if check_wall_collision(pacman_x, pacman_y, pacman_size, pacman_size, wx, wy, ww, wh):
                pacman_y -= dy
                break

        # エサの判定を食べる処理
        remaining_foods = []
        for fx, fy in foods:
            if check_food_collision(pacman_x, pacman_y, pacman_size, pacman_size,
                               fx, fy, food_size, food_size):
                score += 10
                print(f"ワカワカ！　現在のスコア:{score}")
            else:
                remaining_foods.append((fx, fy))
        foods = remaining_foods

        # 画面クリア
        screen.fill((0,0,0))

        # 壁を描画
        for wx, wy, ww, wh in walls:
            draw_rect(screen, wx, wy, ww, wh, (0, 0, 255))

        for fx, fy in foods:
            draw_rect(screen, fx, fy, food_size, food_size, (255, 255, 255))

        draw_rect(screen, pacman_x, pacman_y, pacman_size, pacman_size, (255,255,0))
        pygame.display.flip()
        clock.tick(120)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
