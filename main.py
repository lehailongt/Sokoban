import sys

import pygame

from constants import *
from IDA_star import IDAStarSolver
from sokoban_game import SokobanGame
from ultils import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sokoban - Game xếp thùng với IDA*")

# Font
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Biến toàn cục
clock = pygame.time.Clock()
level_number = 0
algorithm = "IDA* Algorithm"

# Load hình ảnh
images = {
    "wall": load_image("wall.png", COLORS["wall"]),
    "floor": load_image("floor.png", COLORS["floor"]),
    "player": load_image("player.png", COLORS["player"]),
    "player_on_goal": load_image("player_on_goal.png", COLORS["player_on_goal"]),
    "box": load_image("box.png", COLORS["box"]),
    "box_on_goal": load_image("box_on_goal.png", COLORS["box_on_goal"]),
    "goal": load_image("goal.png", COLORS["goal"]),
    "background": load_image("background.jpg", COLORS["background"]),
    "other": load_image("", COLORS["other"]),
}


def update_screen():
    pygame.display.flip()
    clock.tick(60)


def wait_time():
    """Chờ mà không làm đơ game"""
    start = pygame.time.get_ticks()
    # Sửa lỗi đơ game: Dùng vòng lặp kiểm tra sự kiện liên tục để game không bị treo khi chờ
    while pygame.time.get_ticks() - start < STEP_TIME:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.time.delay(10)


def draw_map(board):
    board_width = len(board[0]) * CELL_SIZE
    board_height = len(board) * CELL_SIZE
    offset_x = (WIDTH - board_width) // 2
    offset_y = (HEIGHT - board_height) // 2

    # Xóa map cũ (FUll khối cả chiều dài witdh)
    rect = pygame.Rect(0, offset_y, WIDTH, board_height)
    pygame.draw.rect(screen, BLACK, rect)

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            x = offset_x + j * CELL_SIZE
            y = offset_y + i * CELL_SIZE
            # Vẽ ô tương ứng với ký tự trên board.
            # Lưu ý: `BOX` và `BOX_ON_GOAL` là hai ký tự khác nhau.
            if cell == WALL:
                screen.blit(images["wall"], (x, y))
            elif cell == FLOOR:
                screen.blit(images["floor"], (x, y))
            elif cell == BOX:
                screen.blit(images["box"], (x, y))
            elif cell == BOX_ON_GOAL:
                screen.blit(images["box_on_goal"], (x, y))
            elif cell == PLAYER:
                screen.blit(images["player"], (x, y))
            elif cell == PLAYER_ON_GOAL:
                screen.blit(images["player_on_goal"], (x, y))
            elif cell == GOAL:
                screen.blit(images["goal"], (x, y))
            else:
                screen.blit(images["other"], (x, y))
    update_screen()


def draw_no_solution():
    # Hiển thị thông báo khi solver báo không có lời giải.
    draw_text("NO SOLUTION", HEIGHT - 200, YELLOW, BLACK)
    # Thêm dòng chữ hướng dẫn người chơi bấm phím để tiếp tục
    draw_text("Press ANY KEY to continue", HEIGHT - 160, WHITE, BLACK)


def draw_init_screen():
    """Vẽ màn hình ban đầu chạy chương trình"""
    # Vẽ backgroud
    screen.fill(BLACK)

    # Vẽ title
    title = font.render("SOKOBAN GAME", True, GRAY)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    # Vẽ map hiện thị
    board = parse_level(level_number)
    draw_map(board)

    # Vẽ level
    draw_text(f"Level {level_number + 1} / {len(LEVELS)}", HEIGHT - 120, WHITE, BLACK)

    # Vẽ thông tin algorithm
    algorithm_text = font.render(f"Algorithm: {algorithm}", True, WHITE)
    screen.blit(
        algorithm_text, (WIDTH // 2 - algorithm_text.get_width() // 2, HEIGHT - 80)
    )

    # Hướng dẫn
    help_text = small_font.render(
        "LEFT/RIGHT: Change Level | ENTER: Start | R: Reset | Q: Quit | P: Play",
        True,
        WHITE,
    )
    screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, HEIGHT - 40))
    update_screen()


