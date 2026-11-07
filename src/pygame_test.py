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

def get_ghost_next_dir(gx, gy, g_size, current_dir, walls ,pacman_x, pacman_y, speed):
    TILE_SIZE = 20  # 1マスのピクセル数 (20x20)
    directions = [
        (0, -speed),
        (0, speed),
        (-speed, 0),
        (speed, 0),
    ]

    # 今の向きと真逆(Uターン)の方向
    cur_dx, cur_dy = current_dir
    reverse_dir = (-cur_dx, -cur_dy)

    possible_dirs = []
    for dx, dy in directions:
        # Uターンは原則禁止
        if (dx, dy) == reverse_dir and (cur_dx != 0 or cur_dy != 0):
            continue

        # 1マス先が壁じゃないなら候補に入れる
        step_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
        step_y = 1 if dy > 0 else (-1 if dy < 0 else 0)
        check_x = gx + step_x * TILE_SIZE
        check_y = gy + step_y * TILE_SIZE

        if not is_wall_at(check_x, check_y, g_size, walls):
            possible_dirs.append((dx, dy))
    if not possible_dirs:
        possible_dirs.append(reverse_dir)
    best_dir = possible_dirs[0]
    min_dist = float('inf')
    for dx, dy in possible_dirs:
        next_x = gx + dx
        next_y = gy + dy
        dist = (next_x - pacman_x) ** 2 + (next_y - pacman_y) ** 2
        if dist < min_dist:
            min_dist = dist
            best_dir = (dx, dy)
    return best_dir

# 指定した座標(next_t, next_y)に動いた時、壁にぶつかるかを調べる関数
def is_wall_at(next_x, next_y, size, walls) -> bool:
    for wx, wy, ww, wh in walls:
        if check_wall_collision(next_x, next_y, size, size, wx, wy, ww, wh):
            return True
    return False


def main():
    # ★ 1. テキストで迷路マップをデザイン！
    # 1:壁, .:パックガム, P:パックマン, 空白:通路
    MAZE_MAP = [
        "11111111111111111111",
        "1G.......11........1",
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
    pacman_size = 14
    speed = 2

    ghost_x = 0
    ghost_y = 0
    ghost_size = 14

    OFFSET = (TILE_SIZE - pacman_size) // 2

    for row, line in enumerate(MAZE_MAP):
        for col, char in enumerate(line):
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            if char == "1":
                walls.append((x, y, TILE_SIZE, TILE_SIZE))
            elif char == ".":
                foods.append((x + 7, y + 7))
            elif char == "P":
                pacman_x = x + OFFSET
                pacman_y = y + OFFSET
            elif char == "G":
                ghost_x = x + OFFSET
                ghost_y = y + OFFSET

    dir_x = 0
    dir_y = 0
    next_dir_x = 0
    next_dir_y = 0

    ghost_dir_x = -speed
    ghost_dir_y = 0

    food_size = 6
    score = 0
    game_over = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # キーを押した瞬間、次の方向を「予約」する
                elif event.key == pygame.K_LEFT:
                    next_dir_x, next_dir_y = -speed, 0
                elif event.key == pygame.K_RIGHT:
                    next_dir_x, next_dir_y = speed, 0
                elif event.key == pygame.K_UP:
                    next_dir_x, next_dir_y = 0, -speed
                elif event.key == pygame.K_DOWN:
                    next_dir_x, next_dir_y = 0, speed

        if not game_over:
            if (next_dir_x != 0 or next_dir_y != 0):
                target_x = round((pacman_x - OFFSET) / TILE_SIZE) * TILE_SIZE + OFFSET if next_dir_y != 0 else pacman_x
                target_y = round((pacman_y - OFFSET) / TILE_SIZE) * TILE_SIZE + OFFSET if next_dir_x != 0 else pacman_y

                step_x = (next_dir_x > 0) - (next_dir_x < 0)
                step_y = (next_dir_y > 0) - (next_dir_y < 0)

                check_x = target_x + step_x * TILE_SIZE
                check_y = target_y + step_y * TILE_SIZE

                # if not is_wall_at(target_x + next_dir_x, target_y + next_dir_y, pacman_size, walls):
                if not is_wall_at(check_x, check_y, pacman_size, walls):
                    pacman_x = target_x
                    pacman_y = target_y
                    dir_x = next_dir_x
                    dir_y = next_dir_y
            if not is_wall_at(pacman_x + dir_x, pacman_y + dir_y, pacman_size, walls):
                pacman_x += dir_x
                pacman_y += dir_y

            is_at_center_x = (ghost_x - OFFSET) % TILE_SIZE == 0
            is_at_center_y = (ghost_y - OFFSET) % TILE_SIZE == 0
            if is_at_center_x and is_at_center_y:
                ghost_dir_x, ghost_dir_y = get_ghost_next_dir(
                    ghost_x, ghost_y, pacman_size,
                    (ghost_dir_x, ghost_dir_y),
                    walls, pacman_x, pacman_y, speed
                )

            ghost_x += ghost_dir_x
            ghost_y += ghost_dir_y



        # keys = pygame.key.get_pressed()
        # dx = 0
        # dy = 0
        # if keys[pygame.K_LEFT]:
        #     dx -= speed
        # if keys[pygame.K_RIGHT]:
        #     dx += speed
        # if keys[pygame.K_UP]:
        #     dy -= speed
        # if keys[pygame.K_DOWN]:
        #     dy += speed

        # # x方向の移動と衝突判定
        # pacman_x += dx
        # for wx, wy, ww, wh in walls:
        #     if check_wall_collision(pacman_x, pacman_y, pacman_size, pacman_size, wx, wy, ww, wh):
        #         pacman_x -= dx
        #         break
        # # x方向の移動と衝突判定
        # pacman_y += dy
        # for wx, wy, ww, wh in walls:
        #     if check_wall_collision(pacman_x, pacman_y, pacman_size, pacman_size, wx, wy, ww, wh):
        #         pacman_y -= dy
        #         break

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

        # ゴーストとパックマンの衝突
        if check_food_collision(pacman_x, pacman_y, pacman_size, pacman_size, ghost_x, ghost_y, pacman_size, pacman_size):
            game_over = True
            print("ゲームオーバー！ゴーストに捕まりました")
            # running = False

        # 画面クリア
        screen.fill((0,0,0))

        # 壁を描画
        for wx, wy, ww, wh in walls:
            draw_rect(screen, wx, wy, ww, wh, (0, 0, 255))

        for fx, fy in foods:
            draw_rect(screen, fx, fy, food_size, food_size, (255, 255, 255))

        p_color = (100, 100, 100) if game_over else (255, 255, 0)
        draw_rect(screen, pacman_x, pacman_y, pacman_size, pacman_size, p_color)

        draw_rect(screen, ghost_x, ghost_y, pacman_size, pacman_size, (255, 0, 0))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
