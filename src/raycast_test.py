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
def cast_ray(ox, oy, angle):
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

    # 左に2Dマップ(400幅),右に3Dビュー(400幅) = 合計 800幅
    map_w = len(MAZE_MAP[0]) * TILE_SIZE
    map_h = len(MAZE_MAP) * TILE_SIZE
    view_3d_w = 400
    screen_w = map_w + view_3d_w
    screen_h = map_h

    screen = pygame.display.set_mode((screen_w, screen_h))
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

    # 3Dビューの設定
    FOV = math.pi / 3 # 視野角 60度
    NUM_RAYS = 100    # 飛ばす光線の数 (100本の縦線で3D画面を作る)
    HALF_FOV = FOV / 2

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

        #---------------------------------
        # ①左画面: 2Dマップの描画
        #---------------------------------
        for wx, wy, ww, wh in walls:
            draw_rect(screen, wx, wy, ww, wh, (0, 0, 200))

        #---------------------------------
        # ②右画面: 3D世界の背景(天井と床)
        #---------------------------------
        # 天井(薄いグレー)
        draw_rect(screen, map_w, 0, view_3d_w, screen_h // 2, (40, 40, 40))
        # 床(少し明るいグレー)
        draw_rect(screen, map_w, screen_h // 2, view_3d_w, screen_h // 2, (70, 70, 70))

        #---------------------------------
        # ③レイとキャスティング(3D描画の心臓部)
        #---------------------------------
        # 視野の「左端の角度」から「右端の角度」まで計算
        start_angle = player_angle - HALF_FOV
        # 1本の光線あたりの角度の刻み幅
        delta_angle = FOV / NUM_RAYS
        # 1本の縦線の幅(400ピクセル幅 / 100本 = 1本あたり4ピクセル幅)
        strip_width = view_3d_w // NUM_RAYS

        for i in range(NUM_RAYS):
            # i本目の光線の角度
            ray_angle = start_angle + i * delta_angle
            hit_x, hit_y, depth = cast_ray(player_x, player_y, ray_angle)

            # 左の2Dマップに光線を描く(薄い黄色)
            draw_line(screen, player_x, player_y, hit_x, hit_y, (80, 80, 0))

            # 3Dの壁の高さを計算(反比例の公式)
            # 距離が0のときのゼロ除算を防ぐためにmax(depth, 0.0001)
            wall_height = int((TILE_SIZE * 250) / max(depth, 0.0001))

            # 壁の描画位置(画面の中央揃え)
            wall_top = (screen_h // 2) - (wall_height // 2)
            wall_bottom = (screen_h // 2) + (wall_height // 2)

            # 画面内に収まるようにクリッピングする
            # 画面の上端(0)より上にはみ出たら0でカット
            draw_start_y = max(0, wall_top)
            # 画面の下端(screen_h)より下にはみ出たらscreen_hでカット
            draw_end_y = min(screen_h, wall_bottom)

            # 実際に画面に描く高さ(絶対にscreen_h以下になる)
            actual_height = draw_end_y - draw_start_y

            #右画面のX座標
            screen_x = map_w + i * strip_width

            # 右の3D画面に壁の「柱(縦線)」を描画
            draw_rect(screen, screen_x, draw_start_y, strip_width, actual_height, (0, 0, 255))


        # # 光線を1本飛ばす
        # hit_x, hit_y, depth = cast_single_ray(player_x, player_y, player_angle)

        # # プレイヤーから壁の衝突地点まで赤いレーザー光線を引く
        # draw_line(screen, player_x, player_y, hit_x, hit_y, (255, 0, 0))
        #
        # # 衝突視点に小さな白い点をうつ
        # draw_circle(screen, int(hit_x), int(hit_y), 2, (255, 255, 255))

        # プレイヤー自身(黄色の丸)を描画
        draw_circle(screen, int(player_x), int(player_y), 4, (255, 255, 0))

        # # プレイヤーの「視線(光線)」を赤い線で描画
        # line_len = 30
        # line_end_x = player_x + math.cos(player_angle) * line_len
        # line_end_y = player_y + math.sin(player_angle) * line_len
        # draw_line(screen, player_x, player_y, line_end_x, line_end_y, (255, 0, 0))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