def draw_loading_screen():
    """Vẽ màn hình loading"""
    loading_text = font.render("LOADING...", True, (255, 255, 0))
    screen.blit(loading_text, (WIDTH // 2 - loading_text.get_width() // 2, HEIGHT // 2))

    solving_text = small_font.render(
        "Solving with IDA* algorithm...", True, (200, 200, 200)
    )
    screen.blit(
        solving_text, (WIDTH // 2 - solving_text.get_width() // 2, HEIGHT // 2 + 40)
    )
    update_screen()


def draw_text(content, y, color_text, background):
    text = font.render(content, True, color_text)
    text_x = (WIDTH - text.get_width()) // 2
    text_y = y
    text_width = text.get_width()
    text_height = text.get_height()
    rect = (text_x, text_y, text_width, text_height)
    # Tạo màu background
    pygame.draw.rect(screen, background, rect)
    # Vẽ thông tin nội dung hiện thị
    screen.blit(text, rect)
    update_screen()


def draw_player_win(step_count):
    draw_text(f"Player is winner....", HEIGHT - 200, WHITE, BLACK)
    draw_text(f"STEP COUNT: {step_count}", HEIGHT - 170, WHITE, BLACK)
    # Thêm dòng chữ hướng dẫn người chơi thoát game khi thắng
    draw_text("Press ANY KEY to exit", HEIGHT - 140, WHITE, BLACK)


def draw_solution(solution):
    # Sửa lỗi: Đổi PUSH COUNT thành STEP COUNT do danh sách solution giờ đã chứa cả bước đi bộ
    step_count = len(solution) - 1
    for board in solution:
        draw_map(board)
        # Sửa lỗi đè text: Chuyển lệnh in text vào trong vòng lặp để vẽ lại sau mỗi lần map bị xóa đi vẽ lại
        draw_text(f"STEP COUNT: {step_count}", 20, WHITE, BLACK)
        wait_time()
    # Thêm hướng dẫn bấm phím khi đã vẽ xong kết quả
    draw_text("Press ANY KEY to continue", HEIGHT - 50, WHITE, BLACK)


def update_level_number(new_level_number):
    global level_number
    level_number = new_level_number
    draw_text(f"Level {level_number + 1} / {len(LEVELS)}", HEIGHT - 120, WHITE, BLACK)
    draw_map(parse_level(level_number))


def main():

    global level_number, algorithm
    running = True
    draw_init_screen()
    print("draw_init_screen")

    while running:
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if level_number < len(LEVELS) - 1:
                        update_level_number(level_number + 1)
                elif event.key == pygame.K_LEFT:
                    if level_number > 0:
                        update_level_number(level_number - 1)
                elif event.key == pygame.K_r:  # R
                    level_number = 0
                    draw_init_screen()
                elif event.key == pygame.K_q:  # q
                    running = False
                elif event.key == pygame.K_p:  # P
                    pygame.event.clear()

                    draw_text("Can You Win???", 70, WHITE, BLACK)
                    draw_text(f"Press E to exit game", 100, WHITE, BLACK)

                    board = parse_level(level_number)
                    draw_map(board)
                    game = SokobanGame(board)
                    playing = True
                    while playing:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_RIGHT:
                                    game.move("right")
                                elif event.key == pygame.K_LEFT:
                                    game.move("left")
                                elif event.key == pygame.K_UP:
                                    game.move("up")
                                elif event.key == pygame.K_DOWN:
                                    game.move("down")
                                elif event.key == pygame.K_e:
                                    playing = False
                                draw_map(game.board)
                            if game.check_win():
                                draw_player_win(game.step_count)
                                # Sửa lỗi kẹt vòng lặp: Đợi người dùng nhấn phím để thoát màn hình Win thay vì lặp vô hạn
                                waiting = True
                                pygame.event.clear()
                                while waiting:
                                    for ev in pygame.event.get():
                                        if ev.type == pygame.QUIT:
                                            pygame.quit()
                                            sys.exit()
                                        elif ev.type == pygame.KEYDOWN:
                                            waiting = False
                                            playing = False
                                    pygame.time.delay(50)
                                break
                    draw_init_screen()

                elif event.key == pygame.K_RETURN:  # Enter
                    draw_loading_screen()

                    board = parse_level(level_number)
                    solver = IDAStarSolver(board)
                    solver.solve()
                    if solver.end_node == None:
                        draw_no_solution()
                        # Sửa lỗi trôi phím: Xóa các event cũ và đợi sự kiện bấm phím MỚI xuất hiện
                        pygame.event.clear()
                        waiting = True
                        while waiting:
                            for ev in pygame.event.get():
                                if ev.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                elif ev.type == pygame.KEYDOWN:
                                    waiting = False
                            pygame.time.delay(50)
                        draw_init_screen()
                        continue

                    solution = solver.get_solution()
                    draw_solution(solution)
                    
                    # Sửa lỗi trôi phím: Xóa các event cũ (như phím Enter giữ quá lâu) và đợi sự kiện mới
                    pygame.event.clear()
                    waiting = True
                    while waiting:
                        for ev in pygame.event.get():
                            if ev.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif ev.type == pygame.KEYDOWN:
                                waiting = False
                        pygame.time.delay(50)
                    draw_init_screen()

        update_screen()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
