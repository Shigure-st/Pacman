import pygame
import sys
import math

def my_pixel_put(screen, x: int, y: int, color: tuple[int, int, int]):
    w, h = screen.get_size()
    if 0 <= x < w and 0 <= y < h:
        screen.set_at((x, y), color)

def draw_rect(screen, x: int, y: int, w: int, h: int, color: tuple[int, int, int]):
    for dy in range(h):
        for dx in range(w):
            my_pixel_put(screen, x + dx, y + dy, color)

def draw_circle(screen, cx, cy, radius, color):
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx * dx + dy * dy <= radius * radius:
                my_pixel_put(screen, cx + dx, cy + dy, color)

#2点間に線を引く自作関数(ブレゼンハムのアルゴリズム的な線描画)
def draw_line(screen, x0, y0, x1, y1, color):
    dx = x1 - x0
    dy = y1 - y0
    steps = int(max(abs(dx), abs(dy)))
    if steps == 0:
        my_pixel_put(screen, int(x0), int(y0), color)
        return
    x_inc = dx / steps
    y_inc = dy / steps
    x = x0
    y = y0
    for _ in range(steps):
        my_pixel_put(screen, int(x), int(y), color)
        x += x_inc
        y += y_inc

# 指定した座標が「壁の中」かどうかを調べる関数
def is_wall(x, y):
    col = int(x // TILE_SIZE)
    row = int(y // TILE_SIZE)
    # マップの範囲外は壁とみなす
    if col < 0 or col >= len(MAZE_MAP[0]) or row < 0 or row >= len(MAZE_MAP):
        return True
    return MAZE_MAP[row][col] == "1"

# プレイヤーから角度 angle に光線を飛ばし、壁にぶつかった座標と距離を返す関数
def cast_single_ray(ox, oy, angle):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    ray_x = ox
    ray_y = oy

    # 1ピクセルずつ最大400歩進めて壁を探す
    for depth in range(400):
        ray_x += cos_a
        ray_y += sin_a
        if is_wall(ray_x, ray_y):
            return ray_x, ray_y, depth # ぶつかった座標と壁までの距離

    return ray_x, ray_y, 400



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

def main():
    pygame.init()
    win_w = len(MAZE_MAP[0]) * TILE_SIZE
    win_h = len(MAZE_MAP) * TILE_SIZE
    screen = pygame.display.set_mode((win_w, win_h))
    pygame.display.set_caption("Raycasting Step 1: Angle & FPS Controls")
    clock = pygame.time.Clock()

    walls = []
    player_x = 0
    player_y = 0
    # プレイヤーの向き(角度:ラジアン) 最初は上(-π/2)を向く
    player_angle = -math.pi / 2

    for row, line in enumerate(MAZE_MAP):
        for col, char in enumerate(line):
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            if char == "1":
                walls.append((x, y, TILE_SIZE, TILE_SIZE))
            elif char == "P":
                player_x = x + TILE_SIZE // 2
                player_y = y + TILE_SIZE // 2

    speed = 2
    rot_speed = 0.05

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        # FPS視点の操作(左右で首振り、上下で前進・後退)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_angle -= rot_speed
        if keys[pygame.K_RIGHT]:
            player_angle += rot_speed

        # 前進・後退(壁の中に入らないようにチェック)
        new_x = player_x
        new_y = player_y
        if keys[pygame.K_UP]:
            new_x += math.cos(player_angle) * speed
            new_y += math.sin(player_angle) * speed
        if keys[pygame.K_DOWN]:
            new_x -= math.cos(player_angle) * speed
            new_y -= math.sin(player_angle) * speed

        # 壁でなければ移動を許可
        if not is_wall(new_x, new_y):
            player_x, player_y = new_x, new_y

        # 画面クリア
        screen.fill((0, 0, 0))

        # 迷路を描画
        for wx, wy, ww, wh in walls:
            draw_rect(screen, wx, wy, ww, wh, (0, 0, 200))

        # 光線を1本飛ばす
        hit_x, hit_y, depth = cast_single_ray(player_x, player_y, player_angle)

        # プレイヤーから壁の衝突地点まで赤いレーザー光線を引く
        draw_line(screen, player_x, player_y, hit_x, hit_y, (255, 0, 0))

        # 衝突視点に小さな白い点をうつ
        draw_circle(screen, int(hit_x), int(hit_y), 2, (255, 255, 255))

        # プレイヤー自身(黄色の丸)を描画
        draw_circle(screen, int(player_x), int(player_y), 4, (255, 255, 0))

        # プレイヤーの「視線(光線)」を赤い線で描画
        line_len = 30
        line_end_x = player_x + math.cos(player_angle) * line_len
        line_end_y = player_y + math.sin(player_angle) * line_len
        draw_line(screen, player_x, player_y, line_end_x, line_end_y, (255, 0, 0))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
